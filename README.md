# Beat-Aligned Audio Mixer v2.0

> Automatically align, tempo-match, and remix two audio tracks — with beat detection, crossfade, real-time BPM display, and multi-format export.
---

## Features

| Feature | Description |
|---|---|
| **Beat Detection** | Improved harmonic/percussive separation + cross-correlation alignment |
| **Tempo Matching** | Auto time-stretch instrument track to match base track BPM |
| **Real-time BPM Display** | See BPM of each track instantly after analysis |
| **Crossfade** | Smooth fade-in/fade-out envelopes with adjustable duration |
| **Fine-tune Offset** | Manual slider to nudge alignment with millisecond precision |
| **Volume Control** | Independent volume sliders for each track |
| **Multi-format Export** | Export as **WAV**, **MP3**, or **FLAC** |
| **Multi-format Input** | Supports WAV, MP3, FLAC, OGG, AIFF, M4A |
| **Beat Visualization** | Dark-themed 3-panel waveform + beat marker plot |

---

---

## How to Use

1. **Upload** your base track and instrument track (any supported format)
2. **Enable "Match Tempo"** to auto time-stretch the instrument track to the base BPM
3. Click **"Analyze & Align Beats"** — BPMs appear in real time, the visualization loads
4. Review the **beat visualization** — aligned beats should line up with base beats
5. Use the **Fine-tune Offset** slider to nudge alignment if needed
6. Toggle **Crossfade** and set fade duration for smooth transitions
7. Choose **export format** (WAV / MP3 / FLAC)
8. Click **"Mix Tracks"** and download the result

> **Best results:** Use tracks with clear rhythmic content and similar tempos (within ~25%).


## Tech Stack

- [Gradio](https://gradio.app) — Web UI
- [librosa](https://librosa.org) — Beat detection, tempo analysis, time-stretching
- [SoundFile](https://python-soundfile.readthedocs.io) — Audio I/O
- [NumPy](https://numpy.org) / [SciPy](https://scipy.org) — Signal processing
- [Matplotlib](https://matplotlib.org) — Beat visualization
- [FFmpeg](https://ffmpeg.org) — MP3 encoding (system dependency)

---


Licensed under the [Apache 2.0 License](LICENSE).

---
