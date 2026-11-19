"""Streamlit interface for the Document Chatbot API."""

import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("DOCUMENT_CHATBOT_API_URL", "http://127.0.0.1:8000").rstrip("/")


def _show_api_error(error: requests.RequestException) -> None:
    response = getattr(error, "response", None)
    if response is not None:
        try:
            message = response.json().get("detail", response.text)
        except ValueError:
            message = response.text
        st.error(f"Backend error: {message}")
    else:
        st.error(f"Could not connect to the backend at {API_URL}. Start the FastAPI server and try again.")


def _process_documents(uploaded_files) -> None:
    if not uploaded_files:
        st.sidebar.warning("Upload at least one PDF first.")
        return

    files = [
        ("files", (file.name, file.getvalue(), "application/pdf"))
        for file in uploaded_files
    ]
    try:
        with st.spinner("Processing documents…"):
            response = requests.post(
                f"{API_URL}/documents/process", files=files, timeout=900
            )
            response.raise_for_status()
        result = response.json()
        st.session_state.session_id = result["session_id"]
        st.session_state.messages = []
        st.sidebar.success(
            f"Processed {result['document_count']} PDF(s) into {result['chunk_count']} chunks."
        )
    except requests.RequestException as error:
        _show_api_error(error)


def _render_chat() -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask a question about your documents")
    if not question:
        return
    if not st.session_state.session_id:
        st.info("Upload and process your PDFs first.")
        return

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    try:
        with st.chat_message("assistant"):
            with st.spinner("Finding an answer…"):
                response = requests.post(
                    f"{API_URL}/chat",
                    json={"session_id": st.session_state.session_id, "question": question},
                    timeout=300,
                )
                response.raise_for_status()
                answer = response.json()["answer"]
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
    except requests.RequestException as error:
        st.session_state.messages.pop()
        _show_api_error(error)


def main() -> None:
    st.set_page_config(page_title="Document Chatbot", page_icon="📚")
    st.title("Document Chatbot 📚")
    st.caption("Upload PDF documents and ask questions about their contents.")

    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.subheader("Your documents")
        uploaded_files = st.file_uploader(
            "Upload PDFs", type=["pdf"], accept_multiple_files=True
        )
        if st.button("Process documents", type="primary"):
            _process_documents(uploaded_files)

    _render_chat()


if __name__ == "__main__":
    main()
