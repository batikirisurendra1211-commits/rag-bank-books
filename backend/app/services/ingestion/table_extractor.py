import pdfplumber

def extract_tables(file_path: str):
    results = []
    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables() or []
            for table in tables:
                results.append({"page_number": page_number, "rows": table})
    return results
