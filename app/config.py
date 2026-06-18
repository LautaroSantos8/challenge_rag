from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación cargada desde variables de entorno."""

    # Cohere
    COHERE_API_KEY: str
    LLM_MODEL: str = "command-r-plus-08-2024"
    EMBEDDING_MODEL: str = "embed-multilingual-v3.0"
    LLM_TEMPERATURE: float = 0.0

    # ChromaDB
    CHROMA_COLLECTION_NAME: str = "document_collection"

    # Procesamiento del documento
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    LOG_LEVEL: str = "DEBUG"

    CHROMA_PERSIST_DIR: str = "./chroma_db"
    RERANK_MODEL: str = "rerank-v3.5"

    CACHE_MAX_SIZE: int = 100

    class Config:
        env_file = ".env"


settings = Settings()