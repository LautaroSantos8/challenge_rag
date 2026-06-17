import cohere
import chromadb
from app.config import settings


class VectorStore:
    """Wrapper para operaciones con ChromaDB."""

    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR
        )
        self.cohere_client = cohere.Client(api_key=settings.COHERE_API_KEY)

        self.collection = self.chroma_client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    def _encode(self, texts: list[str], input_type: str) -> list[list[float]]:
        """Encodea textos usando Cohere embeddings."""
        response = self.cohere_client.embed(
            texts=texts,
            model=settings.EMBEDDING_MODEL,
            input_type=input_type
        )
        return response.embeddings

    def add_documents(self, documents: list[str], ids: list[str]) -> None:
        """Encodea y agrega documentos a la colección."""
        embeddings = self._encode(documents, input_type="search_document")
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            ids=ids
        )

    def query(self, query_text: str, n_results: int = 1) -> list[str]:
        """Encodea la pregunta y busca los documentos más relevantes."""
        query_embedding = self._encode([query_text], input_type="search_query")
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        return results["documents"][0]

    def count(self) -> int:
        return self.collection.count()