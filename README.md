# DocuMind AI — Question Paper Solver
Upload question papers (PDF, image, text) and get AI-powered answers, summaries, and document chat — now with **multilingual support for 11 languages**.

🔗 **Live App**: https://drishti-makkar-documind-ai-ai-powered-ocr-and-docume-app-0eujqa.streamlit.app/

---

## ✨ What's New
- 🌐 **Multilingual support** — answer questions in 11 languages
- 🔤 **Multilingual OCR** — extract text from Hindi, Gujarati, Tamil, and more
- 🗂️ **Language selector** in sidebar — OCR and AI both follow your language choice
- 📝 **DOCX support** — upload Word documents directly

---

## Stack
- **Frontend**: Streamlit
- **AI**: Groq API (Llama 3.3 70B) — free
- **Storage**: Azure Blob Storage — free 5GB
- **OCR**: Azure Document Intelligence + Tesseract OCR
- **Hosting**: Streamlit Cloud — free

---

## 🌐 Supported Languages
| Language | OCR Support | AI Answers |
|----------|------------|------------|
| English  | ✅ | ✅ |
| Hindi    | ✅ | ✅ |
| Gujarati | ✅ | ✅ |
| Marathi  | ✅ | ✅ |
| Tamil    | ✅ | ✅ |
| Telugu   | ✅ | ✅ |
| Bengali  | ✅ | ✅ |
| French   | ✅ | ✅ |
| Spanish  | ✅ | ✅ |
| German   | ✅ | ✅ |
| Arabic   | ✅ | ✅ |

---

## Local Setup

### 1. Clone and install
```bash
git clone <your-repo>
cd question_paper_solver_fixed
pip install -r requirements.txt
```

### 2. Install Tesseract OCR (required for image/scanned PDF support)
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to: `C:\Program Files\Tesseract-OCR\`
3. Download language packs from: https://github.com/tesseract-ocr/tessdata
4. Place `.traineddata` files in: `C:\Program Files\Tesseract-OCR\tessdata\`

| Language | File |
|----------|------|
| Hindi    | `hin.traineddata` |
| Gujarati | `guj.traineddata` |
| Marathi  | `mar.traineddata` |
| Tamil    | `tam.traineddata` |
| Telugu   | `tel.traineddata` |
| Bengali  | `ben.traineddata` |
| French   | `fra.traineddata` |
| Spanish  | `spa.traineddata` |
| German   | `deu.traineddata` |
| Arabic   | `ara.traineddata` |

### 3. Set up environment variables
```bash
cp .env.example .env
# Edit .env and fill in your keys
```

### 4. Get your free API keys

**Groq API (required)**
1. Go to https://console.groq.com
2. Sign up → API Keys → Create new key
3. Paste into `GROQ_API_KEY`

**Azure Blob Storage (optional — for cloud file storage)**
1. Azure Portal → Create Storage Account
2. Go to Access Keys → copy Connection String
3. Paste into `AZURE_STORAGE_CONNECTION_STRING`

**Azure Document Intelligence (optional — for scanned PDFs / images)**
1. Azure Portal → Create Document Intelligence resource
2. Go to Keys and Endpoint
3. Copy Key and Endpoint into the `.env`

> Without Azure keys, the app still works for digital PDFs and text using PyMuPDF + Tesseract.

### 5. Run locally
```bash
streamlit run app.py
```

---

## Deploy to Streamlit Cloud (free)
1. Push this project to a GitHub repo
2. Go to https://streamlit.io/cloud → New app
3. Connect your GitHub repo, set `app.py` as the main file
4. Go to **Settings → Secrets** and add your keys in TOML format:

```toml
GROQ_API_KEY = "your_key"
AZURE_STORAGE_CONNECTION_STRING = "your_connection_string"
AZURE_CONTAINER_NAME = "question-papers"
AZURE_DOC_INTELLIGENCE_ENDPOINT = "https://..."
AZURE_DOC_INTELLIGENCE_KEY = "your_key"
```

---

## Features
| Feature | Description |
|---------|-------------|
| 📄 Upload PDF | Upload digital or scanned question paper PDF |
| 🖼️ Upload Image | Upload photo of a question paper |
| 📝 Upload DOCX | Upload Word documents |
| ✏️ Paste Text | Paste questions directly |
| ☁️ Azure Storage | Load previously uploaded files from cloud |
| 🌐 Language Selector | Choose language for both OCR and AI answers |
| 💬 Chat | Ask anything about the document |
| ✅ Answer All | Auto-answer every question in the paper |
| 📋 Summary | Get subject, type, difficulty summary |

---

## Project Structure
question_paper_solver_fixed/
├── app.py                        # Main Streamlit app
├── requirements.txt              # Python dependencies
├── packages.txt                  # System dependencies
├── .env.example                  # Environment variable template
├── .streamlit/
│   └── secrets.toml.example     # Streamlit Cloud secrets template
└── utils/
├── ai.py                     # Groq AI — chat, answer, summarize
├── extractor.py              # OCR — Tesseract + Azure + PyMuPDF
└── storage.py                # Azure Blob Storage

---

## How It Works
1. **Upload** a question paper in any supported format
2. **Select your language** from the sidebar
3. The app **extracts text** using Tesseract OCR (with your chosen language) or Azure Document Intelligence
4. The **AI reads the document** and answers all questions in your selected language
5. You can also **chat** with the document or get a **summary**
