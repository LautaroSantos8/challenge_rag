# Challenge RAG - API de Preguntas y Respuestas

Sistema RAG que permite hacer preguntas sobre documentos utilizando Cohere como LLM y ChromaDB como base de datos vectorial.

## Arquitectura

    challenge_rag/
    ├── app/
    │   ├── main.py                  # App FastAPI con carga automática
    │   ├── config.py                # Configuración desde .env
    │   ├── api/
    │   │   └── routes.py            # Endpoints de la API
    │   ├── models/
    │   │   └── schemas.py           # Schemas request/response
    │   ├── services/
    │   │   ├── rag_service.py       # Orquestador del pipeline RAG
    │   │   ├── llm_service.py       # Integración con Cohere y prompts
    │   │   └── document_reader.py   # Lector de .docx y .pdf
    │   └── db/
    │       └── vector_store.py      # ChromaDB con persistencia
    ├── data/                        # Documentos fuente
    ├── frontend.py                  # Frontend Streamlit
    ├── Dockerfile                   # Contenedor de la API
    ├── Dockerfile.frontend          # Contenedor del frontend
    ├── docker-compose.yml           # Orquestación de servicios
    ├── postman_collection.json      # Colección para pruebas
    ├── PROMPT.md                    # Documentación del prompt
    ├── requirements.txt
    └── run.py

## Requisitos previos

- Python 3.10+
- Cuenta en [Cohere](https://dashboard.cohere.com/api-keys) (tier gratuito)
- Docker (opcional, para ejecución con contenedores)

## Instalación local

1. Clonar el repositorio
```bash
git clone https://github.com/LautaroSantos8/challenge_rag.git
cd challenge_rag
```

2. Crear y activar el ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instalar dependencias
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno
```bash
# Editar .env con tu COHERE_API_KEY
cp .env.example .env
```

5. Ejecutar la API
```bash
python run.py
```

La API estará disponible en http://localhost:8000/docs

6. Ejecutar el frontend (opcional, en otra terminal)
```bash
streamlit run frontend.py
```

El frontend estará disponible en http://localhost:8501

## Ejecución con Docker

```bash
docker compose up --build
```

Esto levanta la API en http://localhost:8000 y el frontend en http://localhost:8501.

Requiere configurar la variable `COHERE_API_KEY` en el archivo `.env`.

## Endpoints

### POST /api/v1/ask
Realiza una pregunta sobre los documentos cargados.
```json
{
    "user_name": "John Doe",
    "question": "¿Quién es Zara?"
}
```

### GET /api/v1/health
Verifica el estado de la API y los documentos cargados.

### POST /api/v1/documents
Sube un documento (.docx o .pdf) para procesarlo en la base de datos vectorial.

### DELETE /api/v1/documents/{filename}
Elimina un documento y todos sus chunks asociados.

## Pruebas con Postman

Importar el archivo `postman_collection.json` en Postman.

## Decisiones técnicas

### Chunking
Se decidió utilizar `RecursiveCharacterTextSplitter` con `chunk_size=500` y `chunk_overlap=50`. Los separadores son jerárquicos: primero por párrafo, luego por salto de línea, y finalmente por oración. El tamaño de 500 se eligió para que cada párrafo del documento quede en un solo chunk sin perder coherencia semántica.

### Embeddings
Se usa `embed-multilingual-v3.0` de Cohere, que soporta español, inglés y portugués nativamente. El encoding se hace explícitamente tanto para los documentos como para las consultas.

### Reranking
Después de recuperar los 3 chunks más similares de ChromaDB, se usa `Cohere Rerank` para reordenar por relevancia real. Esto mejora la precisión del retrieval ya que el reranker analiza la relación pregunta-documento con más detalle que la similaridad coseno.

### Detección de idioma
Se usa `lingua-language-detector` porque es más preciso con textos cortos. El detector está limitado a español, inglés y portugués para mayor precisión.

### Determinismo
Se usa `temperature=0.0` en las llamadas al LLM para garantizar que la misma pregunta siempre genere la misma respuesta.

### Caché
Las respuestas se almacenan en un diccionario en memoria con la pregunta normalizada como clave. Esto evita llamadas repetidas a la API de Cohere, reduciendo costos y latencia. El caché tiene un límite configurable para evitar consumo excesivo de memoria.

### Preguntas fuera de contexto
Se utiliza el score de relevancia del reranking. Si el score es menor a 0.3, el sistema detecta que la pregunta no está relacionada con los documentos y responde conversacionalmente, indicando qué documentos tiene disponibles.

### Persistencia
ChromaDB usa `PersistentClient` para almacenar los embeddings en disco. Los IDs de los chunks son determinísticos (`archivo_chunk_0`) para evitar duplicados al recargar documentos.

## Stack tecnológico

- FastAPI - Framework web con documentación automática en Swagger
- Cohere - LLM (command-r-plus-08-2024), embeddings (embed-multilingual-v3.0) y reranking (rerank-v3.5)
- ChromaDB - Base de datos vectorial con persistencia
- LangChain - Text splitter para chunking
- Lingua - Detección de idioma
- Streamlit - Frontend para interacción visual
- Docker - Contenedorización de la API y frontend
