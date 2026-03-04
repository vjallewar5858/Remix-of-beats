# Changelog

All notable changes to Beat-Aligned Audio Mixer are documented here.

---

## [2.0.0] — 2024

### 🆕 Added
- **Real-time BPM display** — Base and instrument BPM shown instantly after analysis
- **Crossfade support** — Smooth fade-in/fade-out envelopes with adjustable duration (0.5–5s)
- **MP3 export** — Export mixed output as MP3 via FFmpeg (in addition to WAV and FLAC)
- **FLAC export** — Lossless export option
- **Multi-format input** — Now supports WAV, MP3, FLAC, OGG, AIFF, M4A input files
- **Dark-themed beat visualization** — Polished 3-panel waveform plot with colour-coded beat markers
- **BPM info table** — Markdown table in UI showing both BPMs and auto-detected offset

### 🐛 Fixed
- Beat detection now uses cross-correlation alignment for more accurate offset calculation
- Harmonic/percussive separation uses `margin=3.0` for cleaner percussive signal
- Silence trimming before beat analysis avoids false detections at track edges
- Beat frames with unrealistically short gaps (< 0.2s) are now filtered out
- `matplotlib` backend explicitly set to `Agg` to prevent GUI thread conflicts
- Graceful fallback to WAV if FFmpeg is not installed (MP3 export)
- Fixed edge case where instrument track could overflow output buffer

### ♻️ Changed
- Upgraded to Gradio 4.x API (removed deprecated `gr.Slider` component update pattern)
- Refactored `analyze_tracks` to return clean tuple — no more lambda hacks in `.click()`
- Separated audio loading, beat detection, tempo matching, crossfade, mixing into clearly labelled sections
- Volume sliders now go from 0.0 to 2.0 (was 0–2.0 with inconsistent typing)
- Code cleanup: type hints, docstrings, named constants for plot colours

---

## [1.0.0] — Initial Release (Hugging Face)

- Basic beat detection using librosa
- Tempo matching via time-stretch
- Manual offset slider
- WAV export only
- Beat alignment visualization
