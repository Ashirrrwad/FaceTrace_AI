<div align="center">

# 🕵️ FaceTrace AI

### AI-Powered Forensic Suspect Sketch Generator

*Generate police-style composite sketches from verbal witness descriptions using state-of-the-art AI image models.*

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Stability AI](https://img.shields.io/badge/Stability_AI-SDXL-6E3FF3?style=for-the-badge)](https://stability.ai)
[![Hugging Face](https://img.shields.io/badge/Hugging_Face-Inference_API-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co)

</div>

---

## 📖 Overview

**FaceTrace AI** is a forensic intelligence web application that transforms natural-language witness descriptions into realistic police composite sketches. Built for law enforcement simulations and creative projects, it combines LLM-powered prompt refinement with AI image generation to produce authentic graphite-pencil-style suspect portraits.

The system features a dual-API generation pipeline (Stability AI → Hugging Face fallback), an offline similarity-matching mode, and a pre-loaded criminal database for face comparison.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎨 **AI Sketch Generation** | Generates 3 unique sketch variations per case using Stability AI SDXL or HuggingFace models |
| 🧠 **LLM Prompt Refinement** | Uses a Hugging Face LLM to convert raw descriptions into optimised forensic prompts |
| 🗂️ **Criminal Database** | Pre-loaded with 6 suspects, including sketches, case details, and status |
| 🔍 **Face Matching / Compare** | Compares a new description against the database to find the top 3 closest suspects |
| 📁 **Case History** | Persistent session-based case history shown in the sidebar |
| 🛰️ **Offline Simulation Mode** | Falls back gracefully when APIs are unavailable — returns best-match from existing sketches |
| 🌑 **Cyberpunk UI** | Sleek dark forensic interface with glitch effects, scanlines, and glassmorphism |

---

## 🖥️ Screenshots

> The interface features a glitch-title header, a 3-panel trait selector, real-time generation progress, and a case file viewer with sketch/photo comparison.

---

## 🚀 Getting Started

### Prerequisites

- Python **3.9+**
- A [Hugging Face](https://huggingface.co/settings/tokens) account (free) — for image generation & LLM prompt refinement
- A [Stability AI](https://platform.stability.ai/) API key (optional but recommended) — for higher-quality SDXL output

### 1. Clone the Repository

```bash
git clone https://github.com/Ashirrrwad/FaceTrace_AI.git
cd FaceTrace_AI
```

### 2. Set Up a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

```env
HF_TOKEN=your_huggingface_token_here
STABILITY_API_KEY=your_stability_ai_key_here
```

> **Note:** The app works without `STABILITY_API_KEY` — it will automatically fall back to Hugging Face for generation.

### 5. Run the App

```bash
python app.py
```

Open [http://localhost:5001](http://localhost:5001) in your browser.

---

## 🧠 How It Works

```
Witness Description
        │
        ▼
┌───────────────────┐
│  LLM Prompt       │  HuggingFace Mistral/Zephyr refines the raw text
│  Refinement       │  into structured forensic image generation prompt
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Image Generation │  Tries Stability AI SDXL first (3 variations)
│  Pipeline         │  Falls back to HuggingFace if unavailable
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Sketch Saved     │  PNG saved to static/images/cases/
│  to Disk          │  Entry persisted to database.json
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Face Comparison  │  Description matched against criminal DB
│  (/compare)       │  Returns top 3 similarity-scored suspects
└───────────────────┘
```

---

## 📁 Project Structure

```
FaceTrace_AI/
├── app.py                       # Flask backend, API routes, generation logic
├── database.json                # Suspect criminal database (suspects + generated cases)
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variable template
├── README.md
│
├── templates/
│   └── index.html               # Single-page app (Jinja2 template)
│
└── static/
    ├── favicon.svg
    ├── css/
    │   └── style.css            # Cyberpunk dark theme with animations
    ├── js/
    │   └── main.js              # Frontend logic (generation, comparison, UI)
    └── images/
        └── cases/               # Suspect mugshots + AI-generated sketches
```

---

## 🔌 API Reference

### `POST /generate`

Generate a forensic sketch from a description.

**Request Body:**
```json
{
  "case_id": "CRM-0042",
  "description": "Male, late 40s, deep-set eyes, thin lips, receding hairline, scar on left cheek",
  "traits": {
    "age": "40",
    "gender": "male",
    "style": "pencil sketch"
  }
}
```

**Response:**
```json
{
  "success": true,
  "primary_url": "/static/images/cases/crm_0042_primary.png",
  "var1_url": "/static/images/cases/crm_0042_var1.png",
  "var2_url": "/static/images/cases/crm_0042_var2.png",
  "report": "...",
  "confidence": 87,
  "is_simulated": false
}
```

---

### `POST /compare`

Compare a description against the criminal database.

**Request Body:**
```json
{
  "description": "Female, 30s, tattooed arms, green eyes, ponytail"
}
```

**Response:**
```json
{
  "matches": [
    { "id": "CRM-6112", "name": "Sarah Miller", "similarity": 74, ... }
  ]
}
```

---

### `GET /cases`

Returns all suspects in the criminal database.

---

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `HF_TOKEN` | ✅ Yes | Hugging Face User Access Token (for LLM + image generation) |
| `STABILITY_API_KEY` | ⚪ Optional | Stability AI key for SDXL generation (higher quality) |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.9+, Flask |
| AI — Image Gen (Primary) | Stability AI SDXL 1.0 |
| AI — Image Gen (Fallback) | Hugging Face Inference API |
| AI — Prompt Refinement | Hugging Face LLM (Mistral/Zephyr) |
| Image Processing | Pillow |
| Frontend | Vanilla HTML, CSS, JavaScript |
| Fonts | Orbitron, Rajdhani, JetBrains Mono |

---

## ⚙️ Generation Modes

The app uses a **priority cascade** for image generation:

1. **Stability AI SDXL** — Primary. Highest quality. Produces 3 compositional variations per case.
2. **Hugging Face Inference API** — Secondary fallback. Uses 3 different seeds for variation.
3. **Offline Simulation** — Final fallback. Returns the closest-matching pre-existing sketch from the database using trait similarity scoring. No API call required.

---

## 📄 License

MIT License — free to use, modify, and distribute with attribution.

---

<div align="center">
Built with ⚡ by <a href="https://github.com/Ashirrrwad">Ashirrrwad</a>
</div>
