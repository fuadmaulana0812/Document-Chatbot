"""PDF extraction and text chunking."""

from collections.abc import Iterable
from io import BytesIO

from PyPDF2 import PdfReader
from langchain_text_splitters import CharacterTextSplitter

from .config import settings


def extract_pdf_text(pdf_files: Iterable[BytesIO]) -> str:
    """Extract text from PDF byte streams."""
    pages: list[str] = []
    for pdf_file in pdf_files:
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            pages.append(page.extract_text() or "")
    return "\n".join(page for page in pages if page.strip())


def split_text(text: str) -> list[str]:
    """Split extracted text into overlapping retrieval chunks."""
    splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
    )
    return splitter.split_text(text)
