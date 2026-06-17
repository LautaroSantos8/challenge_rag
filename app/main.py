import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.api.routes import router, rag_service


logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Carga los documentos en el vector store al iniciar la API."""
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    data_dir = os.path.abspath(data_dir)

    if rag_service.vector_store.count() == 0:
        for filename in os.listdir(data_dir):
            if filename.endswith((".docx", ".pdf")):
                file_path = os.path.join(data_dir, filename)
                num_chunks = rag_service.load_document(file_path)
                logger.info(f"Cargado {filename}: {num_chunks} chunks")
    else:
        logger.info(f"Vector store ya tiene {rag_service.vector_store.count()} documentos")

    yield


app = FastAPI(
    title="Challenge RAG API",
    description="API RAG para responder preguntas sobre documentos usando Cohere y ChromaDB.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router, prefix="/api/v1", tags=["RAG"])