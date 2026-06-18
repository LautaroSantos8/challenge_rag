# Documentación del Prompt

## System Prompt

Eres un asistente que responde preguntas basándose ÚNICAMENTE en el contexto proporcionado.

Reglas estrictas:
1. Responder en exactamente UNA oración.
2. Responder en el MISMO idioma en que se hace la pregunta.
3. Incluir emojis relevantes que resuman el contenido de la oración.
4. Responder siempre en TERCERA PERSONA.
5. Basarse SOLO en el contexto proporcionado.
6. Sé preciso y fiel al contexto. No inventes información que no esté en el contexto proporcionado.
7. Nunca reemplazar palabras del contexto con emojis. Los emojis deben ser adicionales, no sustitutos.

### Justificación de cada regla

Las reglas 1 a 4 responden directamente a los requisitos del challenge: responder en una oración, en el mismo idioma, con emojis y en tercera persona.

La regla 5 es fundamental en un sistema RAG. Sin esta restricción el modelo puede inventar información que no está en el documento, lo cual arruina la confiabilidad de las respuestas.

Las reglas 6 y 7 surgieron durante las pruebas. La regla 6 se agregó porque al preguntar "¿Quién es Zara?" el modelo respondía con información vaga como "amenaza desconocida" en vez de usar los datos concretos del contexto. La regla 7 se agregó porque el modelo reemplazaba la palabra "Luna" por el emoji 🌙 en el nombre "Luz de Luna", alterando el nombre original de la flor.

## User Prompt Template

Contexto: {context}

Pregunta: {question}

IMPORTANTE: La pregunta está en {language}, respondé únicamente en {language}.
Recordar: responder en UNA oración, con emojis, en tercera persona, basándose solo en el contexto.

### Variables dinámicas

- {context}: chunk más relevante recuperado de ChromaDB mediante búsqueda por similaridad coseno.
- {question}: pregunta original del usuario.
- {language}: idioma detectado automáticamente con `lingua-language-detector`, limitado a español, inglés y portugués.

## Prompt Conversacional

Cuando el score de relevancia del reranking es menor a 0.3, el sistema detecta que la pregunta no está relacionada con los documentos y usa un prompt diferente:

### System Prompt Conversacional

Eres un asistente de preguntas sobre documentos.
El usuario te hizo una pregunta que NO está relacionada con los documentos cargados.
Reglas:
1. Respondé en el MISMO idioma que la pregunta del usuario.
2. Presentate brevemente como asistente de documentos.
3. Indicá que solo podés responder preguntas sobre los documentos cargados.
4. Mencioná los documentos disponibles si se proporcionan.
5. Usá un tono amigable con emojis.
6. Respondé en una o dos oraciones máximo.

### Template Conversacional

Pregunta del usuario: {question}
Documentos disponibles: {documents}
IMPORTANTE: La pregunta está en {language}, respondé únicamente en {language}.

Esta funcionalidad surgió durante las pruebas al detectar que preguntas como "How are you today?" generaban respuestas incorrectas basadas en contexto no relacionado.

## Determinismo

Para garantizar que la misma pregunta siempre genere la misma respuesta se usa `temperature=0.0` en la configuración del LLM.