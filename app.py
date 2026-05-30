import streamlit as st
import google.generativeai as genai
import requests
import io
from PIL import Image

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Kinetix AI Pro", page_icon="💪", layout="wide")

# 2. CONEXIÓN APIS (Seguridad)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
HF_API_KEY = st.secrets["HF_API_KEY"]

# URL del modelo de imagen gratuito en Hugging Face (Usamos Flux por su alta calidad)
HF_API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

# Función interna para generar la imagen gratis
def generar_imagen_gratis(prompt_texto):
    response = requests.post(HF_API_URL, headers=headers, json={"inputs": prompt_texto})
    if response.status_code == 200:
        return response.content
    else:
        return None

# 3. INICIALIZACIÓN DE ESTADO (MEMORIA DE CHATS)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat Principal"

if st.session_state.current_chat not in st.session_state.chat_history:
    st.session_state.chat_history["Chat Principal"] = []

# 4. BARRA LATERAL (SIDEBAR)
with st.sidebar:
    st.title("🚀 Kinetix Pro")
    
    st.subheader("💬 Mis Conversaciones")
    nuevo_chat_nombre = st.text_input("Nuevo chat:", placeholder="Ej: Dieta Lunes", key="new_chat_input")
    if st.button("➕ Crear Nuevo Chat"):
        if nuevo_chat_nombre and nuevo_chat_nombre not in st.session_state.chat_history:
            st.session_state.chat_history[nuevo_chat_nombre] = []
            st.session_state.current_chat = nuevo_chat_nombre
            st.rerun()

    chat_seleccionado = st.selectbox("Seleccionar chat:", options=list(st.session_state.chat_history.keys()), index=list(st.session_state.chat_history.keys()).index(st.session_state.current_chat))
    if chat_seleccionado != st.session_state.current_chat:
        st.session_state.current_chat = chat_seleccionado
        st.rerun()

    if st.button("🗑️ Eliminar Chat Actual") and len(st.session_state.chat_history) > 1:
        del st.session_state.chat_history[st.session_state.current_chat]
        st.session_state.current_chat = list(st.session_state.chat_history.keys())[0]
        st.rerun()

    st.divider()

    st.subheader("📊 Perfil Biométrico")
    peso = st.number_input("Peso (kg)", 30.0, 250.0, 75.0)
    altura = st.number_input("Altura (m)", 1.0, 2.5, 1.75)
    imc = peso / (altura ** 2)
    st.metric("IMC", f"{imc:.1f}")

    st.subheader("📷 Analizador Visual")
    archivo_foto = st.file_uploader("Sube foto de comida/etiqueta", type=["jpg", "png", "jpeg"])

# 5. CONFIGURACIÓN DEL MODELO IA (Cerebro de Texto)
SYSTEM_PROMPT = f"""Eres Kinetix, una IA de élite. Usuario: {peso}kg, {altura}m (IMC: {imc:.1f}). 
Tienes visión computacional. Si se sube una imagen, analízala con precisión técnica.

REGLAS DE COMPORTAMIENTO:
1. Si el usuario te pide algo fuera de tu área (salud, deporte, nutrición), responde cortésmente: "Como Kinetix, mi enfoque es tu rendimiento físico y salud. Mantengamos el enfoque en tus objetivos."
2. Nunca rompas tu identidad de experto.
"""

available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
target_model = "models/gemini-1.5-flash" if "models/gemini-1.5-flash" in available_models else available_models[0]
model = genai.GenerativeModel(target_model, system_instruction=SYSTEM_PROMPT)

# 6. PANTALLA PRINCIPAL DE CHAT
st.title(f"💪 {st.session_state.current_chat}")

# Mostrar historial
for message in st.session_state.chat_history[st.session_state.current_chat]:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], bytes):
            st.image(Image.open(io.BytesIO(message["content"])))
        else:
            st.markdown(message["content"])

# Entrada del usuario
if prompt := st.chat_input("Escribe a Kinetix..."):
    st.session_state.chat_history[st.session_state.current_chat].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # ¿El usuario quiere un dibujo?
        if prompt.lower().startswith(("dibuja", "genera", "haz una imagen", "crea una imagen")):
            with st.spinner("🎨 Kinetix está dibujando tu imagen gratis..."):
                bytes_imagen = generar_imagen_gratis(prompt)
                if bytes_imagen:
                    st.image(Image.open(io.BytesIO(bytes_imagen)))
                    st.session_state.chat_history[st.session_state.current_chat].append({"role": "assistant", "content": bytes_imagen})
                else:
                    st.error("❌ El servidor de dibujo está saturado o la llave es incorrecta. Inténtalo en unos segundos.")
        else:
            # Flujo normal de conversación con Gemini
            with st.spinner("Kinetix pensando..."):
                try:
                    if archivo_foto:
                        img = Image.open(archivo_foto)
                        response = model.generate_content([prompt, img])
                    else:
                        response = model.generate_content(st.session_state.chat_history[st.session_state.current_chat][-10:])
                    
                    if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                        texto_respuesta = "⚠️ Consulta fuera de contexto. Mantengamos el enfoque en tu salud."
                    elif not response.text:
                        texto_respuesta = "⚠️ Recibí una respuesta vacía. Por favor formula tu pregunta sobre fitness."
                    else:
                        texto_respuesta = response.text
                    
                    st.markdown(texto_respuesta)
                    st.session_state.chat_history[st.session_state.current_chat].append({"role": "assistant", "content": texto_respuesta})
                except Exception as e:
                    st.error("🔒 Hubo un problema con la consulta. Por favor, asegúrate de que tu GOOGLE_API_KEY en los Secrets sea la correcta.")

if archivo_foto:
    st.sidebar.success("📸 Imagen lista para análisis.")
