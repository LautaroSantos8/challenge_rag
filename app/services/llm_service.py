import cohere
from app.config import settings
import logging

logger = logging.getLogger(__name__)

from lingua import Language, LanguageDetectorBuilder

# Construir el detector solo con los 3 idiomas que necesitamos
detector = LanguageDetectorBuilder.from_languages(
    Language.SPANISH, Language.ENGLISH, Language.PORTUGUESE
).build()

LANGUAGE_MAP = {
    Language.SPANISH: "español",
    Language.ENGLISH: "inglés",
    Language.PORTUGUESE: "portugués"
}

SYSTEM_PROMPT = """Eres un asistente que responde preguntas basándose ÚNICAMENTE en el contexto proporcionado.

Reglas estrictas:
1. Responder en exactamente UNA oración.
2. Responder en el MISMO idioma en que se hace la pregunta.
3. Incluir emojis relevantes que resuman el contenido de la oración.
4. Responder siempre en TERCERA PERSONA.
5. Basarse SOLO en el contexto proporcionado.
6. Sé preciso y fiel al contexto. No inventes información que no esté en el contexto proporcionado.
7. Nunca reemplazar palabras del contexto con emojis. Los emojis deben ser adicionales, no sustitutos."""

USER_PROMPT_TEMPLATE = """Contexto: {context}

Pregunta: {question}

IMPORTANTE: La pregunta está en {language}, respondé únicamente en {language}.
Recordar: responder en UNA oración, con emojis, en tercera persona, basándose solo en el contexto."""

CONVERSATION_PROMPT = """Eres un asistente de preguntas sobre documentos. 
El usuario te hizo una pregunta que NO está relacionada con los documentos cargados.

Reglas:
1. Respondé en el MISMO idioma que la pregunta del usuario.
2. Presentate brevemente como asistente de documentos.
3. Indicá que solo podés responder preguntas sobre los documentos cargados.
4. Mencioná los documentos disponibles si se proporcionan.
5. Usá un tono amigable con emojis.
6. Respondé en una o dos oraciones máximo."""

CONVERSATION_TEMPLATE = """Pregunta del usuario: {question}
Documentos disponibles: {documents}

IMPORTANTE: La pregunta está en {language}, respondé únicamente en {language}."""


class LLMService:
    """Servicio para interactuar con el LLM de Cohere."""

    def __init__(self):
        self.client = cohere.Client(api_key=settings.COHERE_API_KEY)

    def generate_answer(self, question: str, context: str) -> str:
        detected = detector.detect_language_of(question)
        language = LANGUAGE_MAP.get(detected, "español")
        logger.debug(f"Idioma detectado: {detected} -> {language}")

        user_message = USER_PROMPT_TEMPLATE.format(
            context=context,
            question=question,
            language=language
        )

        response = self.client.chat(
            model=settings.LLM_MODEL,
            preamble=SYSTEM_PROMPT,
            message=user_message,
            temperature=settings.LLM_TEMPERATURE
        )

        return response.text

    def generate_conversation(self, question: str, documents: list[str]) -> str:
        detected = detector.detect_language_of(question)
        language = LANGUAGE_MAP.get(detected, "español")
        doc_list = ", ".join(documents) if documents else "ninguno"

        user_message = CONVERSATION_TEMPLATE.format(
            question=question,
            documents=doc_list,
            language=language
        )

        response = self.client.chat(
            model=settings.LLM_MODEL,
            preamble=CONVERSATION_PROMPT,
            message=user_message,
            temperature=settings.LLM_TEMPERATURE
        )

        return response.text