# app.py - Beat-Aligned Audio Mixer (v2.0)
# GitHub: https://github.com/yourusername/beat-aligned-mixer

import os
import gradio as gr
import numpy as np
import librosa
import soundfile as sf
import tempfile
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import signal

# ─────────────────────────────────────────────
# AUDIO LOADING
# ─────────────────────────────────────────────

SUPPORTED_FORMATS = [".wav", ".mp3", ".flac", ".ogg", ".aiff", ".aif", ".m4a"]

def load_audio(file_path, sr=44100):
    """Load audio file and resample to target sample rate."""
    if file_path is None:
        raise gr.Error("No file provided.")
    ext = os.path.splitext(file_path)[-1].lower()
    if ext not in SUPPORTED_FORMATS:
        raise gr.Error(f"Unsupported format '{ext}'. Supported: {', '.join(SUPPORTED_FORMATS)}")
    try:
        y, sr_orig = librosa.load(file_path, sr=sr, mono=True)
        if len(y) == 0:
            raise gr.Error("Audio file appears to be empty.")
        return y, sr
    except gr.Error:
        raise
    except Exception as e:
        raise gr.Error(f"Error loading audio: {str(e)}")

def get_duration(audio_array, sr):
    """Get duration of audio in seconds."""
    return len(audio_array) / sr

# ─────────────────────────────────────────────
# BEAT DETECTION (improved)
# ─────────────────────────────────────────────

def find_beats(audio, sr):
    """
    Improved beat detection using harmonic/percussive separation
    and multi-feature onset strength.
    """
    # Trim silence from edges to avoid false beat detection
    audio_trimmed, _ = librosa.effects.trim(audio, top_db=30)

    # Separate harmonic and percussive components
    y_harmonic, y_percussive = librosa.effects.hpss(audio_trimmed, margin=3.0)

    # Onset strength combining both components
    onset_env = librosa.onset.onset_strength(
        y=y_percussive,
        sr=sr,
        hop_length=512,
        aggregate=np.median
    )

    # Estimate tempo with prior
    tempo_estimate = librosa.feature.tempo(onset_envelope=onset_env, sr=sr, hop_length=512)
    tempo = float(np.median(tempo_estimate))

    # Beat tracking using dynamic programming
    _, beat_frames = librosa.beat.beat_track(
        onset_envelope=onset_env,
        sr=sr,
        hop_length=512,
        bpm=tempo,
        tightness=100,
        trim=True
    )

    beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=512)

    # Filter out beats that are unrealistically close together (< 0.2s)
    if len(beat_times) > 1:
        diffs = np.diff(beat_times)
        keep = np.concatenate(([True], diffs > 0.2))
        beat_times = beat_times[keep]

    return beat_times, tempo

def calculate_beat_match_offset(base_beats, inst_beats):
    """Find the offset that best aligns the instrument beats with base beats."""
    if len(base_beats) < 2 or len(inst_beats) < 2:
        return 0.0

    base_intervals = np.diff(base_beats)
    inst_intervals = np.diff(inst_beats)

    base_median_interval = np.median(base_intervals)
    inst_median_interval = np.median(inst_intervals)

    tempo_ratio = base_median_interval / inst_median_interval

    if tempo_ratio < 0.8 or tempo_ratio > 1.25:
        return base_beats[0] - inst_beats[0]

    # Cross-correlation-based alignment for better accuracy
    # Build score arrays over a common time grid
    duration = max(base_beats[-1], inst_beats[-1]) + 2.0
    resolution = 0.01  # 10ms grid
    time_grid = np.arange(0, duration, resolution)

    def beats_to_signal(beats, grid):
        sig = np.zeros(len(grid))
        for b in beats:
            idx = int(round(b / resolution))
            if 0 <= idx < len(sig):
                sig[idx] = 1.0
        return sig

    base_sig = beats_to_signal(base_beats, time_grid)
    inst_sig = beats_to_signal(inst_beats, time_grid)

    # Smooth slightly for robustness
    from scipy.ndimage import gaussian_filter1d
    base_sig = gaussian_filter1d(base_sig, sigma=2)
    inst_sig = gaussian_filter1d(inst_sig, sigma=2)

    # Cross-correlate
    corr = np.correlate(base_sig, inst_sig, mode="full")
    lag_idx = np.argmax(corr) - (len(inst_sig) - 1)
    offset = lag_idx * resolution

    return offset

# ─────────────────────────────────────────────
# TEMPO MATCHING
# ─────────────────────────────────────────────

def time_stretch_to_match_tempo(audio, sr, source_tempo, target_tempo):
    """Time-stretch audio to match target tempo."""
    if source_tempo <= 0 or target_tempo <= 0:
        return audio
    ratio = source_tempo / target_tempo
    if 0.97 < ratio < 1.03:
        return audio
    ratio = float(np.clip(ratio, 0.75, 1.33))
    try:
        return librosa.effects.time_stretch(audio, rate=ratio)
    except Exception:
        return audio

# ─────────────────────────────────────────────
# CROSSFADE
# ─────────────────────────────────────────────

def apply_crossfade(track, sr, fade_duration=2.0):
    """Apply fade-in and fade-out to a track."""
    fade_samples = int(fade_duration * sr)
    fade_samples = min(fade_samples, len(track) // 4)

    fade_in = np.linspace(0.0, 1.0, fade_samples)
    fade_out = np.linspace(1.0, 0.0, fade_samples)

    result = track.copy()
    result[:fade_samples] *= fade_in
    result[-fade_samples:] *= fade_out
    return result

# ─────────────────────────────────────────────
# MIXING ENGINE
# ─────────────────────────────────────────────

def mix_with_beat_alignment(
    track1_path, track2_path,
    track1_volume=1.0, track2_volume=1.0,
    manual_offset=0.0, match_tempo=True,
    crossfade=True, crossfade_duration=2.0,
    export_format="wav"
):
    """Mix tracks with beat alignment, optional tempo matching, and crossfade."""
    if not track1_path:
        raise gr.Error("Please upload a base track.")
    if not track2_path:
        raise gr.Error("Please upload an instrument track.")

    track1, sr = load_audio(track1_path)
    track2_orig, sr = load_audio(track2_path)

    try:
        track1_beats, track1_tempo = find_beats(track1, sr)
        track2_beats, track2_tempo = find_beats(track2_orig, sr)

        if match_tempo and abs(track1_tempo - track2_tempo) > 3.0:
            track2 = time_stretch_to_match_tempo(track2_orig, sr, track2_tempo, track1_tempo)
            track2_beats, track2_tempo = find_beats(track2, sr)
        else:
            track2 = track2_orig

        beat_offset = calculate_beat_match_offset(track1_beats, track2_beats)
        total_offset = beat_offset + float(manual_offset)

    except Exception as e:
        print(f"Beat detection failed: {str(e)}")
        track2 = track2_orig
        total_offset = float(manual_offset)

    # Apply crossfade envelopes
    if crossfade:
        track1 = apply_crossfade(track1, sr, crossfade_duration)
        track2 = apply_crossfade(track2, sr, crossfade_duration)

    # Convert offset to samples
    offset_samples = int(total_offset * sr)

    # Build output buffer
    max_output_length = max(len(track1), len(track2) + max(0, offset_samples))
    mixed = np.zeros(max_output_length)

    mixed[:len(track1)] += track1 * float(track1_volume)

    if offset_samples >= 0:
        end = min(max_output_length, offset_samples + len(track2))
        mixed[offset_samples:end] += track2[:end - offset_samples] * float(track2_volume)
    else:
        start = abs(offset_samples)
        if start < len(track2):
            chunk = track2[start:]
            mixed[:len(chunk)] += chunk * float(track2_volume)

    # Normalize
    peak = np.max(np.abs(mixed))
    if peak > 1.0:
        mixed = mixed / peak

    # Export
    export_format = export_format.lower()
    suffix = f".{export_format}"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        output_path = tmp.name

    if export_format == "mp3":
        # Write wav first, then convert with ffmpeg
        wav_path = output_path.replace(".mp3", "_tmp.wav")
        sf.write(wav_path, mixed, sr)
        ret = os.system(f'ffmpeg -y -i "{wav_path}" -q:a 2 "{output_path}" 2>/dev/null')
        os.remove(wav_path)
        if ret != 0:
            # Fallback to wav if ffmpeg not available
            output_path = output_path.replace(".mp3", ".wav")
            sf.write(output_path, mixed, sr)
    else:
        sf.write(output_path, mixed, sr)

    return output_path

# ─────────────────────────────────────────────
# VISUALIZATION
# ─────────────────────────────────────────────

COLORS = {
    "base": "#4A90D9",
    "inst": "#27AE60",
    "aligned": "#8E44AD",
    "beats_base": "#E74C3C",
    "beats_inst": "#F39C12",
}

def create_beat_visualization(track1_path, track2_path, manual_offset=0.0, match_tempo=True):
    """Create polished beat alignment visualization."""
    try:
        track1, sr = load_audio(track1_path)
        track2_orig, sr = load_audio(track2_path)

        track1_beats, track1_tempo = find_beats(track1, sr)
        track2_beats_orig, track2_tempo_orig = find_beats(track2_orig, sr)

        if match_tempo and abs(track1_tempo - track2_tempo_orig) > 3.0:
            track2 = time_stretch_to_match_tempo(track2_orig, sr, track2_tempo_orig, track1_tempo)
            track2_beats, track2_tempo = find_beats(track2, sr)
        else:
            track2 = track2_orig
            track2_beats = track2_beats_orig
            track2_tempo = track2_tempo_orig

        beat_offset = calculate_beat_match_offset(track1_beats, track2_beats)
        total_offset = beat_offset + float(manual_offset)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            plot_path = tmp.name

        window = min(30, len(track1) / sr)

        fig, axes = plt.subplots(3, 1, figsize=(14, 9), facecolor="#1A1A2E")
        plt.subplots_adjust(hspace=0.5)

        def style_ax(ax, title):
            ax.set_facecolor("#16213E")
            ax.set_title(title, color="white", fontsize=11, pad=8)
            ax.tick_params(colors="gray")
            for spine in ax.spines.values():
                spine.set_edgecolor("#333355")

        # Base track
        ax1 = axes[0]
        t1 = np.linspace(0, len(track1) / sr, len(track1))
        ax1.plot(t1, track1, color=COLORS["base"], alpha=0.6, linewidth=0.5)
        ax1.vlines(track1_beats, -0.9, 0.9, color=COLORS["beats_base"],
                   linewidth=1.0, alpha=0.85, label="Beats")
        ax1.set_xlim(0, window)
        ax1.set_ylim(-1, 1)
        style_ax(ax1, f"🎵 Base Track — {track1_tempo:.1f} BPM")
        ax1.legend(loc="upper right", fontsize=8, facecolor="#1A1A2E", labelcolor="white")

        # Original instrument track
        ax2 = axes[1]
        t2 = np.linspace(0, len(track2_orig) / sr, len(track2_orig))
        ax2.plot(t2, track2_orig, color=COLORS["inst"], alpha=0.6, linewidth=0.5)
        ax2.vlines(track2_beats_orig, -0.9, 0.9, color=COLORS["beats_inst"],
                   linewidth=1.0, alpha=0.85, label="Beats")
        ax2.set_xlim(0, window)
        ax2.set_ylim(-1, 1)
        style_ax(ax2, f"🎸 Instrument Track (Original) — {track2_tempo_orig:.1f} BPM")
        ax2.legend(loc="upper right", fontsize=8, facecolor="#1A1A2E", labelcolor="white")

        # Aligned instrument track overlaid with base beats
        ax3 = axes[2]
        t3 = np.linspace(0, len(track2) / sr, len(track2)) + total_offset
        ax3.plot(t3, track2, color=COLORS["aligned"], alpha=0.6, linewidth=0.5)
        ax3.vlines(track2_beats + total_offset, -0.9, 0.9, color=COLORS["beats_inst"],
                   linewidth=1.2, alpha=0.85, label="Aligned Beats")
        ax3.vlines(track1_beats, -0.9, 0.9, color=COLORS["beats_base"],
                   linewidth=0.8, linestyle="--", alpha=0.45, label="Base Beats")
        ax3.set_xlim(0, window)
        ax3.set_ylim(-1, 1)
        ax3.set_xlabel("Time (seconds)", color="gray", fontsize=9)
        style_ax(ax3, f"✅ Aligned — Offset: {total_offset:.2f}s")
        ax3.legend(loc="upper right", fontsize=8, facecolor="#1A1A2E", labelcolor="white")

        fig.suptitle("Beat Alignment Visualization", color="white", fontsize=14, y=0.98)
        plt.savefig(plot_path, dpi=150, bbox_inches="tight", facecolor="#1A1A2E")
        plt.close(fig)

        return plot_path, track1_tempo, track2_tempo_orig, beat_offset

    except Exception as e:
        print(f"Visualization error: {str(e)}")
        return None, 0.0, 0.0, 0.0

# ─────────────────────────────────────────────
# ANALYSIS WRAPPER
# ─────────────────────────────────────────────

def analyze_tracks(track1_path, track2_path, match_tempo):
    """Analyze tracks and return visualization + BPM info."""
    if not track1_path or not track2_path:
        return None, "Upload both tracks to see BPM info.", "—", "—"

    try:
        viz, t1_bpm, t2_bpm, offset = create_beat_visualization(
            track1_path, track2_path, 0.0, match_tempo
        )
        bpm_info = (
            f"### 🎚️ Analysis Results\n"
            f"| Track | BPM | Auto Offset |\n"
            f"|---|---|---|\n"
            f"| Base | **{t1_bpm:.1f}** | — |\n"
            f"| Instrument | **{t2_bpm:.1f}** | **{offset:.2f}s** |"
        )
        return viz, bpm_info, f"{t1_bpm:.1f}", f"{t2_bpm:.1f}"
    except Exception as e:
        return None, f"❌ Analysis error: {str(e)}", "—", "—"

# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────

CSS = """
#title { text-align: center; }
.gr-button-primary { background: linear-gradient(90deg, #4A90D9, #8E44AD) !important; border: none !important; }
.gr-button { border-radius: 8px !important; }
footer { display: none !important; }
"""

def create_ui():
    with gr.Blocks(title="Beat-Aligned Audio Mixer v2", css=CSS, theme=gr.themes.Soft()) as app:

        gr.Markdown("# 🎛️ Beat-Aligned Audio Mixer v2.0", elem_id="title")
        gr.Markdown(
            "Upload two audio tracks — the app auto-detects beats, matches tempo, "
            "and creates a perfectly aligned remix. Supports WAV, MP3, FLAC, OGG, AIFF, M4A.",
            elem_id="title"
        )

        # ── Track Upload ──────────────────────────────
        with gr.Row():
            with gr.Column():
                track1_input = gr.Audio(label="🎵 Base Track", type="filepath")
                track1_volume = gr.Slider(0.0, 2.0, value=1.0, step=0.05,
                                          label="Base Track Volume")
                base_bpm_display = gr.Textbox(label="Base BPM", value="—", interactive=False)

            with gr.Column():
                track2_input = gr.Audio(label="🎸 Instrument Track", type="filepath")
                track2_volume = gr.Slider(0.0, 2.0, value=1.0, step=0.05,
                                          label="Instrument Track Volume")
                inst_bpm_display = gr.Textbox(label="Instrument BPM", value="—", interactive=False)

        # ── Controls ──────────────────────────────────
        with gr.Row():
            match_tempo_cb = gr.Checkbox(label="⏱️ Match Tempo (time-stretch)", value=True)
            crossfade_cb   = gr.Checkbox(label="🎚️ Crossfade", value=True)
            crossfade_dur  = gr.Slider(0.5, 5.0, value=2.0, step=0.5,
                                       label="Crossfade Duration (s)")
            export_fmt     = gr.Radio(["wav", "mp3", "flac"], value="wav",
                                      label="📁 Export Format")

        with gr.Row():
            analyze_btn = gr.Button("🔍 Analyze & Align Beats", variant="primary", scale=2)
            mix_btn     = gr.Button("🎧 Mix Tracks", variant="primary", scale=2)

        # ── BPM Info ──────────────────────────────────
        bpm_info_md = gr.Markdown("")

        # ── Visualization ─────────────────────────────
        beat_viz = gr.Image(label="Beat Alignment Visualization")

        # ── Fine-tune ─────────────────────────────────
        fine_tune = gr.Slider(-5.0, 5.0, value=0.0, step=0.01,
                              label="🎯 Fine-tune Offset (seconds)",
                              info="Drag to manually nudge the instrument track forward/backward")

        # ── Output ────────────────────────────────────
        output_audio = gr.Audio(label="🎶 Mixed Output")

        # ── Events ────────────────────────────────────
        analyze_btn.click(
            fn=analyze_tracks,
            inputs=[track1_input, track2_input, match_tempo_cb],
            outputs=[beat_viz, bpm_info_md, base_bpm_display, inst_bpm_display]
        )

        mix_btn.click(
            fn=mix_with_beat_alignment,
            inputs=[
                track1_input, track2_input,
                track1_volume, track2_volume,
                fine_tune, match_tempo_cb,
                crossfade_cb, crossfade_dur,
                export_fmt
            ],
            outputs=output_audio
        )

        # ── Instructions ──────────────────────────────
        gr.Markdown("""
---
## 📖 How to Use

1. **Upload** your base track and instrument track (WAV, MP3, FLAC, OGG, AIFF, M4A supported)
2. **Enable "Match Tempo"** to auto time-stretch the instrument track to the base track BPM
3. Click **"Analyze & Align Beats"** — BPMs and auto-offset will appear in real time
4. Review the **beat visualization** — aligned beats should line up with the base track
5. Use the **Fine-tune Offset** slider to nudge alignment manually if needed
6. Toggle **Crossfade** to apply smooth fade-in/fade-out envelopes
7. Choose your **export format** (WAV, MP3, FLAC)
8. Click **"Mix Tracks"** and download the result

> 💡 **Tip:** Works best with tracks that have clear rhythmic content. Tracks with similar tempos (within ~25%) produce the best results.
        """)

    return app

# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

demo = create_ui()

if __name__ == "__main__":
    demo.launch()
