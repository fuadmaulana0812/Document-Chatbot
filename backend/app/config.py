"""Backend settings and environment loading."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    llm_model_id: str = "google/flan-t5-base"
    chunk_size: int = 1000
    chunk_overlap: int = 200


settings = Settings()
