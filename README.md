# 🎛️ Beat-Aligned Audio Mixer v2.0

> Automatically align, tempo-match, and remix two audio tracks — with beat detection, crossfade, real-time BPM display, and multi-format export.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://python.org)
[![Gradio](https://img.shields.io/badge/Gradio-4.0%2B-orange?logo=gradio)](https://gradio.app)
[![License](https://img.shields.io/badge/License-Apache%202.0-green)](LICENSE)
[![HuggingFace](https://img.shields.io/badge/🤗%20HuggingFace-Space-yellow)](https://huggingface.co/spaces)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🥁 **Beat Detection** | Improved harmonic/percussive separation + cross-correlation alignment |
| ⏱️ **Tempo Matching** | Auto time-stretch instrument track to match base track BPM |
| 📊 **Real-time BPM Display** | See BPM of each track instantly after analysis |
| 🎚️ **Crossfade** | Smooth fade-in/fade-out envelopes with adjustable duration |
| 🎯 **Fine-tune Offset** | Manual slider to nudge alignment with millisecond precision |
| 🎛️ **Volume Control** | Independent volume sliders for each track |
| 📁 **Multi-format Export** | Export as **WAV**, **MP3**, or **FLAC** |
| 🎵 **Multi-format Input** | Supports WAV, MP3, FLAC, OGG, AIFF, M4A |
| 📈 **Beat Visualization** | Dark-themed 3-panel waveform + beat marker plot |

---

## 🖼️ Screenshot

![Beat Alignment Visualization](docs/screenshot.png)
*(Add your own screenshot here)*

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/beat-aligned-mixer.git
cd beat-aligned-mixer
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install FFmpeg (for MP3 export)

| Platform | Command |
|---|---|
| Ubuntu/Debian | `sudo apt install ffmpeg` |
| macOS | `brew install ffmpeg` |
| Windows | [Download from ffmpeg.org](https://ffmpeg.org/download.html) |

> FFmpeg is only required for MP3 export. WAV and FLAC export work without it.

### 5. Run the app

```bash
python app.py
```

Open your browser at **http://localhost:7860**

---

## 🎧 How to Use

1. **Upload** your base track and instrument track (any supported format)
2. **Enable "Match Tempo"** to auto time-stretch the instrument track to the base BPM
3. Click **"Analyze & Align Beats"** — BPMs appear in real time, the visualization loads
4. Review the **beat visualization** — aligned beats should line up with base beats
5. Use the **Fine-tune Offset** slider to nudge alignment if needed
6. Toggle **Crossfade** and set fade duration for smooth transitions
7. Choose **export format** (WAV / MP3 / FLAC)
8. Click **"Mix Tracks"** and download the result

> 💡 **Best results:** Use tracks with clear rhythmic content and similar tempos (within ~25%).

---

## 🗂️ Project Structure

```
beat-aligned-mixer/
├── app.py              # Main application (UI + audio engine)
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── LICENSE             # Apache 2.0
├── .gitignore          # Git ignore rules
├── .gitattributes      # Git attributes
└── docs/
    └── screenshot.png  # (Add your screenshot here)
```

---

## 🔧 Configuration & Tips

- **Tempo range:** The app handles tempo ratios up to ~1.33× (e.g. 90 BPM ↔ 120 BPM)
- **Crossfade duration:** 1–3 seconds works best for most music; higher values for ambient/slow tracks
- **Manual offset:** Use negative values to move the instrument track earlier, positive to delay it
- **Sample rate:** Everything is processed at 44100 Hz internally

---

## 🛠️ Tech Stack

- [Gradio](https://gradio.app) — Web UI
- [librosa](https://librosa.org) — Beat detection, tempo analysis, time-stretching
- [SoundFile](https://python-soundfile.readthedocs.io) — Audio I/O
- [NumPy](https://numpy.org) / [SciPy](https://scipy.org) — Signal processing
- [Matplotlib](https://matplotlib.org) — Beat visualization
- [FFmpeg](https://ffmpeg.org) — MP3 encoding (system dependency)

---

## 🤗 Deploy on Hugging Face Spaces

This app is compatible with Hugging Face Spaces (Gradio SDK).

1. Create a new Space on [huggingface.co/spaces](https://huggingface.co/spaces)
2. Set SDK to **Gradio**
3. Push this repo:

```bash
git remote add hf https://huggingface.co/spaces/yourusername/beat-aligned-mixer
git push hf main
```

> Note: FFmpeg is available by default on HF Spaces, so MP3 export works out of the box.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

1. Fork the repo
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

Licensed under the [Apache 2.0 License](LICENSE).

---

## 🙏 Acknowledgements

- Beat detection powered by [librosa](https://librosa.org)
- UI built with [Gradio](https://gradio.app)
- Originally built and hosted on [Hugging Face Spaces](https://huggingface.co/spaces)
