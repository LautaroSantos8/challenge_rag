import os
import uuid
import logging
import re

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.db.vector_store import VectorStore
from app.services.document_reader import read_document
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

class RAGService:
    """Orquesta el pipeline RAG: carga de documentos, retrieval y generación."""

    def __init__(self):
        self.vector_store = VectorStore()
        self.llm_service = LLMService()
        self.cache = {}

    def load_document(self, file_path: str) -> int:
        """
        Lee un documento, lo divide en chunks y los guarda en la vector DB.

        Se usa RecursiveCharacterTextSplitter con separadores jerárquicos:
        primero por parrafo (\n\n), luego por salto de linea (\n), y finalmente por oracion (.) si el chunk sigue siendo grande.
        """
        content = read_document(file_path)

        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ". "],
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

        docs = text_splitter.create_documents([content])

        doc_ids = [f"{os.path.basename(file_path)}_chunk_{i}" for i, _ in enumerate(docs)]
        doc_texts = [doc.page_content for doc in docs]

        self.vector_store.add_documents(documents=doc_texts, ids=doc_ids)

        return len(docs)

    def _normalize(self, question: str) -> str:
        """Normaliza la pregunta para usar como clave del caché."""
        question = question.lower().strip()
        question = re.sub(r'[¿?!¡]', '', question)
        return question

    def ask(self, question: str) -> dict:
        """
        Procesa una pregunta a través del pipeline RAG.
        1. Verifica si la pregunta ya está en caché.
        2. Si no, encodea la pregunta.
        3. Busca el chunk más relevante en ChromaDB.
        4. Pasa el chunk como contexto al LLM.
        5. Guarda en caché y retorna la respuesta.
        """
        normalized = self._normalize(question)

        if normalized in self.cache:
            logger.debug("Respuesta obtenida desde caché")
            return self.cache[normalized]

        relevant_docs = self.vector_store.query(
            query_text=question, n_results=1
        )
        context = relevant_docs[0] if relevant_docs else ""
        logger.debug(f"Contexto recuperado: {context}")

        answer = self.llm_service.generate_answer(
            question=question,
            context=context
        )

        result = {"answer": answer, "context": context}
        self.cache[normalized] = result

        return result