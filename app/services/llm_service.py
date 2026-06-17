import cohere
from app.config import settings

SYSTEM_PROMPT = """Eres un asistente que responde preguntas basándose ÚNICAMENTE en el contexto proporcionado.

Reglas estrictas:
1. Responder en exactamente UNA oración.
2. Responder en el MISMO idioma en que se hace la pregunta.
3. Incluir emojis relevantes que resuman el contenido de la oración.
4. Responder siempre en TERCERA PERSONA.
5. Basarse SOLO en el contexto proporcionado."""

USER_PROMPT_TEMPLATE = """Contexto: {context}

Pregunta: {question}

Recordar: responder en UNA oración, en el mismo idioma de la pregunta, con emojis, en tercera persona, basándose solo en el contexto."""


class LLMService:
    """Servicio para interactuar con el LLM de Cohere."""

    def __init__(self):
        self.client = cohere.Client(api_key=settings.COHERE_API_KEY)

    def generate_answer(self, question: str, context: str) -> str:
        """Genera una respuesta usando el LLM con el contexto proporcionado."""
        user_message = USER_PROMPT_TEMPLATE.format(
            context=context,
            question=question
        )

        response = self.client.chat(
            model=settings.LLM_MODEL,
            preamble=SYSTEM_PROMPT,
            message=user_message,
            temperature=settings.LLM_TEMPERATURE
        )

        return response.text