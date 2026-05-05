import streamlit as st
from openai import OpenAI
import streamlit.components.v1 as components

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="📐 Mateo IA | Matemáticas",
    page_icon="📐",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

# CSS ESENCIAL
css_mateo = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stDecoration"] {display: none;}
    .stApp {max-width: 100%; padding: 0;}
    .stDeployButton {display: none;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stStatusWidget"] {display: none;}
</style>
"""
st.markdown(css_mateo, unsafe_allow_html=True)

# PERSONALIDAD DE MATEO IA - ESPECIALISTA EN MATEMÁTICAS
SYSTEM_PROMPT = """Eres Mateo IA, un asistente de inteligencia artificial especializado en MATEMÁTICAS. Tu símbolo es un compás y una escuadra, representando la precisión y el razonamiento lógico.

Tu objetivo principal es ayudar a estudiantes a comprender conceptos matemáticos, resolver problemas paso a paso, y desarrollar pensamiento matemático.

**REGLAS FUNDAMENTALES:**
1.  **Advertencia Inicial Obligatoria:** En tu primer mensaje de bienvenida, debes aclarar: "¡Hola! Soy Mateo IA, tu asistente en matemáticas. Recuerda que soy una herramienta de apoyo al aprendizaje. Es importante que intentes resolver los problemas por ti mismo primero. Mis explicaciones te guiarán, pero el verdadero aprendizaje viene con la práctica personal."
2.  **Tono:** Paciente, didáctico y motivador. Usa un lenguaje claro y accesible para estudiantes.
3.  **Metodología:** Explica los conceptos paso a paso, muestra procedimientos claros, y cuando sea posible, ofrece ejemplos similares para practicar.
4.  **Áreas de Especialización:** Álgebra, geometría, cálculo, trigonometría, estadística, aritmética, y matemáticas en general desde nivel básico hasta avanzado.

**ESTILO DE RESPUESTA:**
- Comienza validando la pregunta del usuario.
- Desglosa el problema en pasos lógicos.
- Usa notación matemática clara cuando sea necesario.
- Ofrece tips o trucos de aprendizaje.
- Si la pregunta no es de matemáticas, amablemente redirige al tema.

Responde de forma concisa pero completa. ¡Tú puedes con las matemáticas!
"""

# INTERFAZ PRINCIPAL
st.title("📐 Mateo IA")
st.caption("Especialista en Matemáticas | Explicaciones paso a paso")

# CONEXIÓN CON GROQ
try:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=st.secrets["groq"]["api_key"]
    )
except Exception:
    st.error("❌ Error de configuración: Revisa los 'Secrets' en Streamlit Cloud.")
    st.stop()

# --- FUNCIÓN DE VOZ (TEXT-TO-SPEECH) ---
def speak_js(text):
    """Inyecta JavaScript para hablar."""
    clean_text = text.replace("'", "\\'").replace('"', '\\"').replace("\n", " ")
    js_code = f"""
    <div id="audio-trigger"></div>
    <script>
        var text = "{clean_text}";
        function hablar() {{
            if ('speechSynthesis' in window) {{
                var utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'es-MX';
                utterance.rate = 1.0;
                window.speechSynthesis.cancel();
                window.speechSynthesis.speak(utterance);
            }}
        }}
        setTimeout(hablar, 100);
    </script>
    """
    components.html(js_code, height=0)

# HISTORIAL DE CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_response" not in st.session_state:
    st.session_state.last_response = ""

# Mostrar historial
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# FUNCIÓN PARA PROCESAR RESPUESTA
def procesar_respuesta(user_input):
    # Muestra mensaje del usuario
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Genera respuesta
    with st.chat_message("assistant"):
        try:
            mensajes_api = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages
            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=mensajes_api,
                stream=True,
            )
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.last_response = response
        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")

# --- INTERFAZ DE USUARIO ---

# 1. Entrada de Texto
if prompt := st.chat_input("Escribe tu problema o duda matemática..."):
    procesar_respuesta(prompt)

# 2. Botón para escuchar la última respuesta
if st.session_state.last_response:
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔊 Escuchar última respuesta", use_container_width=True):
            speak_js(st.session_state.last_response)
