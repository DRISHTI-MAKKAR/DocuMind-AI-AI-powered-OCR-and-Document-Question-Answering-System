import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

# ── Tesseract path (Windows) ──────────────────────────────────────────────────
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ── Language map: app language → Tesseract lang code ─────────────────────────
LANGUAGE_MAP = {
    "English":  "eng",
    "Hindi":    "eng+hin",
    "Gujarati": "eng+guj",
    "Marathi":  "eng+mar",
    "Tamil":    "eng+tam",
    "Telugu":   "eng+tel",
    "Bengali":  "eng+ben",
    "French":   "eng+fra",
    "Spanish":  "eng+spa",
    "German":   "eng+deu",
    "Arabic":   "eng+ara",
}

# ── Tessdata files needed for each language ───────────────────────────────────
TESSDATA_FILES = {
    "Hindi":    "hin.traineddata",
    "Gujarati": "guj.traineddata",
    "Marathi":  "mar.traineddata",
    "Tamil":    "tam.traineddata",
    "Telugu":   "tel.traineddata",
    "Bengali":  "ben.traineddata",
    "French":   "fra.traineddata",
    "Spanish":  "spa.traineddata",
    "German":   "deu.traineddata",
    "Arabic":   "ara.traineddata",
}

# Optional Azure fallback
try:
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.core.credentials import AzureKeyCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False


def check_tessdata(language: str) -> tuple[bool, str]:
    """
    Check if the required tessdata file exists for a language.
    Returns (is_ok, warning_message)
    """
    if language == "English":
        return True, ""

    tessdata_file = TESSDATA_FILES.get(language, "")
    if not tessdata_file:
        return True, ""

    tessdata_dir = r"C:\Program Files\Tesseract-OCR\tessdata"
    full_path = os.path.join(tessdata_dir, tessdata_file)

    if not os.path.exists(full_path):
        return False, (
            f"⚠️ Tesseract language file for **{language}** is missing.\n\n"
            f"Please download `{tessdata_file}` from:\n"
            f"https://github.com/tesseract-ocr/tessdata\n\n"
            f"And place it in:\n`{tessdata_dir}`"
        )
    return True, ""


def extract_text_from_file(file_bytes: bytes, filename: str, language: str = "English") -> str:
    """
    Extract text from uploaded file with language support.
    - .txt        → plain decode
    - .pdf        → PyMuPDF (digital) OR Tesseract page-by-page (scanned)
    - .png/.jpg   → Tesseract OCR
    - .docx       → python-docx
    - Azure Doc Intelligence used only if keys are configured
    """
    ext = filename.lower().split(".")[-1]

    # Plain text — return directly
    if ext == "txt":
        return file_bytes.decode("utf-8", errors="ignore")

    # Word documents
    if ext == "docx":
        return _extract_with_docx(file_bytes)

    endpoint = os.getenv("AZURE_DOC_INTELLIGENCE_ENDPOINT", "")
    key      = os.getenv("AZURE_DOC_INTELLIGENCE_KEY", "")

    # Azure takes priority if configured
    if AZURE_AVAILABLE and endpoint and key:
        return _extract_with_azure(file_bytes, endpoint, key)

    # Images → Tesseract OCR
    if ext in ("png", "jpg", "jpeg"):
        return _extract_with_tesseract(file_bytes, language)

    # PDFs → try PyMuPDF first, fall back to Tesseract if scanned
    if ext == "pdf":
        text = _extract_with_pymupdf(file_bytes)
        if len(text.strip()) < 50:  # likely a scanned PDF
            return _extract_pdf_with_tesseract(file_bytes, language)
        return text

    return "Unsupported file type."


def _extract_with_tesseract(file_bytes: bytes, language: str = "English") -> str:
    """OCR a single image using Tesseract with language support."""
    lang_code = LANGUAGE_MAP.get(language, "eng")
    img = Image.open(io.BytesIO(file_bytes))

    # Improve OCR accuracy — convert to RGB if needed
    if img.mode != "RGB":
        img = img.convert("RGB")

    return pytesseract.image_to_string(img, lang=lang_code)


def _extract_pdf_with_tesseract(file_bytes: bytes, language: str = "English") -> str:
    """OCR each page of a scanned PDF using PyMuPDF + Tesseract."""
    lang_code = LANGUAGE_MAP.get(language, "eng")
    doc  = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        # Render page to image at 300 DPI for better OCR accuracy
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text += pytesseract.image_to_string(img, lang=lang_code) + "\n"
    return text.strip()


def _extract_with_pymupdf(file_bytes: bytes) -> str:
    """Extract text from a digital PDF (no OCR needed)."""
    doc  = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()


def _extract_with_docx(file_bytes: bytes) -> str:
    """Extract text from a Word .docx file."""
    try:
        import docx
        doc  = docx.Document(io.BytesIO(file_bytes))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except ImportError:
        return "python-docx not installed. Run: pip install python-docx"


def _extract_with_azure(file_bytes: bytes, endpoint: str, key: str) -> str:
    """Use Azure Document Intelligence to extract text (optional)."""
    client  = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    poller  = client.begin_analyze_document(
        "prebuilt-read",
        analyze_request=file_bytes,
        content_type="application/octet-stream",
    )
    result    = poller.result()
    extracted = []
    for page in result.pages:
        for line in page.lines:
            extracted.append(line.content)
    return "\n".join(extracted)