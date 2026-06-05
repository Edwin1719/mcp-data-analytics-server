import os
import sys
import asyncio
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient
from st_social_media_links import SocialMediaIcons

# ==================================================
# CONFIGURACIÓN WINDOWS
# ==================================================
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# ==================================================
# VARIABLES DE ENTORNO
# ==================================================
load_dotenv()

key = os.getenv("OPENAI_API_KEY")

# ==================================================
# CONFIGURACIÓN STREAMLIT
# ==================================================
st.set_page_config(
    page_title="MCP Data Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# CONFIGURACIÓN MCP SERVER
# ==================================================
ruta_servidor = r"C:\Users\EdwinQuintero\Documents\Anaconda 3\mcp-data-analytics-server\server.py"

config = {
    "mcpServers": {
        "mi-servidor-local": {
            "command": "python",
            "args": [ruta_servidor],
            "cwd": os.path.dirname(ruta_servidor)
        }
    }
}

# ==================================================
# INICIALIZAR CLIENTE MCP Y LLM
# ==================================================
client = MCPClient.from_dict(config)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

agent = MCPAgent(
    llm=llm,
    client=client,
    max_steps=50
)

# ==================================================
# SIDEBAR
# ==================================================
with st.sidebar:

    st.title("⚙️ Sistema")

    st.subheader("Estado General")

    if key:
        st.success("✅ OpenAI Conectado")
    else:
        st.error("❌ OpenAI API Key no encontrada")

    if os.path.exists(ruta_servidor):
        st.success("✅ MCP Server Detectado")
    else:
        st.error("❌ MCP Server No Encontrado")

    st.info("🤖 Modelo: GPT-4o-mini")

    st.divider()

    st.subheader("📁 Gestión de Archivos")

    uploaded_file = st.file_uploader(
        "Subir archivo",
        type=["csv", "xlsx", "pdf", "txt"]
    )

    if uploaded_file:

        temp_path = f"temp_{uploaded_file.name}"

        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success("Archivo cargado")

        st.caption(temp_path)

    st.divider()

    st.subheader("🛠 Herramientas Disponibles")

    st.markdown("""
    **📁 Archivos**
    - analizar_archivo
    - crear_archivo
    - leer_documento

    **📊 Datos**
    - analizar_datos
    - tabla_dinamica_avanzada
    - convertir_formato_datos

    **📈 Visualización**
    - crear_visualizacion

    **🌐 Web**
    - buscar_repositorios_github
    - extraer_contenido_web
    - descargar_archivo_web
    """)

    st.divider()

    st.subheader("📊 Estadísticas")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Tools", "10")

    with col2:
        st.metric("LLM", "GPT-4o")

# ==================================================
# CONTENIDO PRINCIPAL
# ==================================================
st.title("📊 MCP Data Analytics Platform")

st.caption(
    "Plataforma Inteligente de Análisis de Datos impulsada por MCP, FastMCP y OpenAI"
)

imagen_url = (
    "https://anhanguera.s3.amazonaws.com/wp-content/uploads/"
    "2024/09/capa-homem-com-mao-estendida-04-09-2024-66d8f14be6cc4.webp"
)

st.image(imagen_url, width="stretch")

# ==================================================
# EJEMPLOS
# ==================================================
with st.expander("💡 Ejemplos de consultas para probar"):

    st.markdown("""
### 📊 Análisis de Datos

- Analiza el archivo temp_datos.csv y muéstrame estadísticas
- Resume el archivo CSV cargado

### 📈 Visualización

- Crea un gráfico de barras del archivo cargado
- Genera un histograma de las ventas

### 🌐 GitHub

- Busca repositorios de Python para análisis de datos
- Busca repositorios de IA generativa

### 📄 Documentos

- Lee el PDF cargado
- Resume el contenido del documento
""")

# ==================================================
# CONSULTA PRINCIPAL
# ==================================================
st.subheader("💬 Consulta Inteligente")

consulta = st.text_area(
    "Ingresa tu consulta",
    height=120,
    placeholder="Ejemplo: Busca repositorios de Python para análisis de datos"
)

col1, col2 = st.columns([1, 1])

with col1:

    ejecutar = st.button(
        "🚀 Ejecutar Consulta",
        use_container_width=True
    )

with col2:

    limpiar = st.button(
        "🗑️ Limpiar Temporales",
        use_container_width=True
    )

# ==================================================
# EJECUCIÓN DEL AGENTE
# ==================================================
if ejecutar and consulta:

    with st.spinner("Procesando consulta..."):

        try:

            resultado = asyncio.run(agent.run(consulta))

            st.success("✅ Consulta completada")

            st.subheader("Resultado")

            if isinstance(resultado, dict):
                st.json(resultado)
            else:
                st.write(resultado)

        except Exception as e:

            st.error(f"❌ Error: {str(e)}")

            with st.expander("Ver detalles técnicos"):
                st.code(str(e))

# ==================================================
# LIMPIAR ARCHIVOS TEMPORALES
# ==================================================
if limpiar:

    archivos_temp = [
        f for f in os.listdir(".")
        if f.startswith("temp_")
    ]

    if not archivos_temp:
        st.info("No existen archivos temporales")

    for archivo in archivos_temp:

        try:
            os.remove(archivo)
            st.success(f"Eliminado: {archivo}")

        except Exception:
            st.warning(f"No se pudo eliminar: {archivo}")

# ==================================================
# FOOTER
# ==================================================
st.markdown("---")

st.markdown(
    """
    <div style="text-align:center">
        <strong>Desarrollador:</strong> Edwin Quintero Alzate<br>
        <strong>Email:</strong> egqa1975@gmail.com
    </div>
    """,
    unsafe_allow_html=True
)

social_media_links = [
    "https://www.facebook.com/edwin.quinteroalzate",
    "https://www.linkedin.com/in/edwinquintero0329/",
    "https://github.com/Edwin1719"
]

social_media_icons = SocialMediaIcons(
    social_media_links
)

social_media_icons.render()