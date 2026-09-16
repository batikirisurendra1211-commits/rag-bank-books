from pathlib import Path

from pypdf import PdfReader


def extract_pdf_pages(file_path: str) -> list[dict]:
    """
    Extract text from a PDF page by page.

    Args:
        file_path: Path to the PDF file.

    Returns:
        A list of dictionaries containing:
        - page_number
        - text
    """

    pdf_path = Path(file_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {pdf_path}"
        )

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(
            "The provided file is not a PDF."
        )

    reader = PdfReader(str(pdf_path))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        try:
            text = page.extract_text() or ""

        except Exception as exc:
            print(
                f"Warning: Could not extract page "
                f"{page_number}: {exc}"
            )
            text = ""

        text = text.strip()

        pages.append(
            {
                "page_number": page_number,
                "text": text,
            }
        )

    return pages