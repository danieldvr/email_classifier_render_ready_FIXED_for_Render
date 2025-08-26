from pdfminer.high_level import extract_text

def extract_text_from_pdf(file_stream) -> str:
    # file_stream é um FileStorage (werkzeug)
    return extract_text(file_stream)
