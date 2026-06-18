import streamlit as st
import requests

API_URL = "http://localhost:8000/api/v1"

st.title("Challenge RAG - Preguntas y Respuestas")

# Sidebar para gestión de documentos
st.sidebar.header("Gestión de documentos")

# Estado de la API
health = requests.get(f"{API_URL}/health")
if health.status_code == 200:
    data = health.json()
    st.sidebar.metric("Documentos", data["documentos_cargados"])
    st.sidebar.metric("Chunks", data["chunks_totales"])

    if data["documentos"]:
        st.sidebar.write("Archivos cargados:")
        for doc in data["documentos"]:
            st.sidebar.write(f"- {doc}")

# Subir documento
uploaded_file = st.sidebar.file_uploader("Subir documento", type=["docx", "pdf"])
if uploaded_file and st.sidebar.button("Cargar"):
    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
    response = requests.post(f"{API_URL}/documents", files=files)
    if response.status_code == 200:
        st.sidebar.success(response.json()["message"])
        st.rerun()
    else:
        st.sidebar.error(response.json().get("detail", "Error al cargar"))

# Eliminar documento
filename = st.sidebar.text_input("Nombre del archivo a eliminar", placeholder="documento.docx")
if st.sidebar.button("Eliminar"):
    if filename:
        response = requests.delete(f"{API_URL}/documents/{filename}")
        if response.status_code == 200:
            st.sidebar.success(response.json()["message"])
            st.rerun()
        else:
            st.sidebar.error(response.json().get("detail", "No encontrado"))

# Sección principal: preguntas
st.divider()
user_name = st.text_input("Nombre de usuario", placeholder="John Doe")
question = st.text_input("Pregunta", placeholder="¿Quién es Zara?")

if st.button("Preguntar"):
    if not user_name or not question:
        st.warning("Completá ambos campos.")
    else:
        with st.spinner("Buscando respuesta..."):
            response = requests.post(
                f"{API_URL}/ask",
                json={"user_name": user_name, "question": question}
            )
        if response.status_code == 200:
            st.success(response.json()["answer"])
        else:
            st.error(f"Error: {response.json().get('detail', 'Error desconocido')}")