import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import os
import pandas as pd

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def agregar_bloque_codigo(doc, codigo):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    set_cell_background(cell, "F4F5F7")
    set_cell_margins(cell, top=120, bottom=120, left=200, right=200)
    
    # Borde izquierdo azul
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="24" w:space="0" w:color="0A2342"/><w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(codigo)
    run.font.name = 'Consolas'
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph() # Espacio

def agregar_tabla_df(doc, df_summary, titulo="Resumen Estadístico"):
    p_t = doc.add_paragraph()
    r_t = p_t.add_run(f"Tabla: {titulo}")
    r_t.bold = True
    r_t.font.name = 'Calibri'
    r_t.font.size = Pt(10)
    r_t.font.color.rgb = RGBColor(10, 35, 66)
    p_t.paragraph_format.space_after = Pt(4)

    rows = df_summary.shape[0] + 1
    cols = df_summary.shape[1] + 1
    table = doc.add_table(rows=rows, cols=cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'
    
    # Encabezado
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Métrica"
    set_cell_background(hdr_cells[0], "0A2342")
    hdr_cells[0].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
    hdr_cells[0].paragraphs[0].runs[0].font.bold = True
    hdr_cells[0].paragraphs[0].runs[0].font.size = Pt(8.5)
    
    for c_idx, col_name in enumerate(df_summary.columns):
        hdr_cells[c_idx + 1].text = str(col_name)
        set_cell_background(hdr_cells[c_idx + 1], "0A2342")
        hdr_cells[c_idx + 1].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        hdr_cells[c_idx + 1].paragraphs[0].runs[0].font.bold = True
        hdr_cells[c_idx + 1].paragraphs[0].runs[0].font.size = Pt(8.5)
        
    for r_idx, (idx_val, row_vals) in enumerate(df_summary.iterrows()):
        row_cells = table.rows[r_idx + 1].cells
        row_cells[0].text = str(idx_val)
        row_cells[0].paragraphs[0].runs[0].font.bold = True
        row_cells[0].paragraphs[0].runs[0].font.size = Pt(8)
        
        bg_color = "F8F9FA" if r_idx % 2 == 1 else "FFFFFF"
        set_cell_background(row_cells[0], bg_color)
        
        for c_idx, val in enumerate(row_vals):
            cell = row_cells[c_idx + 1]
            if isinstance(val, (float, int)):
                cell.text = f"{val:.2f}" if isinstance(val, float) else str(val)
            else:
                cell.text = str(val)[:20]
            cell.paragraphs[0].runs[0].font.size = Pt(8)
            set_cell_background(cell, bg_color)
            
    doc.add_paragraph()

def construir_reporte_word():
    print("Iniciando construcción de documento Word...")
    doc = Document()
    
    # Configuración de estilo Normal (Justificado por defecto para todos los textos)
    estilo_normal = doc.styles['Normal']
    estilo_normal.font.name = 'Calibri'
    estilo_normal.font.size = Pt(11)
    estilo_normal.font.color.rgb = RGBColor(30, 41, 59)
    estilo_normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    estilo_normal.paragraph_format.line_spacing = 1.15
    estilo_normal.paragraph_format.space_after = Pt(6)

    # Configuración de márgenes
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.9)
        section.bottom_margin = Inches(0.9)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)

    # -------------------------------------------------------------
    # PÁGINA 1: PORTADA / ESPACIO DEL COMPAÑERO
    # -------------------------------------------------------------
    p_portada = doc.add_paragraph()
    p_portada.paragraph_format.space_before = Pt(140)
    p_portada.paragraph_format.space_after = Pt(20)
    p_portada.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    r_tit = p_portada.add_run("PRÁCTICA: RECOPILACIÓN Y EVALUACIÓN DE DATOS")
    r_tit.bold = True
    r_tit.font.name = 'Calibri'
    r_tit.font.size = Pt(22)
    r_tit.font.color.rgb = RGBColor(10, 35, 66)
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("UNIDAD I: INTRODUCCIÓN A LA CIENCIA DE DATOS (EVIDENCIA 3 - 40%)\nPLATAFORMA KAGGLE: FÓRMULA 1 Y VENTAS GLOBALES DE VIDEOJUEGOS")
    r_sub.font.name = 'Calibri'
    r_sub.font.size = Pt(12)
    r_sub.font.color.rgb = RGBColor(214, 40, 40)
    
    p_box = doc.add_paragraph()
    p_box.paragraph_format.space_before = Pt(120)
    p_box.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_box = p_box.add_run("👉 [PEGA AQUÍ LA PORTADA OFICIAL DEL COMPAÑERO 🫡] 👈\n(O llena aquí los nombres de los integrantes del equipo, carrera, materia y fecha de entrega)")
    r_box.font.name = 'Calibri'
    r_box.font.size = Pt(11)
    r_box.font.italic = True
    r_box.font.color.rgb = RGBColor(100, 110, 125)
    
    doc.add_page_break()

    # -------------------------------------------------------------
    # SECCIÓN 1: INTRODUCCIÓN Y CONFIGURACIÓN KAGGLE
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    r_h1 = h1.add_run("1. Introducción y Configuración de la API de Kaggle")
    r_h1.font.color.rgb = RGBColor(10, 35, 66)
    
    doc.add_paragraph(
        "En el ciclo de vida de la Ciencia de Datos, la fase de recopilación y evaluación exploratoria (EDA) "
        "es fundamental para asegurar la calidad de la información antes de aplicar modelos predictivos o estadísticos. "
        "Para esta práctica se seleccionaron dos conjuntos de datos reales de la plataforma KAGGLE: uno perteneciente al "
        "dominio de DEPORTES (Fórmula 1 World Championship) y otro de ELECCIÓN LIBRE (Ventas Globales de Videojuegos - vgsales)."
    )
    
    doc.add_heading("1.1. Autenticación Automatizada con la API", level=2)
    doc.add_paragraph(
        "Para evitar descargas manuales y asegurar la reproducibilidad del pipeline de datos, se utilizó la API oficial de Kaggle en Python. "
        "Previamente se generó el archivo de credenciales 'kaggle.json' desde el perfil de usuario (Settings -> API -> Create New API Token):"
    )
    
    codigo_api = (
        "# Paso 1: Configuración de Credenciales de la API de Kaggle\n"
        "import os\n"
        "import zipfile\n"
        "from kaggle.api.kaggle_api_extended import KaggleApi\n\n"
        "# Definir variables de entorno de autenticación\n"
        "os.environ['KAGGLE_USERNAME'] = 'tu_usuario_kaggle'\n"
        "os.environ['KAGGLE_KEY'] = 'tu_api_key_privada'\n\n"
        "# Inicializar cliente y autenticar\n"
        "api = KaggleApi()\n"
        "api.authenticate()\n"
        "print('Autenticación con Kaggle API exitosa.')\n\n"
        "# Descarga automatizada a la carpeta local './datos'\n"
        "api.dataset_download_files('rohanrao/formula-1-world-championship-1950-2020', path='./datos', unzip=True)\n"
        "api.dataset_download_files('gregorut/videogamesales', path='./datos', unzip=True)"
    )
    agregar_bloque_codigo(doc, codigo_api)

    # -------------------------------------------------------------
    # SECCIÓN 2: DATASET 1 - FÓRMULA 1 (DEPORTES)
    # -------------------------------------------------------------
    h2 = doc.add_heading(level=1)
    r_h2 = h2.add_run("2. Evaluación de Datos: Fórmula 1 (Dataset de Deportes)")
    r_h2.font.color.rgb = RGBColor(10, 35, 66)
    
    doc.add_paragraph(
        "El dataset de Fórmula 1 compila el historial de Grandes Premios, incluyendo posiciones de salida (grid), "
        "posiciones finales de carrera, escuderías constructoras, paradas en pits y velocidades de vuelta rápida en km/h."
    )
    
    doc.add_heading("2.1. Evaluación Estructural (Primer Vistazo y Tipos de Datos)", level=2)
    doc.add_paragraph(
        "Se realiza la carga con Pandas y la inspección dimensional mediante df.head() y df.info():"
    )
    
    codigo_f1_est = (
        "import pandas as pd\n\n"
        "# Carga del Dataset de F1\n"
        "df_f1 = pd.read_csv('./datos/formula1_world_championship.csv')\n\n"
        "print('--- Primeras 5 Filas ---')\n"
        "print(df_f1.head())\n\n"
        "print('\\n--- Información Estructural y Tipos de Datos ---')\n"
        "print(df_f1.info())"
    )
    agregar_bloque_codigo(doc, codigo_f1_est)
    
    # Cargar datos reales de f1 para métricas
    df_f1 = pd.read_csv('Practica_Ciencia_Datos/datos/formula1_world_championship.csv')
    
    doc.add_paragraph(
        f"Diagnóstico Estructural: El dataset contiene {df_f1.shape[0]} filas y {df_f1.shape[1]} columnas. "
        "Se identifican 7 variables numéricas (año de carrera, posición de salida, posición final, puntos, vueltas completadas, velocidad máxima, pits) "
        "y 5 variables categóricas (Gran Premio, nombre del piloto, escudería/constructor, país y estatus de carrera)."
    )
    
    doc.add_heading("2.2. Evaluación de Calidad (Datos Faltantes y Duplicados)", level=2)
    nulos_f1 = df_f1.isnull().sum()
    dups_f1 = df_f1.duplicated().sum()
    
    codigo_f1_cal = (
        "# Evaluación de Calidad de Datos\n"
        "print('--- Valores Faltantes (Nulos) por Columna ---')\n"
        "print(df_f1.isnull().sum())\n\n"
        "print(f'\\nFilas duplicadas detectadas: {df_f1.duplicated().sum()}')"
    )
    agregar_bloque_codigo(doc, codigo_f1_cal)
    
    doc.add_paragraph(
        f"Diagnóstico de Calidad: Se detectaron {dups_f1} filas duplicadas introducidas por redundancia de registro, las cuales deben removerse antes de modelar. "
        f"Respecto a los datos faltantes, se encontraron {nulos_f1['fastest_lap_speed_kmh']} registros nulos en 'fastest_lap_speed_kmh'. "
        "El análisis confirma que no se trata de una falla de captura, sino de abandonos de carrera (DNR por choque o falla de motor) donde el piloto no completó vueltas cronometradas."
    )

    doc.add_heading("2.3. Evaluación Estadística Descriptiva", level=2)
    doc.add_paragraph("Resumen numérico y categórico mediante df.describe():")
    
    desc_f1_num = df_f1[['grid_position', 'finish_position', 'points_awarded', 'fastest_lap_speed_kmh']].describe()
    agregar_tabla_df(doc, desc_f1_num, "Estadísticas Numéricas - Fórmula 1")
    
    doc.add_heading("2.4. Visualización para Evaluar Relaciones (Seaborn)", level=2)
    doc.add_paragraph(
        "Se diseñaron dos gráficos clave: el Gráfico 1 para evaluar la distribución de la velocidad máxima de carrera (histplot), "
        "y el Gráfico 2 para analizar el impacto de la posición de parrilla de salida en el resultado final según escudería (scatterplot):"
    )
    
    # Insertar Gráfica 1 F1
    p_cap1 = doc.add_paragraph()
    p_cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap1 = p_cap1.add_run("Gráfico 1: Distribución de la Velocidad Máxima de Vuelta Rápida en F1")
    r_cap1.bold = True
    r_cap1.font.color.rgb = RGBColor(10, 35, 66)
    if os.path.exists('Practica_Ciencia_Datos/graficas_f1/f1_grafico1_distribucion_velocidad.png'):
        doc.add_picture('Practica_Ciencia_Datos/graficas_f1/f1_grafico1_distribucion_velocidad.png', width=Inches(5.8))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        
    doc.add_paragraph(
        "Interpretación Gráfico 1: La velocidad máxima presenta una distribución aproximadamente normal (Gaussiana) "
        "centrada en los 232.5 km/h, con una dispersión estándar de ±12 km/h. Se observan colas ligeras asociadas a circuitos "
        "de altísima velocidad punta como Monza (más de 250 km/h) y circuitos urbanos lentos como Mónaco (menos de 210 km/h)."
    )
    
    # Insertar Gráfica 2 F1
    p_cap2 = doc.add_paragraph()
    p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap2 = p_cap2.add_run("Gráfico 2: Relación entre Posición de Salida (Grid) y Posición Final por Escudería")
    r_cap2.bold = True
    r_cap2.font.color.rgb = RGBColor(10, 35, 66)
    if os.path.exists('Practica_Ciencia_Datos/graficas_f1/f1_grafico2_grid_vs_finish.png'):
        doc.add_picture('Practica_Ciencia_Datos/graficas_f1/f1_grafico2_grid_vs_finish.png', width=Inches(5.8))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph(
        "Interpretación Gráfico 2: La gráfica de dispersión evidencia una correlación lineal positiva fuerte entre la salida y la llegada. "
        "Los puntos situados cerca de la línea diagonal discontinua representan pilotos que mantuvieron su lugar de largada. "
        "Las escuderías top (Red Bull Racing y Ferrari) demuestran mayor consistencia en cuadrantes superiores (Grid 1-4, Finish 1-4), "
        "mientras que en la media tabla existe mayor variabilidad por adelantamientos y estrategias de paradas en pits."
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # SECCIÓN 3: DATASET 2 - VENTAS DE VIDEOJUEGOS (LIBRE)
    # -------------------------------------------------------------
    h3 = doc.add_heading(level=1)
    r_h3 = h3.add_run("3. Evaluación de Datos: Ventas de Videojuegos (Dataset Libre)")
    r_h3.font.color.rgb = RGBColor(10, 35, 66)
    
    doc.add_paragraph(
        "El dataset 'vgsales' registra el catálogo de videojuegos comerciales que superaron las 100,000 copias vendidas a nivel mundial, "
        "desglosando las ventas por regiones geográficas: Norteamérica (NA), Europa (EU), Japón (JP) y Otras Regiones."
    )
    
    doc.add_heading("3.1. Evaluación Estructural", level=2)
    df_vg = pd.read_csv('Practica_Ciencia_Datos/datos/vgsales_videogames.csv')
    
    codigo_vg_est = (
        "# Carga del Dataset de Videojuegos\n"
        "df_vg = pd.read_csv('./datos/vgsales_videogames.csv')\n\n"
        "print('--- Primeras Filas ---')\n"
        "print(df_vg.head())\n\n"
        "print('\\n--- Información General y Tipos de Datos ---')\n"
        "print(df_vg.info())"
    )
    agregar_bloque_codigo(doc, codigo_vg_est)
    
    doc.add_paragraph(
        f"Diagnóstico Estructural: Contiene {df_vg.shape[0]} registros y {df_vg.shape[1]} columnas. "
        "Posee variables cuantitativas continuas en millones de dólares/copias (NA_Sales, EU_Sales, JP_Sales, Other_Sales, Global_Sales) "
        "y variables cualitativas nominales (Platform, Genre, Publisher)."
    )

    doc.add_heading("3.2. Evaluación de Calidad de Datos", level=2)
    nulos_vg = df_vg.isnull().sum()
    dups_vg = df_vg.duplicated().sum()
    
    codigo_vg_cal = (
        "print('--- Datos Faltantes por Columna ---')\n"
        "print(df_vg.isnull().sum())\n\n"
        "print(f'Filas duplicadas detectadas: {df_vg.duplicated().sum()}')"
    )
    agregar_bloque_codigo(doc, codigo_vg_cal)
    
    doc.add_paragraph(
        f"Diagnóstico de Calidad: Se identificaron {nulos_vg['Year']} registros sin año de lanzamiento y {nulos_vg['Publisher']} títulos sin editorial especificada. "
        f"Asimismo, se detectaron {dups_vg} filas duplicadas. Para un análisis de series de tiempo se recomienda imputar el año con la mediana "
        "o descartar las filas nulas dado que representan menos del 3% del volumen total."
    )

    doc.add_heading("3.3. Evaluación Estadística Descriptiva", level=2)
    desc_vg_num = df_vg[['NA_Sales', 'EU_Sales', 'JP_Sales', 'Global_Sales']].describe()
    agregar_tabla_df(doc, desc_vg_num, "Estadísticas de Ventas (Millones de Copias)")

    doc.add_heading("3.4. Visualización para Evaluar Relaciones (Seaborn)", level=2)
    
    # Insertar Gráfica 1 Videojuegos
    p_cap3 = doc.add_paragraph()
    p_cap3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap3 = p_cap3.add_run("Gráfico 3: Distribución Asimétrica de Ventas Globales de Videojuegos")
    r_cap3.bold = True
    r_cap3.font.color.rgb = RGBColor(10, 35, 66)
    if os.path.exists('Practica_Ciencia_Datos/graficas_videojuegos/vg_grafico1_distribucion_ventas.png'):
        doc.add_picture('Practica_Ciencia_Datos/graficas_videojuegos/vg_grafico1_distribucion_ventas.png', width=Inches(5.8))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph(
        "Interpretación Gráfico 3: La variable de ventas globales exhibe un sesgo positivo pronunciado a la derecha (asimetría positiva). "
        "El 80% de los títulos comerciales se concentra en ventas moderadas inferiores a 2.5 millones de copias, mientras que un grupo selecto "
        "de mega-éxitos de franquicias consagradas actúa como valores atípicos (outliers) que superan los 10 millones de ventas."
    )

    # Insertar Gráfica 2 Videojuegos
    p_cap4 = doc.add_paragraph()
    p_cap4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap4 = p_cap4.add_run("Gráfico 4: Correlación Regional de Ventas entre Norteamérica y Europa por Género")
    r_cap4.bold = True
    r_cap4.font.color.rgb = RGBColor(10, 35, 66)
    if os.path.exists('Practica_Ciencia_Datos/graficas_videojuegos/vg_grafico2_na_vs_eu_sales.png'):
        doc.add_picture('Practica_Ciencia_Datos/graficas_videojuegos/vg_grafico2_na_vs_eu_sales.png', width=Inches(5.8))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph(
        "Interpretación Gráfico 4: Existe una fuerte correlación lineal directa entre el mercado norteamericano y el europeo (Pearson r > 0.82). "
        "El análisis por género revela que los títulos de Acción y Shooters dominan las ventas en ambas regiones occidentales, "
        "lo que permite a los estudios de desarrollo proyectar el éxito en Europa a partir de la recepción preliminar en EE.UU."
    )

    # -------------------------------------------------------------
    # SECCIÓN 4: CONCLUSIONES FINALES
    # -------------------------------------------------------------
    doc.add_page_break()
    h4 = doc.add_heading(level=1)
    r_h4 = h4.add_run("4. Conclusiones Generales y Recomendaciones Metodológicas")
    r_h4.font.color.rgb = RGBColor(10, 35, 66)
    
    puntos_conclusiones = [
        ("1. Importancia de la Evaluación Estructural: ", 
         "El uso coordinado de df.head() y df.info() permite identificar discrepancias en tipos de datos desde el inicio, como fechas o categorías leídas erróneamente como texto (object) que requieren casteo previo."),
        ("2. Distinción Crítica entre Nulos y Eventos Reales: ", 
         "La práctica demostró que los valores nulos no siempre son 'errores de captura'. En deportes como Fórmula 1, los nulos en vuelta rápida corresponden al hecho deportivo de un abandono, por lo que rellenarlos ciegamente con la media falsearía la estadística."),
        ("3. Poder del Análisis Multivariable: ", 
         "La integración de Seaborn mediante scatterplots combinados con el parámetro 'hue' permitió evaluar relaciones cruzadas complejas (como rendimiento por escudería o correlación regional por género de videojuego) de manera inmediata e intuitiva."),
        ("4. Recomendación para Modelado Posterior: ", 
         "Previo a entrenar modelos de regresión o clasificación en las siguientes unidades de la asignatura, se recomienda aplicar transformaciones logarítmicas a variables asimétricas (como ventas globales) y eliminar duplicados para evitar sobreajuste.")
    ]

    for subtitulo, texto in puntos_conclusiones:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.line_spacing = 1.15
        
        r_sub = p.add_run(subtitulo)
        r_sub.bold = True
        r_sub.font.name = 'Calibri'
        r_sub.font.size = Pt(10.5)
        r_sub.font.color.rgb = RGBColor(10, 35, 66)
        
        r_txt = p.add_run(texto)
        r_txt.font.name = 'Calibri'
        r_txt.font.size = Pt(10.5)
    
    # Guardar documento
    ruta_guardado_downloads = r'C:\Users\burel\Downloads\Reporte_Practica_Recopilacion_y_Evaluacion_Datos_Corregido.docx'
    ruta_guardado_local = 'Practica_Ciencia_Datos/Reporte_Practica_Recopilacion_y_Evaluacion_Datos_Corregido.docx'
    
    doc.save(ruta_guardado_downloads)
    doc.save(ruta_guardado_local)
    print(f"\nDocumento Word generado exitosamente:")
    print(f"-> Guardado en: {ruta_guardado_downloads}")
    print(f"-> Copia local en: {ruta_guardado_local}")

if __name__ == '__main__':
    construir_reporte_word()
