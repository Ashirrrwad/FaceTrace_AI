<div align="center">

# 🕵️ FaceTrace AI

### AI-Powered Forensic Suspect Sketch Generator

Generate realistic forensic composite sketches from witness descriptions using Large Language Models (LLMs) and AI image generation.

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![Stability AI](https://img.shields.io/badge/Stability_AI-SDXL-6E3FF3?style=for-the-badge)
![Hugging Face](https://img.shields.io/badge/Hugging_Face-Inference_API-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</div>

---

# 📖 Overview

FaceTrace AI is an AI-powered forensic investigation system that transforms natural language witness descriptions into realistic police-style suspect sketches.

Instead of relying entirely on manual forensic artists, investigators can provide descriptive details about a suspect, and the application automatically generates multiple forensic sketch variations using state-of-the-art AI image generation models.

To improve reliability, FaceTrace AI includes:

- 🧠 LLM-powered prompt refinement
- 🎨 AI sketch generation
- 🔍 Criminal database comparison
- 📂 Case history management
- 🌐 Multi-model fallback architecture
- ⚡ Offline simulation mode

The project demonstrates how modern AI can assist forensic investigations, criminal identification, educational simulations, and research.

---

# ✨ Features

## 🎨 AI Sketch Generation

Generate multiple forensic sketch variations directly from witness descriptions.

- Generates three sketch variations
- High-quality SDXL generation
- Pencil-sketch optimized prompts

---

## 🧠 Intelligent Prompt Refinement

Uses a Large Language Model (LLM) to convert raw witness descriptions into structured prompts optimized for AI image generation.

---

## 🔍 Criminal Database Matching

Compare newly generated suspects with stored criminal records using similarity scoring.

Returns:

- Top 3 matching suspects
- Similarity percentage
- Criminal profile
- Case information

---

## 📂 Case History

Automatically stores generated investigations with:

- Case ID
- Witness description
- Generated sketches
- Investigation report

---

## 🌐 Multi-Engine AI Pipeline

Supports multiple AI providers for maximum reliability.

Priority order:

1. Stability AI SDXL
2. Hugging Face Inference API
3. Offline Simulation Mode

---

## 🌑 Modern Cyberpunk Interface

Dark-themed forensic dashboard featuring:

- Glassmorphism UI
- Glitch animations
- Scanline effects
- Responsive layout

---

# 🎥 Demo

> Replace the following with your demo GIF after deployment.

```
Witness Description
        │
        ▼
Generate Sketch
        │
        ▼
View AI Results
        │
        ▼
Compare Criminal Database
        │
        ▼
Investigation Report
```

---

# 🖼 Screenshots

Add screenshots after completing the project.

| Dashboard | Sketch Generation |
|-----------|-------------------|
| Screenshot | Screenshot |

| Criminal Match | Case History |
|----------------|--------------|
| Screenshot | Screenshot |

---

# 🏗 System Architecture

```
                 Witness Description
                         │
                         ▼
              Prompt Refinement (LLM)
                         │
                         ▼
           Structured Forensic Prompt
                         │
                         ▼
        Stability AI SDXL Generation
                 │
      (Fallback if unavailable)
                 ▼
      Hugging Face Image Generation
                 │
      (Fallback if unavailable)
                 ▼
         Offline Simulation Mode
                 │
                 ▼
      Generated Composite Sketch
                 │
                 ▼
     Criminal Database Comparison
                 │
                 ▼
        Investigation Report
```

---

# ⚙ How It Works

### Step 1

The investigator enters a witness description.

Example:

> Male, approximately 35 years old, short beard, scar on left cheek, deep-set eyes.

↓

### Step 2

The description is refined using an LLM to create a detailed forensic image-generation prompt.

↓

### Step 3

The optimized prompt is sent to Stability AI.

↓

### Step 4

If Stability AI is unavailable, the request automatically falls back to Hugging Face.

↓

### Step 5

If no AI service is available, FaceTrace AI enters Offline Simulation Mode and retrieves the closest matching suspect based on trait similarity.

↓

### Step 6

Generated sketches are saved and added to the investigation history.

---

# 🚀 Getting Started

## Prerequisites

- Python 3.9+
- Git
- Hugging Face Access Token
- Stability AI API Key (Optional)

---

## Clone Repository

```bash
git clone https://github.com/Ashirrrwad/FaceTrace_AI.git

cd FaceTrace_AI
```

---

## Create Virtual Environment

Windows

```bash
python -m venv venv

venv\Scripts\activate
```

Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create a `.env` file.

```env
HF_TOKEN=your_huggingface_token

STABILITY_API_KEY=your_stability_api_key
```

> **Note:** `STABILITY_API_KEY` is optional. If omitted, the application automatically uses Hugging Face for image generation.

---

## Run the Application

```bash
python app.py
```

Open your browser:

```
http://localhost:5001
```

---

# 📡 API Reference

## POST `/generate`

Generate suspect sketches.

### Request

```json
{
    "case_id": "CRM-1001",
    "description": "Male, 40 years old, scar on left cheek",
    "traits": {
        "gender": "Male",
        "age": "40",
        "style": "Pencil Sketch"
    }
}
```

### Response

```json
{
    "success": true,
    "primary_url": "/static/images/cases/sketch1.png",
    "var1_url": "/static/images/cases/sketch2.png",
    "var2_url": "/static/images/cases/sketch3.png",
    "confidence": 91,
    "is_simulated": false
}
```

---

## POST `/compare`

Compare suspect description against stored criminal records.

### Request

```json
{
    "description": "Female with green eyes and tattoo on neck"
}
```

### Response

```json
{
    "matches":[
        {
            "id":"CRM-201",
            "name":"Sarah Miller",
            "similarity":81
        }
    ]
}
```

---

## GET `/cases`

Returns every stored criminal profile.

---

# 📂 Project Structure

```
FaceTrace_AI
│
├── app.py
├── database.json
├── requirements.txt
├── README.md
├── .env.example
│
├── templates
│   └── index.html
│
└── static
    ├── css
    │   └── style.css
    │
    ├── js
    │   └── main.js
    │
    ├── images
    │   └── cases
    │
    └── favicon.svg
```

---

# 🛠 Tech Stack

| Layer | Technology |
|--------|------------|
| Backend | Python |
| Framework | Flask |
| Frontend | HTML, CSS, JavaScript |
| Prompt Engineering | Hugging Face LLM |
| Image Generation | Stability AI SDXL |
| Backup Generator | Hugging Face Inference API |
| Image Processing | Pillow |
| Database | JSON |
| Version Control | Git & GitHub |

---

# ⚙ AI Generation Pipeline

The application follows a three-stage generation strategy.

### Primary

✅ Stability AI SDXL

- Highest quality
- Fast generation
- Three variations

↓

### Secondary

✅ Hugging Face Inference API

- Automatic fallback
- Multiple random seeds

↓

### Final Fallback

✅ Offline Simulation

- No internet required
- Returns closest criminal sketch
- Uses similarity scoring

---

# 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| HF_TOKEN | ✅ | Hugging Face Access Token |
| STABILITY_API_KEY | Optional | Stability AI API Key |

---

# ⚠ Challenges

### Prompt Engineering

Witness descriptions are often incomplete or inconsistent.

**Solution**

Implemented LLM-based prompt refinement before image generation.

---

### AI Service Availability

External APIs may fail or become rate-limited.

**Solution**

Implemented a cascading fallback architecture.

---

### Sketch Consistency

Generative models often produce photorealistic outputs.

**Solution**

Designed forensic-specific prompts to encourage graphite pencil sketches.

---

### Criminal Matching

Generated suspects must be compared against existing records.

**Solution**

Built a similarity scoring algorithm using facial traits and metadata.

---

# 🚀 Future Enhancements

- FaceNet-based facial embeddings
- Real facial recognition support
- MongoDB integration
- Authentication system
- Cloud deployment
- PDF investigation reports
- Voice-to-sketch generation
- Multilingual witness support
- Criminal analytics dashboard
- Fine-tuned forensic diffusion model

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push your branch.
5. Open a Pull Request.

---

# 📄 License

This project is licensed under the MIT License.

---

# 🙏 Acknowledgements

Special thanks to the open-source community and the technologies that made this project possible.

- Stability AI
- Hugging Face
- Flask
- Pillow
- Python Community

---

<div align="center">

## ⭐ Star this repository if you found it useful!

Built with ❤️ by **Ashirwad**

</div>
