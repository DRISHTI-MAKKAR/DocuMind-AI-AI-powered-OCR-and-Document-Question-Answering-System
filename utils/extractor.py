import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

# Optional Azure fallback (only used if keys are set)
try:
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.core.credentials import AzureKeyCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False


def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """
    Extract text from uploaded file.
    - .txt        → plain decode
    - .pdf        → PyMuPDF (digital) OR Tesseract page-by-page (scanned)
    - .png/.jpg   → Tesseract OCR
    - Azure Doc Intelligence used only if keys are configured
    """
    ext = filename.lower().split(".")[-1]

    # Plain text — return directly
    if ext == "txt":
        return file_bytes.decode("utf-8", errors="ignore")

    endpoint = os.getenv("AZURE_DOC_INTELLIGENCE_ENDPOINT", "")
    key = os.getenv("AZURE_DOC_INTELLIGENCE_KEY", "")

    # Azure takes priority if configured
    if AZURE_AVAILABLE and endpoint and key:
        return _extract_with_azure(file_bytes, endpoint, key)

    # Images → Tesseract OCR
    if ext in ("png", "jpg", "jpeg"):
        return _extract_with_tesseract(file_bytes)

    # PDFs → try PyMuPDF first, fall back to Tesseract if scanned
    if ext == "pdf":
        text = _extract_with_pymupdf(file_bytes)
        if len(text.strip()) < 50:  # likely a scanned PDF
            return _extract_pdf_with_tesseract(file_bytes)
        return text

    return "Unsupported file type."


def _extract_with_tesseract(file_bytes: bytes) -> str:
    """OCR a single image using Tesseract."""
    img = Image.open(io.BytesIO(file_bytes))
    return pytesseract.image_to_string(img)


def _extract_pdf_with_tesseract(file_bytes: bytes) -> str:
    """OCR each page of a scanned PDF using PyMuPDF + Tesseract."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        # Render page to image at 300 DPI
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text += pytesseract.image_to_string(img) + "\n"
    return text.strip()


def _extract_with_pymupdf(file_bytes: bytes) -> str:
    """Extract text from a digital PDF (no OCR needed)."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()


def _extract_with_azure(file_bytes: bytes, endpoint: str, key: str) -> str:
    """Use Azure Document Intelligence to extract text (optional)."""
    client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    poller = client.begin_analyze_document(
        "prebuilt-read",
        analyze_request=file_bytes,
        content_type="application/octet-stream",
    )
    result = poller.result()
    extracted = []
    for page in result.pages:
        for line in page.lines:
            extracted.append(line.content)
    return "\n".join(extracted)
