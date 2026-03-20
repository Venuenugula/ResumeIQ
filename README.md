<div align="center">

# 🧠 ResumeIQ

### AI-Powered Resume Analyzer for Freshers & Students

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain.com)
[![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![FAISS](https://img.shields.io/badge/FAISS-Vector_DB-orange?style=for-the-badge)](https://github.com/facebookresearch/faiss)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<br/>

**Upload your resume. Paste a job description. Get an AI match score, skill gap analysis, tailored cover letter, interview questions, and more — in seconds.**

[🚀 Live Demo](#) · [📸 Screenshots](#screenshots) · [⚡ Quick Start](#quick-start) · [🛠 Tech Stack](#tech-stack)

<br/>

![ResumeIQ Demo](https://raw.githubusercontent.com/Venuenugula/ResumeIQ/main/assets/demo.png)

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 📊 **AI Match Score** | Get a 0–100% compatibility score between your resume and any job description |
| 🔍 **ATS Keyword Scanner** | Find which JD keywords are missing from your resume before you apply |
| 📉 **Skill Gap Analysis** | See exactly which skills you have vs what the role requires |
| ✉️ **Cover Letter Generator** | Get a tailored, professional cover letter written for your specific resume + JD |
| 🎯 **Interview Question Predictor** | 10 likely interview questions with personalized tips based on your gaps |
| ✏️ **Resume Bullet Rewriter** | Paste weak bullets — Gemini rewrites them with strong action verbs and metrics |
| 🔗 **LinkedIn Summary Generator** | Auto-generate a compelling LinkedIn About section for your target role |
| 🏆 **Multi-JD Comparison** | Upload one resume, compare 3 JDs — find out which role you're best suited for |

---

## 📸 Screenshots

<div align="center">

### Match Score + Gap Analysis
> Animated score ring, color-coded skill badges, and AI verdict

### Interview Question Predictor
> Role-specific questions with personalized tips

### Resume Bullet Rewriter
> Before/after comparison with ATS-optimized rewrites

</div>

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- A free [Gemini API key](https://aistudio.google.com/apikey) (takes 2 minutes)

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/Venuenugula/ResumeIQ.git
cd ResumeIQ

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your API key
echo "GEMINI_API_KEY=your_key_here" > .env

# 5. Run the app
streamlit run app.py
```

Open **http://localhost:8501** in your browser. That's it! 🎉

---

## 🛠 Tech Stack

```
ResumeIQ/
├── app.py                  ← Streamlit UI (all tabs, styling, state)
├── utils/
│   ├── parser.py           ← PDF text extraction (pypdf)
│   ├── rag.py              ← LangChain + FAISS vector pipeline
│   ├── analyzer.py         ← Gemini match score + gap analysis
│   └── generator.py        ← Cover letter, interview Qs, bullet rewriter, LinkedIn
├── .env                    ← API key (never committed)
├── requirements.txt
└── README.md
```

| Layer | Technology | Why |
|---|---|---|
| **LLM** | Gemini 2.5 Flash | Fast, free tier, excellent instruction following |
| **Embeddings** | sentence-transformers `all-MiniLM-L6-v2` | Fully local, offline, zero API cost |
| **Vector DB** | FAISS | Lightweight, fast similarity search, no server needed |
| **RAG Framework** | LangChain | Clean chunking, retrieval, and prompt chaining |
| **UI** | Streamlit | Rapid prototyping, easy deployment |
| **PDF Parsing** | pypdf | Reliable text extraction from any PDF resume |

---

## 🏗 How It Works

```
Upload Resume PDF
       │
       ▼
  pypdf extracts text
       │
       ▼
  LangChain chunks resume into 500-token segments
       │
       ▼
  sentence-transformers embeds chunks → FAISS index
       │
       ▼
  JD text used as query → retrieve top 6 relevant chunks
       │
       ▼
  Gemini 2.5 Flash analyzes chunks vs JD
       │
       ├── Match score (0-100)
       ├── Matched / missing skills
       ├── Strengths + improvements
       ├── Cover letter
       ├── Interview questions
       ├── Bullet rewrites
       └── LinkedIn summary
```

---

## 📦 Installation Details

### Full `requirements.txt`

```
streamlit
langchain
langchain-community
langchain-google-genai
faiss-cpu
pypdf
python-dotenv
google-genai
sentence-transformers
requests
```

Install all at once:

```bash
pip install -r requirements.txt
```

---

## 🔑 API Key Setup

1. Go to [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Click **Create API key in new project**
3. Copy the key
4. Add to `.env`:

```env
GEMINI_API_KEY=your_key_here
```

> **Free tier limits:** 1500 requests/day per key. For development, create 2 keys and the app auto-rotates between them.

---

## ☁️ Deploy on Streamlit Cloud (Free)

1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select your forked repo
4. Set **Main file path** to `app.py`
5. Under **Advanced settings → Secrets**, add:
```toml
GEMINI_API_KEY = "your_key_here"
```
6. Click **Deploy** — you get a live URL in ~2 minutes 🚀

---

## 🗺 Roadmap

- [x] PDF resume parsing
- [x] RAG pipeline with FAISS
- [x] AI match score + gap analysis
- [x] ATS keyword scanner
- [x] Cover letter generator
- [x] Interview question predictor
- [x] Resume bullet rewriter
- [x] LinkedIn summary generator
- [x] Multi-JD comparison
- [ ] Resume PDF export with suggested edits
- [ ] Job scraping integration (extend Hire Scout)
- [ ] User accounts + history
- [ ] Support for DOCX resumes
- [ ] Chrome extension

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

```bash
# Fork the repo, then:
git checkout -b feature/your-feature-name
git commit -m "feat: add your feature"
git push origin feature/your-feature-name
# Open a Pull Request
```

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

### Built with ❤️ by Venu Enugula

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/venu-enugula-mlengineer)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Venuenugula)
[![PyPI](https://img.shields.io/badge/PyPI-dsa--daa--kit-3775A9?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/dsa-daa-kit/)

*If this project helped you, please consider giving it a ⭐ on GitHub!*

</div>
