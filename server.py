# Servidor MCP Optimizado
from mcp.server.fastmcp import FastMCP
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import httpx
import pandas as pd
import PyPDF2
import plotly.express as px
import plotly.graph_objects as go
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import json

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instancia del servidor
mcp = FastMCP("Demo")

# ========== CLASES AUXILIARES ==========
class FileHandler:
    """Manejador centralizado de archivos"""
    
    @staticmethod
    def validate_file_exists(path: Path) -> None:
        """Valida que el archivo exista"""
        if not path.exists():
            raise FileNotFoundError(f"El archivo {path} no existe")
    
    @staticmethod
    def read_dataframe(path: Path) -> pd.DataFrame:
        """Lee un DataFrame desde CSV o Excel"""
        FileHandler.validate_file_exists(path)
        
        if path.suffix.lower() == ".csv":
            return pd.read_csv(path)
        elif path.suffix.lower() in [".xlsx", ".xls"]:
            return pd.read_excel(path)
        elif path.suffix.lower() == ".json":
            return pd.read_json(path)
        else:
            raise ValueError(f"Formato no soportado: {path.suffix}")
    
    @staticmethod
    def validate_columns(df: pd.DataFrame, columns: List[str]) -> None:
        """Valida que las columnas existan en el DataFrame"""
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Columnas no encontradas: {', '.join(missing_cols)}")

class ResponseFormatter:
    """Formateador estándar de respuestas"""
    
    @staticmethod
    def success(data: Any, message: str = "") -> Dict:
        """Formato de respuesta exitosa"""
        return {
            "success": True,
            "data": data,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def error(error: str, details: str = "") -> Dict:
        """Formato de respuesta de error"""
        return {
            "success": False,
            "error": error,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }

# ========== HERRAMIENTAS BÁSICAS DE ARCHIVOS ==========
@mcp.tool()
def analizar_archivo(archivo: Path) -> Dict:
    """Analiza las propiedades completas de un archivo"""
    try:
        FileHandler.validate_file_exists(Path(archivo))
        path = Path(archivo)
        stat = path.stat()
        
        data = {
            "nombre": path.name,
            "extension": path.suffix,
            "tamaño_bytes": stat.st_size,
            "tamaño_legible": _format_file_size(stat.st_size),
            "fecha_creacion": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "fecha_modificacion": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "es_archivo": path.is_file(),
            "es_directorio": path.is_dir(),
        }
        
        # Si es archivo de texto pequeño, incluir contenido
        if path.is_file() and path.suffix.lower() in ['.txt', '.md', '.py', '.json'] and stat.st_size < 10000:
            try:
                data["contenido_preview"] = path.read_text(encoding="utf-8")[:1000]
            except:
                data["contenido_preview"] = "No se pudo leer el contenido"
        
        return ResponseFormatter.success(data, f"Archivo {path.name} analizado exitosamente")
        
    except Exception as e:
        logger.error(f"Error analizando archivo: {e}")
        return ResponseFormatter.error(str(e))

@mcp.tool()
def crear_archivo(ruta: Path, contenido: str, encoding: str = "utf-8") -> Dict:
    """Crea un archivo con el contenido especificado"""
    try:
        path = Path(ruta)
        # Crear directorio padre si no existe
        path.parent.mkdir(parents=True, exist_ok=True)
        
        path.write_text(contenido, encoding=encoding)
        
        return ResponseFormatter.success(
            {"ruta": str(path), "tamaño": len(contenido.encode(encoding))},
            f"Archivo {path.name} creado exitosamente"
        )
        
    except Exception as e:
        logger.error(f"Error creando archivo: {e}")
        return ResponseFormatter.error(str(e))

# ========== HERRAMIENTAS DE LECTURA DE DOCUMENTOS ==========
@mcp.tool()
def leer_documento(ruta: Path, limite_caracteres: int = 10000) -> Dict:
    """Lee documentos de texto, PDF con límite configurable"""
    try:
        path = Path(ruta)
        FileHandler.validate_file_exists(path)
        
        if path.suffix.lower() == ".pdf":
            contenido = _extract_pdf_text(path)
        elif path.suffix.lower() in [".txt", ".md", ".csv", ".json", ".py"]:
            contenido = path.read_text(encoding="utf-8")
        else:
            raise ValueError(f"Formato no soportado: {path.suffix}")
        
        # Aplicar límite de caracteres
        contenido_limitado = contenido[:limite_caracteres]
        fue_truncado = len(contenido) > limite_caracteres
        
        data = {
            "contenido": contenido_limitado,
            "longitud_total": len(contenido),
            "longitud_retornada": len(contenido_limitado),
            "fue_truncado": fue_truncado
        }
        
        return ResponseFormatter.success(data, f"Documento {path.name} leído exitosamente")
        
    except Exception as e:
        logger.error(f"Error leyendo documento: {e}")
        return ResponseFormatter.error(str(e))

# ========== HERRAMIENTAS DE ANÁLISIS DE DATOS ==========
@mcp.tool()
def analizar_datos(ruta_archivo: Path, incluir_muestra: bool = True) -> Dict:
    """Análisis completo de archivos de datos (CSV/Excel/JSON)"""
    try:
        df = FileHandler.read_dataframe(Path(ruta_archivo))
        
        # Información básica
        info_basica = {
            "filas": len(df),
            "columnas": len(df.columns),
            "lista_columnas": list(df.columns),
            "tipos_datos": df.dtypes.to_dict(),
        }
        
        # Estadísticas descriptivas para columnas numéricas
        numericas = df.select_dtypes(include=['number'])
        estadisticas = {}
        if not numericas.empty:
            estadisticas = numericas.describe().to_dict()
        
        # Información de valores faltantes
        valores_faltantes = df.isnull().sum().to_dict()
        
        # Muestra de datos (opcional)
        muestra = {}
        if incluir_muestra:
            muestra = {
                "primeras_5_filas": df.head().to_dict('records'),
                "ultimas_5_filas": df.tail().to_dict('records')
            }
        
        data = {
            "info_basica": info_basica,
            "estadisticas_numericas": estadisticas,
            "valores_faltantes": valores_faltantes,
            "muestra_datos": muestra
        }
        
        return ResponseFormatter.success(data, f"Análisis de {Path(ruta_archivo).name} completado")
        
    except Exception as e:
        logger.error(f"Error analizando datos: {e}")
        return ResponseFormatter.error(str(e))

@mcp.tool()
def tabla_dinamica_avanzada(
    ruta_archivo: Path,
    index_cols: Union[str, List[str]],
    columns_cols: Union[str, List[str]], 
    values_col: str,
    aggfunc: Union[str, List[str]] = "mean",
    fill_value: Optional[float] = None
) -> Dict:
    """Crea tablas dinámicas avanzadas con múltiples funciones de agregación"""
    try:
        df = FileHandler.read_dataframe(Path(ruta_archivo))
        
        # Normalizar inputs
        if isinstance(index_cols, str):
            index_cols = [index_cols]
        if isinstance(columns_cols, str):
            columns_cols = [columns_cols]
        if isinstance(aggfunc, str):
            aggfunc = [aggfunc]
        
        # Validar columnas
        todas_columnas = index_cols + columns_cols + [values_col]
        FileHandler.validate_columns(df, todas_columnas)
        
        # Validar funciones de agregación
        funciones_validas = ["mean", "sum", "min", "max", "count", "std", "var", "median"]
        funciones_invalidas = [f for f in aggfunc if f not in funciones_validas]
        if funciones_invalidas:
            raise ValueError(f"Funciones no válidas: {funciones_invalidas}. Use: {funciones_validas}")
        
        # Crear tabla dinámica
        pivot_table = df.pivot_table(
            index=index_cols,
            columns=columns_cols,
            values=values_col,
            aggfunc=aggfunc,
            fill_value=fill_value
        )
        
        # Convertir a formato serializable
        if len(aggfunc) == 1:
            resultado = pivot_table.to_dict()
        else:
            resultado = {func: pivot_table[func].to_dict() for func in aggfunc}
        
        data = {
            "tabla_dinamica": resultado,
            "metadata": {
                "index_columnas": index_cols,
                "columnas_pivote": columns_cols,
                "columna_valores": values_col,
                "funciones_agregacion": aggfunc,
                "dimensiones": pivot_table.shape
            }
        }
        
        return ResponseFormatter.success(data, "Tabla dinámica creada exitosamente")
        
    except Exception as e:
        logger.error(f"Error creando tabla dinámica: {e}")
        return ResponseFormatter.error(str(e))

# ========== HERRAMIENTAS DE VISUALIZACIÓN ==========
@mcp.tool()
def crear_visualizacion(
    ruta_archivo: Path,
    tipo_grafico: str,
    configuracion: Dict[str, Any]
) -> Dict:
    """Sistema unificado de visualización con Plotly"""
    try:
        df = FileHandler.read_dataframe(Path(ruta_archivo))
        
        # Validar configuración mínima
        if 'columnas' not in configuracion:
            raise ValueError("Debe especificar 'columnas' en la configuración")
        
        columnas = configuracion['columnas']
        FileHandler.validate_columns(df, columnas)
        
        # Crear figura según tipo
        fig = _create_plotly_figure(df, tipo_grafico, configuracion)
        
        # Personalizar figura
        titulo = configuracion.get('titulo', f'Gráfico {tipo_grafico}')
        fig.update_layout(title=titulo, template=configuracion.get('template', 'plotly'))
        
        # Guardar
        ruta_salida = Path(ruta_archivo).with_suffix('.html')
        fig.write_html(ruta_salida)
        
        data = {
            "archivo_salida": str(ruta_salida),
            "tipo_grafico": tipo_grafico,
            "columnas_utilizadas": columnas
        }
        
        return ResponseFormatter.success(data, f"Visualización {tipo_grafico} creada exitosamente")
        
    except Exception as e:
        logger.error(f"Error creando visualización: {e}")
        return ResponseFormatter.error(str(e))

# ========== HERRAMIENTAS WEB ==========
@mcp.tool()
async def buscar_repositorios_github(
    query: str, 
    sort: str = "stars", 
    order: str = "desc", 
    per_page: int = 10
) -> Dict:
    """Búsqueda avanzada de repositorios en GitHub"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            url = "https://api.github.com/search/repositories"
            params = {
                "q": query,
                "sort": sort,
                "order": order,
                "per_page": min(per_page, 100)  # Límite de API
            }
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data_json = response.json()
            repositorios = []
            
            for repo in data_json.get("items", []):
                repositorios.append({
                    "nombre_completo": repo["full_name"],
                    "descripcion": repo.get("description", "Sin descripción"),
                    "url": repo["html_url"],
                    "estrellas": repo["stargazers_count"],
                    "forks": repo["forks_count"],
                    "lenguaje": repo.get("language", "No especificado"),
                    "actualizado": repo["updated_at"],
                    "temas": repo.get("topics", [])
                })
            
            data = {
                "repositorios": repositorios,
                "total_encontrados": data_json["total_count"],
                "query_utilizada": query
            }
            
            return ResponseFormatter.success(data, f"Se encontraron {len(repositorios)} repositorios")
            
    except Exception as e:
        logger.error(f"Error buscando repositorios: {e}")
        return ResponseFormatter.error(str(e))

@mcp.tool()
async def extraer_contenido_web(url: str, selector_css: Optional[str] = None) -> Dict:
    """Extrae contenido de páginas web con opciones avanzadas"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            if selector_css:
                elementos = soup.select(selector_css)
                contenido = "\n".join([elem.get_text(strip=True) for elem in elementos])
            else:
                contenido = soup.get_text(strip=True)
            
            data = {
                "url": url,
                "contenido": contenido[:10000],  # Límite para evitar respuestas muy grandes
                "longitud_total": len(contenido),
                "titulo": soup.title.string if soup.title else "Sin título",
                "selector_usado": selector_css
            }
            
            return ResponseFormatter.success(data, "Contenido web extraído exitosamente")
            
    except Exception as e:
        logger.error(f"Error extrayendo contenido web: {e}")
        return ResponseFormatter.error(str(e))

@mcp.tool()
async def descargar_archivo_web(url: str, ruta_destino: Path, sobrescribir: bool = False) -> Dict:
    """Descarga archivos desde URLs con validaciones mejoradas"""
    try:
        path = Path(ruta_destino)
        
        # Verificar si el archivo existe
        if path.exists() and not sobrescribir:
            raise FileExistsError(f"El archivo {path} ya existe. Use sobrescribir=True para reemplazarlo")
        
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            # Crear directorio padre si no existe
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Guardar archivo
            path.write_bytes(response.content)
            
            data = {
                "url": url,
                "archivo_destino": str(path),
                "tamaño_bytes": len(response.content),
                "tamaño_legible": _format_file_size(len(response.content)),
                "tipo_contenido": response.headers.get("content-type", "desconocido")
            }
            
            return ResponseFormatter.success(data, "Archivo descargado exitosamente")
            
    except Exception as e:
        logger.error(f"Error descargando archivo: {e}")
        return ResponseFormatter.error(str(e))

# ========== HERRAMIENTAS DE CONVERSIÓN ==========
@mcp.tool()
def convertir_formato_datos(
    archivo_entrada: Path, 
    formato_salida: str,
    opciones: Dict[str, Any] = None
) -> Dict:
    """Conversión mejorada entre formatos de datos"""
    try:
        if opciones is None:
            opciones = {}
            
        df = FileHandler.read_dataframe(Path(archivo_entrada))
        
        # Generar nombre de archivo de salida
        archivo_salida = Path(archivo_entrada).with_suffix(f".{formato_salida}")
        
        # Opciones por defecto para cada formato
        opciones_defecto = {
            "json": {"orient": "records", "indent": 2},
            "csv": {"index": False, "encoding": "utf-8"},
            "xlsx": {"index": False},
            "parquet": {"index": False}
        }
        
        # Combinar opciones
        opts_finales = {**opciones_defecto.get(formato_salida, {}), **opciones}
        
        # Realizar conversión
        if formato_salida == "json":
            df.to_json(archivo_salida, **opts_finales)
        elif formato_salida == "csv":
            df.to_csv(archivo_salida, **opts_finales)
        elif formato_salida == "xlsx":
            df.to_excel(archivo_salida, **opts_finales)
        elif formato_salida == "parquet":
            df.to_parquet(archivo_salida, **opts_finales)
        else:
            formatos_soportados = ["json", "csv", "xlsx", "parquet"]
            raise ValueError(f"Formato '{formato_salida}' no soportado. Use: {formatos_soportados}")
        
        data = {
            "archivo_entrada": str(archivo_entrada),
            "archivo_salida": str(archivo_salida),
            "formato_origen": Path(archivo_entrada).suffix,
            "formato_destino": f".{formato_salida}",
            "filas_procesadas": len(df)
        }
        
        return ResponseFormatter.success(data, f"Conversión a {formato_salida} completada")
        
    except Exception as e:
        logger.error(f"Error en conversión: {e}")
        return ResponseFormatter.error(str(e))

# ========== FUNCIONES AUXILIARES ==========
def _format_file_size(size_bytes: int) -> str:
    """Convierte bytes a formato legible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def _extract_pdf_text(path: Path) -> str:
    """Extrae texto de archivos PDF"""
    with open(path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        return " ".join([page.extract_text() for page in reader.pages])

def _create_plotly_figure(df: pd.DataFrame, tipo: str, config: Dict) -> go.Figure:
    """Crea figuras de Plotly según tipo y configuración"""
    columnas = config['columnas']
    
    if tipo == "bar":
        return px.bar(df, x=columnas[0], y=columnas[1], **config.get('extra_params', {}))
    elif tipo == "line":
        return px.line(df, x=columnas[0], y=columnas[1], **config.get('extra_params', {}))
    elif tipo == "scatter":
        return px.scatter(df, x=columnas[0], y=columnas[1], **config.get('extra_params', {}))
    elif tipo == "pie":
        return px.pie(df, names=columnas[0], values=columnas[1], **config.get('extra_params', {}))
    elif tipo == "histogram":
        return px.histogram(df, x=columnas[0], **config.get('extra_params', {}))
    elif tipo == "box":
        return px.box(df, x=columnas[0], y=columnas[1] if len(columnas) > 1 else None, **config.get('extra_params', {}))
    else:
        tipos_soportados = ["bar", "line", "scatter", "pie", "histogram", "box"]
        raise ValueError(f"Tipo '{tipo}' no soportado. Use: {tipos_soportados}")

# ========== EJECUCIÓN DEL SERVIDOR ==========
if __name__ == "__main__":
    mcp.run(transport="stdio")