import os
from docx import Document
from PyPDF2 import PdfReader


def read_document(file_path: str) -> str:
    """Lee el contenido de un documento .docx o .pdf."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Documento no encontrado: {file_path}")

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".docx":
        with open(file_path, "rb") as f:
            doc = Document(f)
            return "\n\n".join([p.text for p in doc.paragraphs if p.text.strip()])

    elif extension == ".pdf":
        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            return "\n\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

    else:
        raise ValueError(f"Formato no soportado: {extension}")