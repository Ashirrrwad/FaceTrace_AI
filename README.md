# 🕵️ FaceTrace AI — Suspect Sketch Generator

> An AI-powered forensic suspect sketch system that generates police-style composite sketches from text descriptions using Hugging Face Inference API and Stability AI.

---

## ✨ Features

- 🎨 **AI Sketch Generation** — Generate realistic police composite sketches from verbal descriptions
- 🗂️ **Criminal Database** — Browse a pre-loaded database of suspects with sketches & case files
- 🔍 **Face Matching** — Compare generated sketches against database suspects
- 📋 **Case Management** — View full suspect profiles with offense details and status
- 🌑 **Dark UI** — Sleek cyberpunk-inspired forensic interface

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- A [Hugging Face](https://huggingface.co) account with an API token
- A [Stability AI](https://stability.ai) API key

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/face-trace-ai.git
cd face-trace-ai

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your actual API keys
```

### Running Locally

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## 📁 Project Structure

```
face-trace-ai/
├── app.py                  # Flask backend & API routes
├── database.json           # Suspect criminal database
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── templates/
│   └── index.html          # Main HTML template
└── static/
    ├── css/style.css       # Stylesheet
    ├── js/main.js          # Frontend JavaScript
    ├── favicon.svg         # App icon
    └── images/cases/       # Suspect photos & AI-generated sketches
```

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `HF_TOKEN` | Hugging Face API token for inference |
| `STABILITY_API_KEY` | Stability AI API key for image generation |

---

## 🛠️ Tech Stack

- **Backend**: Python / Flask
- **AI Models**: Hugging Face Inference API, Stability AI SDXL
- **Image Processing**: Pillow
- **Frontend**: Vanilla HTML, CSS, JavaScript

---

## 📄 License

MIT License — feel free to use, modify, and distribute.
