"""Application services and in-memory conversation storage."""

from io import BytesIO
from uuid import uuid4

from .documents import extract_pdf_text, split_text
from .retrieval import create_conversation_chain, create_vector_store

_conversations = {}


def process_documents(files: list[tuple[str, bytes]]) -> dict[str, str | int]:
    pdf_streams = [BytesIO(contents) for _, contents in files]
    text = extract_pdf_text(pdf_streams)
    if not text.strip():
        raise ValueError("No readable text was found in the uploaded PDFs.")

    chunks = split_text(text)
    if not chunks:
        raise ValueError("The uploaded PDFs did not produce any text chunks.")

    vector_store = create_vector_store(chunks)
    chain = create_conversation_chain(vector_store)
    session_id = str(uuid4())
    _conversations[session_id] = chain
    return {"session_id": session_id, "document_count": len(files), "chunk_count": len(chunks)}


def ask_question(session_id: str, question: str) -> str:
    chain = _conversations.get(session_id)
    if chain is None:
        raise KeyError("Conversation not found. Process your PDFs again.")
    response = chain.invoke({"question": question})
    return response["answer"]
