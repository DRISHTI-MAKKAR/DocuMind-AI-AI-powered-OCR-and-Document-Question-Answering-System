# Question Paper AI

Upload question papers (PDF, image, text) and get AI-powered answers, summaries, and document chat.

## Stack
- **Frontend**: Streamlit
- **AI**: Groq API (Llama 3.3 70B) — free
- **Storage**: Azure Blob Storage — free 5GB
- **OCR**: Azure Document Intelligence — free 500 pages/month
- **Hosting**: Streamlit Cloud — free

---

## Local Setup

### 1. Clone and install
```bash
git clone <your-repo>
cd qna-app
pip install -r requirements.txt
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Edit .env and fill in your keys
```

### 3. Get your free API keys

**Groq API (required)**
1. Go to https://console.groq.com
2. Sign up → API Keys → Create new key
3. Paste into GROQ_API_KEY

**Azure Blob Storage (optional — for cloud file storage)**
1. Azure Portal → Create Storage Account
2. Go to Access Keys → copy Connection String
3. Paste into AZURE_STORAGE_CONNECTION_STRING

**Azure Document Intelligence (optional — for scanned PDFs / images)**
1. Azure Portal → Create Document Intelligence resource
2. Go to Keys and Endpoint
3. Copy Key and Endpoint into the .env

> Without Azure keys, the app still works for digital PDFs and text using PyMuPDF.

### 4. Run locally
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
|---|---|
| 📄 Upload PDF | Upload question paper PDF |
| 🖼️ Upload Image | Upload scanned paper (requires Azure Doc Intelligence) |
| ✏️ Paste Text | Paste questions directly |
| ☁️ Azure Storage | Load previously uploaded files |
| 💬 Chat | Ask anything about the document |
| ✅ Answer All | Auto-answer every question in the paper |
| 📋 Summary | Get subject, type, difficulty summary |

---

## Project Structure

```
qna-app/
├── app.py                        # Main Streamlit app
├── requirements.txt
├── .env.example                  # Environment variable template
├── .streamlit/
│   └── secrets.toml.example     # Streamlit Cloud secrets template
└── utils/
    ├── ai.py                     # Groq AI — chat + answer
    ├── extractor.py              # Azure Doc Intelligence + PyMuPDF
    └── storage.py                # Azure Blob Storage
```
