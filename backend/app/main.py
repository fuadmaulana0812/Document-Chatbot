"""FastAPI routes for PDF processing and document chat."""

import logging

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from .service import ask_question, process_documents

app = FastAPI(title="Document Chatbot API", version="1.0.0")
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    session_id: str
    question: str = Field(min_length=1, max_length=4000)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/documents/process")
async def process_uploaded_documents(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="Upload at least one PDF.")

    payload: list[tuple[str, bytes]] = []
    for file in files:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        payload.append((file.filename, await file.read()))

    try:
        return process_documents(payload)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Could not process documents: {error}") from error


@app.post("/chat")
def chat(request: ChatRequest) -> dict[str, str]:
    try:
        answer = ask_question(request.session_id, request.question.strip())
        return {"answer": answer}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error).strip("'")) from error
    except Exception as error:
        logger.exception("Could not answer chat question")
        message = str(error).strip() or repr(error)
        raise HTTPException(
            status_code=500,
            detail=f"Could not answer question ({type(error).__name__}): {message}",
        ) from error
