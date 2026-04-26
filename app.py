import streamlit as st
import google.generativeai as genai

# Configuración de la página
st.set_page_config(page_title="kinetix AI", page_icon="⚖️")
st.title("⚖️ kinetix: Tu Coach de Salud")
st.subheader("Bienvenido. ¿En que te puedo ayudar el dia de hoy?")
# Recuperar la API Key de los secretos de Streamlit
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Aquí pegas el prompt que creamos antes
SYSTEM_PROMPT = """Actúa como Vitalis, experta en nutrición y fitness... (todo el prompt de antes)"""

model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=SYSTEM_PROMPT)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar el historial de chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada del usuario
if prompt := st.chat_input("¿En qué puedo ayudarte hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = model.generate_content(prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
