import os
import uuid
import logging
import re
import cohere

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
        self.cohere_client = cohere.Client(api_key=settings.COHERE_API_KEY)

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

    def delete_document(self, filename: str) -> int:
        """Elimina un documento y sus chunks de la vector DB y del disco."""
        data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
        file_path = os.path.abspath(os.path.join(data_dir, filename))

        deleted = self.vector_store.delete_by_filename(filename)

        if os.path.exists(file_path):
            os.remove(file_path)

        self.cache = {}

        logger.info(f"Eliminado {filename}: {deleted} chunks borrados")
        return deleted

    def ask(self, question: str) -> dict:
        """
        Procesa una pregunta a través del pipeline RAG.
        1. Verifica si la pregunta ya está en caché.
        2. Encodea la pregunta y recupera los 3 chunks más similares de ChromaDB.
        3. Reordena los chunks con Cohere Rerank para seleccionar el más relevante.
        4. Si el score es bajo, responde conversacionalmente.
        5. Si el score es alto, pasa el mejor chunk como contexto al LLM.
        6. Guarda en caché y retorna la respuesta.
        """
        normalized = self._normalize(question)

        if normalized in self.cache:
            logger.debug("Respuesta obtenida desde caché")
            return self.cache[normalized]

        relevant_docs = self.vector_store.query(query_text=question, n_results=3)

        # Reordenar por relevancia real
        rerank_response = self.cohere_client.rerank(
            model=settings.RERANK_MODEL,
            query=question,
            documents=relevant_docs,
            top_n=1
        )

        best_result = rerank_response.results[0]
        best_index = best_result.index
        relevance_score = best_result.relevance_score

        logger.debug(f"Rerank: chunk {best_index} seleccionado, score: {relevance_score}")

        # Si el score es bajo, la pregunta no es sobre los documentos
        if relevance_score < 0.3:
            docs = self.vector_store.list_documents()
            answer = self.llm_service.generate_conversation(
                question=question,
                documents=docs
            )
            result = {"answer": answer}
            if len(self.cache) >= settings.CACHE_MAX_SIZE:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            self.cache[normalized] = result
            return result

        context = relevant_docs[best_index]
        logger.debug(f"Contexto recuperado: {context}")

        answer = self.llm_service.generate_answer(
            question=question,
            context=context
        )

        result = {"answer": answer, "context": context}
        if len(self.cache) >= settings.CACHE_MAX_SIZE:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        self.cache[normalized] = result
        return result