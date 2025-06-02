import os
import sys
import asyncio
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient
from st_social_media_links import SocialMediaIcons

# Configuración de compatibilidad en Windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Ruta absoluta al archivo del servidor FastMCP
ruta_servidor = r"D:\Usuarios\Anaconda 3\MY_MCP_SERVER\server1.py"

# Configuración del cliente MCP para conectarse al servidor local
config = {
    "mcpServers": {
        "mi-servidor-local": {
            "command": "python",
            "args": [ruta_servidor],
            "cwd": os.path.dirname(ruta_servidor)
        }
    }
}

# Inicializar el cliente y el agente MCP
client = MCPClient.from_dict(config)
llm = ChatOpenAI(model="gpt-4o-mini")
agent = MCPAgent(llm=llm, client=client, max_steps=50)

# Interfaz de usuario con Streamlit
st.set_page_config(page_title="Cliente MCP Local", page_icon="🛠️")
st.title("🔧 MCP Server / Data Analysis")

imagen_url = (
    "https://anhanguera.s3.amazonaws.com/wp-content/uploads/"
    "2024/09/capa-homem-com-mao-estendida-04-09-2024-66d8f14be6cc4.webp"
)
st.image(imagen_url, use_container_width=True)

# 🔥 Lista actualizada de herramientas
with st.expander("🔍 Ver herramientas disponibles"):
    st.markdown("""
    ### 📁 Gestión de Archivos
    • **analizar_archivo** - Análisis completo de propiedades
    • **crear_archivo** - Crear archivos con contenido
    • **leer_documento** - Leer texto, PDF con límites configurables
    
    ### 📊 Análisis de Datos  
    • **analizar_datos** - Análisis estadístico completo (antes: resumir_datos)
    • **tabla_dinamica_avanzada** - Tablas dinámicas mejoradas
    • **convertir_formato_datos** - Conversión entre formatos
    
    ### 📈 Visualización
    • **crear_visualizacion** - Sistema unificado de gráficos
    
    ### 🌐 Web y GitHub
    • **buscar_repositorios_github** - Búsqueda avanzada
    • **extraer_contenido_web** - Extracción con selectores CSS
    • **descargar_archivo_web** - Descarga mejorada
    """)

# 🔥 Ejemplos de consultas
with st.expander("💡 Ejemplos de consultas para probar"):
    st.markdown("""
    **📊 Para análisis de datos:**
    - "Analiza el archivo temp_datos.csv y muéstrame las estadísticas"
    - "Crea una tabla dinámica de temp_ventas.csv que muestre ventas totales por región y producto"
    
    **🌐 Para web:**
    - "Busca repositorios de Python para análisis de datos en GitHub"
    - "Extrae el contenido de https://example.com"
    
    **📈 Para visualización:**
    - "Crea un gráfico de barras de mi archivo CSV"
    """)

# Carga de archivos para herramientas que los necesitan
uploaded_file = st.file_uploader("📁 Subir archivo (opcional)", type=['csv', 'xlsx', 'pdf', 'txt'])
if uploaded_file:
    # Guardar archivo temporalmente
    temp_path = f"temp_{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"Archivo guardado como: {temp_path}")

consulta = st.text_input("Ingresa tu consulta:")

if st.button("Enviar") and consulta:
    with st.spinner("Procesando..."):
        try:
            resultado = asyncio.run(agent.run(consulta))
            st.success("✅ Consulta completada.")
            st.write("**Resultado:**")
            
            # visualización de resultados
            if isinstance(resultado, dict):
                st.json(resultado)
            else:
                st.write(resultado)
                
        except Exception as e:
            st.error(f"❌ Error en la consulta: {str(e)}")
            # MEJORA OPCIONAL 4: Más detalles del error en desarrollo
            with st.expander("Ver detalles del error"):
                st.code(str(e))

# Botón para limpiar archivos temporales
if st.button("🗑️ Limpiar archivos temporales"):
    archivos_temp = [f for f in os.listdir('.') if f.startswith('temp_')]
    for archivo in archivos_temp:
        try:
            os.remove(archivo)
            st.success(f"Eliminado: {archivo}")
        except:
            st.warning(f"No se pudo eliminar: {archivo}")

# Pie de página
st.markdown(
    '<div style="text-align: center;">'
    '---<br>'
    '<strong>Desarrollador:</strong> Edwin Quintero Alzate / '
    '<strong>Email:</strong> egqa1975@gmail.com'
    '</div>',
    unsafe_allow_html=True
)
social_media_links = [
    "https://www.facebook.com/edwin.quinteroalzate   ",
    "https://www.linkedin.com/in/edwinquintero0329/   ",
    "https://github.com/Edwin1719   "
]
social_media_icons = SocialMediaIcons(social_media_links)
social_media_icons.render()