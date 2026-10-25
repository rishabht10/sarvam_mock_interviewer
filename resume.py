from io import BytesIO

from pypdf import PdfReader


def extract_text(file_bytes: bytes, max_chars: int = 6000) -> str:
    """Pull text out of a PDF resume. Scanned PDFs have no text layer and return ''."""
    reader = PdfReader(BytesIO(file_bytes))
    text = "\n".join((page.extract_text() or "") for page in reader.pages)
    return text.strip()[:max_chars]
