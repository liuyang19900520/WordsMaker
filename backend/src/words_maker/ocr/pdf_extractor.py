from typing import List

import fitz  # PyMuPDF


def extract_images_from_pdf(pdf_path: str, start_page: int, end_page: int) -> List[bytes]:
    """Extract each page of a PDF as PNG bytes.

    Args:
        pdf_path: Path to the PDF file.
        start_page: First page number (1-indexed, inclusive).
        end_page: Last page number (1-indexed, inclusive).

    Returns:
        List of PNG image bytes, one per page.
    """
    doc = fitz.open(pdf_path)
    images: List[bytes] = []
    for page_num in range(start_page - 1, min(end_page, len(doc))):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        images.append(pix.tobytes("png"))
    return images
