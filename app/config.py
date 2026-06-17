from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación cargada desde variables de entorno."""

    # Cohere
    COHERE_API_KEY: str
    LLM_MODEL: str = "command-r-plus"
    EMBEDDING_MODEL: str = "embed-multilingual-v3.0"
    LLM_TEMPERATURE: float = 0.0

    # ChromaDB
    CHROMA_COLLECTION_NAME: str = "document_collection"

    # Procesamiento del documento
    CHUNK_SIZE: int = 300
    CHUNK_OVERLAP: int = 50

    LOG_LEVEL: str = "DEBUG"

    class Config:
        env_file = ".env"


settings = Settings()