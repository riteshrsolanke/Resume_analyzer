"""
PDF text extraction using pdfplumber.
"""
import pdfplumber


def extract_text_from_pdf(file_obj):
    """
    Extract text from a PDF file-like object (e.g. Django UploadedFile or path).
    Returns the concatenated text of all pages, or '' if nothing could be read.
    """
    text_chunks = []
    try:
        with pdfplumber.open(file_obj) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_chunks.append(page_text)
    except Exception as exc:
        # Caller decides how to surface this; we just avoid crashing the request.
        return ''
    return '\n'.join(text_chunks).strip()


def count_pdf_pages(file_obj):
    try:
        with pdfplumber.open(file_obj) as pdf:
            return len(pdf.pages)
    except Exception:
        return 0
