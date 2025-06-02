# 🔧 MCP Data Analytics Server

![texto del vínculo](https://camo.githubusercontent.com/58b51da4887fd84007572883d81033edf32743eff1e6947173054487c627a953/68747470733a2f2f6173736574732e706963616f732e636f6d2f6769742f706963612d6d63702e706e67)

> Servidor MCP para análisis de datos con interfaz Streamlit

Un servidor de análisis de datos construido con FastMCP que proporciona herramientas para procesamiento, análisis y visualización de datos, con una interfaz web intuitiva.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Características

- 📁 **Gestión de Archivos**: Análisis, creación y lectura de documentos
- 📊 **Análisis de Datos**: Estadísticas, tablas dinámicas, detección de tipos
- 📈 **Visualización**: Gráficos interactivos con Plotly
- 🌐 **Web Tools**: Búsqueda GitHub, web scraping, descarga de archivos
- 🔄 **Conversión**: Entre formatos CSV, JSON, Excel, Parquet

## 🚀 Instalación

### 1. Clonar repositorio
```bash
git clone https://github.com/Edwin1719/mcp-data-analytics-server.git
cd mcp-data-analytics-server

2. Instalar dependencias
pip install -r requirements.txt

3. Configurar API key
cp .env.example .env
# Editar .env y agregar tu OPENAI_API_KEY

4. Ejecutar
# Terminal 1: Servidor MCP
python server.py

# Terminal 2: Cliente Streamlit  
streamlit run app.py

Abrir navegador en: http://localhost:8501

📋 Herramientas Disponibles

- analizar_archivo: Análisis completo de propiedades de archivos
- crear_archivo: Creación de archivos con contenido
- leer_documento: Lectura de PDFs, TXT, CSV con límites
- analizar_datos: Análisis estadístico de datasets
- tabla_dinamica_avanzada: Tablas dinámicas con agregaciones
- crear_visualizacion: Gráficos con Plotly (barras, líneas, etc.)
- buscar_repositorios_github: Búsqueda avanzada en GitHub
- extraer_contenido_web: Web scraping con selectores CSS
- descargar_archivo_web: Descarga de archivos desde URLs
- convertir_formato_datos: Conversión entre formatos

💡 Ejemplos de Uso:
"Analiza el archivo ventas.csv y muéstrame las estadísticas"
"Crea un gráfico de barras de las ventas por mes"
"Busca repositorios de Python para análisis de datos"
"Convierte mi archivo Excel a JSON".

📋 Requisitos

* Python 3.8+
* OpenAI API Key
* Dependencias en requirements.txt

👨‍💻 Autor
Edwin Quintero Alzate

📧 egqa1975@gmail.com
🔗 LinkedIn
🐱 GitHub

📄 Licencia
MIT License - ver archivo LICENSE
