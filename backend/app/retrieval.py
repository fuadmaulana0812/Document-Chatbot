"""Vector indexing and conversational retrieval."""

from functools import lru_cache

from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline

from .config import settings


def create_vector_store(text_chunks: list[str]) -> FAISS:
    """Embed chunks and build an in-memory FAISS index."""
    embeddings = HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
    )
    return FAISS.from_texts(texts=text_chunks, embedding=embeddings)


@lru_cache(maxsize=1)
def _load_local_llm() -> HuggingFacePipeline:
    """Load and reuse a small local model; inference does not use a paid API."""
    return HuggingFacePipeline.from_model_id(
        model_id=settings.llm_model_id,
        task="text2text-generation",
        pipeline_kwargs={"max_new_tokens": 256, "do_sample": False},
    )


def create_conversation_chain(vector_store: FAISS) -> ConversationalRetrievalChain:
    """Create a conversational chain backed by the document index."""
    memory = ConversationBufferMemory(
        memory_key="chat_history", return_messages=True, output_key="answer"
    )
    return ConversationalRetrievalChain.from_llm(
        llm=_load_local_llm(),
        retriever=vector_store.as_retriever(),
        memory=memory,
        return_source_documents=False,
    )
