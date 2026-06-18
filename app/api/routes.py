import logging

from fastapi import APIRouter, HTTPException, UploadFile, File
import os
import shutil

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

@router.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    """Sube un documento y lo procesa en la vector DB."""
    if not file.filename.endswith((".docx", ".pdf")):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos .docx y .pdf")

    data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
    data_dir = os.path.abspath(data_dir)
    file_path = os.path.join(data_dir, file.filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    num_chunks = rag_service.load_document(file_path)

    return {
        "message": f"Documento {file.filename} cargado exitosamente",
        "chunks_creados": num_chunks
    }

@router.delete("/documents/{filename}")
async def delete_document(filename: str):
    """Elimina un documento y sus chunks de la vector DB."""
    deleted = rag_service.delete_document(filename)

    if deleted == 0:
        raise HTTPException(status_code=404, detail=f"No se encontraron chunks para {filename}")

    return {
        "message": f"Documento {filename} eliminado exitosamente",
        "chunks_eliminados": deleted
    }