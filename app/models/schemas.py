from pydantic import BaseModel


class QuestionRequest(BaseModel):
    """Esquema del request de entrada."""
    user_name: str
    question: str


class AnswerResponse(BaseModel):
    """Esquema de la respuesta de la API."""
    answer: str