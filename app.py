import streamlit as st
import google.generativeai as genai

# 1. Configuración Profesional de la Página
st.set_page_config(
    page_title="Kinetix AI",
    page_icon="💪",
    layout="wide" # Esto usa todo el ancho de la pantalla
)

# 2. Configuración de la API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 3. BARRA LATERAL (Panel de Control Pro)
with st.sidebar:
    st.title("📊 Panel Kinetix")
    st.write("Configura tus datos base:")
    
    # Entradas de datos
    peso = st.number_input("Peso actual (kg)", min_value=30.0, max_value=250.0, value=75.0, step=0.1)
    altura = st.number_input("Altura (m)", min_value=1.0, max_value=2.5, value=1.70, step=0.01)
    edad = st.number_input("Edad", min_value=5, max_value=100, value=25)
    
    # Cálculo automático de IMC en la barra lateral
    imc = peso / (altura ** 2)
    st.divider()
    st.metric(label="Tu IMC", value=f"{imc:.1f}")
    
    if imc < 18.5: st.warning("Bajo peso")
    elif 18.5 <= imc < 25: st.success("Rango Saludable")
    elif 25 <= imc < 30: st.info("Sobrepeso")
    else: st.error("Obesidad")
    
    st.info(f"Datos enviados a Kinetix para cálculos precisos.")

# 4. PROMPT DE IDENTIDAD (El Cerebro)
SYSTEM_PROMPT = f"""
Eres Kinetix, una IA de élite experta en Nutrición y Ciencias del Deporte. 
Tu usuario actual tiene estos datos: Peso {peso}kg, Altura {altura}m, Edad {edad} años (IMC: {imc:.1f}).
Usa estos datos siempre que el usuario pregunte por calorías, dietas o ejercicios.
Sé conciso, técnico y motivador. No des información de relleno.
"""

# 5. Inicialización del Modelo
# Usamos el buscador automático para evitar el error 404
available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
target_model = "models/gemini-1.5-flash" if "models/gemini-1.5-flash" in available_models else available_models[0]
model = genai.GenerativeModel(target_model, system_instruction=SYSTEM_PROMPT)

# 6. Lógica del Chat
st.title("💪 Kinetix: Performance AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de usuario
if prompt := st.chat_input("¿Cuál es el plan de hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Enviamos el historial completo para que tenga memoria
        response = model.generate_content(prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
