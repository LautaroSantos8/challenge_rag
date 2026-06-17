import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import QuestionRequest, AnswerResponse
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)

router = APIRouter()
rag_service = RAGService()


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """Recibe una pregunta y devuelve la respuesta generada por el LLM."""
    try:
        result = rag_service.ask(question=request.question)
        logger.debug(f"Contexto usado: {result['context']}")

        return AnswerResponse(answer=result["answer"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la API."""
    return {
        "status": "healthy",
        "documentos_cargados": rag_service.vector_store.count()
    }