import os
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
import fitz  # PyMuPDF fallback


def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """
    Extract text from uploaded file.
    Uses Azure Document Intelligence for PDFs/images.
    Falls back to PyMuPDF for plain PDFs if Azure is not configured.
    Also accepts plain text input directly.
    """
    ext = filename.lower().split(".")[-1]

    # Plain text — return directly
    if ext == "txt":
        return file_bytes.decode("utf-8", errors="ignore")

    endpoint = os.getenv("AZURE_DOC_INTELLIGENCE_ENDPOINT", "")
    key = os.getenv("AZURE_DOC_INTELLIGENCE_KEY", "")

    # Use Azure Document Intelligence if configured
    if endpoint and key:
        return _extract_with_azure(file_bytes, endpoint, key)

    # Fallback: PyMuPDF for PDFs only
    if ext == "pdf":
        return _extract_with_pymupdf(file_bytes)

    return "Could not extract text. Please configure Azure Document Intelligence for image/scanned PDF support."


def _extract_with_azure(file_bytes: bytes, endpoint: str, key: str) -> str:
    """Use Azure Document Intelligence to extract text."""
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


def _extract_with_pymupdf(file_bytes: bytes) -> str:
    """Use PyMuPDF as a free fallback for digital PDFs."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()
