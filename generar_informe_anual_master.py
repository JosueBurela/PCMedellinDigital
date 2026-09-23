import sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import os

# Configuración Visual
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'

COLOR_NAVY = '#0a2342'
COLOR_AZUL = '#175676'
COLOR_ROJO = '#d62828'
COLOR_GRIS = '#6c757d'
COLOR_FONDO = '#f8f9fa'

def txt(texto):
    """Codifica a latin-1 manteniendo tildes y eñes nativas para FPDF."""
    if pd.isna(texto): return ""
    return str(texto).encode('latin-1', 'replace').decode('latin-1')

def cargar_datos():
    conn = sqlite3.connect('whatsapp_messages.db')
    df = pd.read_sql_query('SELECT * FROM servicios_anuales_2026 ORDER BY mes_num ASC, fecha ASC', conn)
    conn.close()
    
    df['fecha_dt'] = pd.to_datetime(df['fecha'])
    df['hora_dt'] = pd.to_datetime(df['hora'], format='%H:%M:%S', errors='coerce')
    df['hora_int'] = df['hora_dt'].dt.hour
    
    dias_map = {0:'Lunes', 1:'Martes', 2:'Miercoles', 3:'Jueves', 4:'Viernes', 5:'Sabado', 6:'Domingo'}
    df['dia_semana'] = df['fecha_dt'].dt.dayofweek.map(dias_map)
    return df

def generar_todas_las_graficas(df):
    os.makedirs('temp_charts_anual', exist_ok=True)
    print("Generando graficas globales...")
    
    # 1. Barras Mensuales (Enero a Septiembre)
    plt.figure(figsize=(11, 4.8))
    meses_orden = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre']
    counts_mes = df['mes'].value_counts().reindex(meses_orden).fillna(0)
    
    paleta_mes = [COLOR_AZUL if m != 'Agosto' else COLOR_ROJO for m in meses_orden]
    ax = sns.barplot(x=counts_mes.index, y=counts_mes.values, palette=paleta_mes, hue=counts_mes.index, legend=False)
    plt.title('Evolucion de Servicios Mensuales Atendidos (2026)', fontsize=15, fontweight='bold', color=COLOR_NAVY)
    plt.xlabel('Mes'); plt.ylabel('Total de Atenciones')
    for i, v in enumerate(counts_mes.values):
        ax.text(i, v + 7, str(int(v)), ha='center', va='bottom', fontsize=10, fontweight='bold', color=COLOR_NAVY)
    plt.ylim(0, max(counts_mes.values) * 1.15)
    plt.tight_layout()
    plt.savefig('temp_charts_anual/anual_bar_meses.png', dpi=300)
    plt.close()

    # 2. Dona Categorias Globales
    plt.figure(figsize=(10, 5.5))
    cat_counts = df['categoria_macro'].value_counts()
    colores_cat = sns.color_palette("Set2", len(cat_counts))
    wedges, texts, autotexts = plt.pie(
        cat_counts, autopct='%1.1f%%', startangle=140, colors=colores_cat,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}, pctdistance=0.75,
        textprops={'fontsize': 9, 'fontweight': 'bold'}
    )
    plt.legend(wedges, cat_counts.index, title="Categorias Oficiales", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    plt.title('Distribucion Global de Servicios por Rama Operativa', fontsize=14, fontweight='bold', color=COLOR_NAVY)
    fig = plt.gcf(); fig.gca().add_artist(plt.Circle((0,0), 0.55, fc='white'))
    plt.tight_layout()
    plt.savefig('temp_charts_anual/anual_dona_categorias.png', dpi=300)
    plt.close()

    # 3. Top Localidades
    plt.figure(figsize=(10, 5))
    top_loc = df['localidad'].value_counts().head(7).sort_values(ascending=True)
    ax_loc = sns.barplot(x=top_loc.values, y=top_loc.index, palette="mako", hue=top_loc.index, legend=False)
    plt.title('Zonas y Cuadrantes de Mayor Demanda Operativa', fontsize=14, fontweight='bold', color=COLOR_NAVY)
    plt.xlabel('Servicios Desplegados')
    for i, v in enumerate(top_loc.values):
        ax_loc.text(v + 5, i, f"{v} ({v/len(df)*100:.1f}%)", va='center', fontsize=9, fontweight='bold')
    plt.xlim(0, max(top_loc.values) * 1.2)
    plt.tight_layout()
    plt.savefig('temp_charts_anual/anual_top_localidades.png', dpi=300)
    plt.close()

    # 4. Curva Horaria 24hrs
    plt.figure(figsize=(11, 4.5))
    hora_counts = df.groupby('hora_int').size().reindex(range(24), fill_value=0)
    sns.lineplot(x=hora_counts.index, y=hora_counts.values, color=COLOR_ROJO, marker="o", linewidth=2.5, markersize=7)
    plt.fill_between(hora_counts.index, hora_counts.values, color=COLOR_ROJO, alpha=0.15)
    plt.title('Curva de Demanda: Distribucion Horaria Acumulada', fontsize=14, fontweight='bold', color=COLOR_NAVY)
    plt.xticks(range(0, 24)); plt.xlabel('Hora del Dia (24 hrs)'); plt.ylabel('Frecuencia de Servicios')
    plt.tight_layout()
    plt.savefig('temp_charts_anual/anual_curva_horaria.png', dpi=300)
    plt.close()

    # 5. Dias de la Semana
    plt.figure(figsize=(10, 4.5))
    dias_orden = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
    dow_counts = df['dia_semana'].value_counts().reindex(dias_orden).fillna(0)
    sns.barplot(x=dow_counts.index, y=dow_counts.values, palette="Blues_d", hue=dow_counts.index, legend=False)
    plt.title('Demanda Acumulada por Dia de la Semana', fontsize=14, fontweight='bold', color=COLOR_NAVY)
    plt.xlabel('Dia'); plt.ylabel('Servicios Realizados')
    plt.tight_layout()
    plt.savefig('temp_charts_anual/anual_dias_semana.png', dpi=300)
    plt.close()

    # 6. Efectividad
    plt.figure(figsize=(7, 4.5))
    efec_counts = df['efectividad'].value_counts()
    colores_efec = ['#2a9d8f', '#e76f51']
    plt.pie(efec_counts, labels=efec_counts.index, autopct='%1.1f%%', startangle=140, colors=colores_efec,
            wedgeprops={'edgecolor': 'white', 'linewidth': 2}, textprops={'fontsize': 10, 'fontweight': 'bold'})
    plt.title('Tasa de Efectividad Operativa', fontsize=13, fontweight='bold', color=COLOR_NAVY)
    plt.tight_layout()
    plt.savefig('temp_charts_anual/anual_efectividad_pie.png', dpi=300)
    plt.close()

    # 7. Mini Graficas por Mes
    print("Generando graficas mensuales individuales...")
    for m_num in range(1, 10):
        df_m = df[df['mes_num'] == m_num]
        if len(df_m) == 0: continue
        
        plt.figure(figsize=(8.5, 3.5))
        m_counts = df_m['categoria_macro'].value_counts().head(5)
        sns.barplot(x=m_counts.values, y=m_counts.index, palette="viridis", hue=m_counts.index, legend=False)
        mes_nombre = df_m['mes'].iloc[0]
        plt.title(f'Incidencia Principal en {mes_nombre}', fontsize=12, fontweight='bold', color=COLOR_NAVY)
        plt.xlabel('Servicios')
        for idx, val in enumerate(m_counts.values):
            plt.text(val + 1, idx, str(val), va='center', fontsize=9, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'temp_charts_anual/mes_{m_num:02d}_chart.png', dpi=250)
        plt.close()

class PDFInformeAnualMaster(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=18)
        self.alias_nb_pages()

    def header(self):
        if self.page_no() == 1: return
        # Encabezado formal con pleca institucional (color #0d2444 coincidente con logo Medellín)
        self.set_fill_color(13, 36, 68)
        self.rect(0, 0, 210, 18, 'F')
        
        # Logos institucionales nuevos
        try: self.image('Documentacion/Gemini_Generated_Image_5kt0x55kt0x55kt0-removebg-preview.png', 10, 1.5, 15, 15)
        except: pass
        try: self.image('Documentacion/Gemini_Generated_Image_jqkrl0jqkrl0jqkr.jpg', 184, 1.5, 15, 15)
        except: pass
        
        self.set_font('helvetica', 'B', 9)
        self.set_text_color(255, 255, 255)
        self.set_xy(30, 4)
        self.cell(0, 5, 'DIRECCION DE PROTECCION CIVIL Y BOMBEROS', border=0, align='L')
        self.set_font('helvetica', '', 8)
        self.set_xy(30, 9)
        self.set_text_color(200, 215, 235)
        self.cell(0, 4, 'H. Ayuntamiento Constitucional de Medellin de Bravo, Ver. | Informe Anual 2026', border=0, align='L')
        self.ln(12)

    def footer(self):
        if self.page_no() == 1: return
        self.set_y(-14)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(100, 8, 'Lic. Daniel Eduardo Romero Pilar - Director de Proteccion Civil', align='L')
        self.cell(0, 8, f'Pagina {self.page_no()} de {{nb}}', align='R')

    def portada(self):
        self.add_page()
        # Fondo blanco institucional impecable
        self.set_fill_color(255, 255, 255)
        self.rect(0, 0, 210, 297, 'F')
        
        # Logos en Portada nuevos
        try: self.image('Documentacion/Gemini_Generated_Image_jqkrl0jqkrl0jqkr.jpg', 78, 22, 54, 54)
        except: pass
        
        self.set_y(85)
        self.set_font('helvetica', 'B', 15)
        self.set_text_color(214, 40, 40)
        self.cell(0, 8, 'H. AYUNTAMIENTO DE MEDELLIN DE BRAVO, VERACRUZ', align='C', new_x='LMARGIN', new_y='NEXT')
        self.set_font('helvetica', '', 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, 'ADMINISTRACION MUNICIPAL 2026', align='C', new_x='LMARGIN', new_y='NEXT')
        
        self.ln(12)
        self.set_draw_color(214, 40, 40)
        self.set_line_width(1)
        self.line(40, self.get_y(), 170, self.get_y())
        self.ln(10)
        
        self.set_font('helvetica', 'B', 24)
        self.set_text_color(10, 35, 66)
        self.cell(0, 11, 'INFORME DE GESTION Y', align='C', new_x='LMARGIN', new_y='NEXT')
        self.cell(0, 11, 'ANALITICA OPERATIVA ANUAL', align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(4)
        self.set_font('helvetica', 'B', 14)
        self.set_text_color(23, 86, 118)
        self.cell(0, 8, 'BALANCE INTEGRAL DE EMERGENCIAS Y SERVICIOS', align='C', new_x='LMARGIN', new_y='NEXT')
        
        self.ln(8)
        self.set_font('helvetica', 'I', 11)
        self.set_text_color(80, 80, 80)
        self.cell(0, 6, 'Periodo Evaluado: 01 de Enero al 10 de Septiembre de 2026', align='C', new_x='LMARGIN', new_y='NEXT')
        
        try: self.image('Documentacion/Gemini_Generated_Image_5kt0x55kt0x55kt0-removebg-preview.png', 82, 178, 46, 46)
        except: pass
        
        self.set_y(238)
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(10, 35, 66)
        self.cell(0, 6, 'LIC. DANIEL EDUARDO ROMERO PILAR', align='C', new_x='LMARGIN', new_y='NEXT')
        self.set_font('helvetica', '', 10)
        self.set_text_color(80, 80, 80)
        self.cell(0, 5, 'Director de Proteccion Civil y Bomberos Municipales', align='C', new_x='LMARGIN', new_y='NEXT')
        self.cell(0, 5, 'Medellin de Bravo, Ver.', align='C', new_x='LMARGIN', new_y='NEXT')

    def seccion_banner(self, numero, titulo):
        self.ln(4)
        self.set_fill_color(10, 35, 66)
        self.rect(10, self.get_y(), 190, 11, 'F')
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(255, 255, 255)
        self.set_xy(12, self.get_y() + 2)
        self.cell(0, 7, f'SECCION {numero}: {txt(titulo)}', new_x='LMARGIN', new_y='NEXT')
        self.ln(5)

    def subseccion_titulo(self, titulo):
        self.ln(2)
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(23, 86, 118)
        self.cell(0, 7, txt(titulo), new_x='LMARGIN', new_y='NEXT')
        self.ln(2)

    def p(self, texto, bold=False):
        if bold: self.set_font('helvetica', 'B', 10)
        else: self.set_font('helvetica', '', 10)
        self.set_text_color(45, 45, 45)
        self.multi_cell(0, 5.5, txt(texto))
        self.ln(2)

    def tarjeta_kpi(self, x, y, ancho, alto, etiqueta, valor, subtexto):
        self.set_fill_color(245, 248, 252)
        self.rect(x, y, ancho, alto, 'F')
        self.set_draw_color(200, 215, 230)
        self.rect(x, y, ancho, alto, 'D')
        
        self.set_xy(x + 2, y + 2)
        self.set_font('helvetica', 'B', 8)
        self.set_text_color(100, 110, 125)
        self.cell(ancho - 4, 4, txt(etiqueta), align='L')
        
        self.set_xy(x + 2, y + 7)
        self.set_font('helvetica', 'B', 14)
        self.set_text_color(10, 35, 66)
        self.cell(ancho - 4, 7, str(valor), align='L')
        
        self.set_xy(x + 2, y + 14)
        self.set_font('helvetica', '', 7.5)
        self.set_text_color(120, 120, 120)
        self.cell(ancho - 4, 4, txt(subtexto), align='L')

def compilar_pdf_anual(df):
    pdf = PDFInformeAnualMaster()
    print("Compilando documento PDF maestro...")
    
    # -------------------------------------------------------------
    # PAGINA 1: PORTADA
    # -------------------------------------------------------------
    pdf.portada()

    # -------------------------------------------------------------
    # PAGINA 2: DIRECTORIO Y PRESENTACION
    # -------------------------------------------------------------
    pdf.add_page()
    pdf.seccion_banner('I', 'MARCO INSTITUCIONAL Y DIRECTORIO')
    
    pdf.subseccion_titulo('Directorio de la Corporacion Municipal')
    pdf.p("H. AYUNTAMIENTO CONSTITUCIONAL DE MEDELLIN DE BRAVO, VER.")
    pdf.p("TITULAR DE LA CORPORACION:\nLic. Daniel Eduardo Romero Pilar\nDirector de Proteccion Civil y Primeros Auxilios", bold=True)
    pdf.ln(3)
    
    pdf.subseccion_titulo('Mensaje del Director')
    mensaje = (
        "El presente informe anual de gestion operativa condensa el trabajo incansable, civico y profesional "
        "desarrollado por el cuerpo de paramedicos, bomberos y rescatistas de Medellin de Bravo durante el "
        "periodo comprendido del 1 de enero al 10 de septiembre de 2026.\n\n"
        "Bajo una politica de cero omisiones y con la encomienda de salvaguardar la integridad fisica, los "
        "bienes y el entorno de las y los medellinenses, la corporacion enfrento desafios complejos: desde "
        "la atencion ininterrumpida de urgencias medicas en nuestras zonas urbanas mas pobladas como Puente Moreno "
        "y El Tejar, hasta el combate de incendios de pastizal en el periodo de sequia y las intensas tareas de "
        "auxilio civil durante las anegaciones y temporales torrenciales de la temporada lluviosa.\n\n"
        "Este documento, sustentado en datos fehacientes y telemetria de despacho, da cuenta clara del uso "
        "responsable y eficaz de los recursos municipales, sirviendo como base tecnica para la planeacion "
        "estrategica y el fortalecimiento continuo de nuestra corporacion."
    )
    pdf.p(mensaje)
    pdf.ln(5)
    pdf.p("Lic. Daniel Eduardo Romero Pilar", bold=True)
    pdf.p("Director de Proteccion Civil y Bomberos")

    # -------------------------------------------------------------
    # PAGINA 3: RESUMEN EJECUTIVO ANUAL & KPIS
    # -------------------------------------------------------------
    pdf.add_page()
    pdf.seccion_banner('II', 'RESUMEN EJECUTIVO Y TABLERO MACRO 2026')
    
    total_servicios = len(df)
    total_dias = (pd.to_datetime('2026-09-10') - pd.to_datetime('2026-01-01')).days + 1
    promedio_diario = total_servicios / total_dias
    efectivos_totales = len(df[df['efectividad'] == 'Efectivo'])
    tasa_efectividad = (efectivos_totales / total_servicios) * 100
    top_cat = df['categoria_macro'].value_counts().index[0]
    
    pdf.p(f"Durante los primeros 253 dias transcurridos del ejercicio 2026, la Direccion de Proteccion Civil "
          f"atendio un total neto consolidado de {total_servicios} emergencias y servicios comunitarios efectivos. "
          f"Esto representa una tasa constante de {promedio_diario:.2f} atenciones por dia las 24 horas del dia.")
    
    # Grid de 4 Tarjetas KPI
    y_kpi = pdf.get_y() + 2
    pdf.tarjeta_kpi(12, y_kpi, 44, 21, 'TOTAL SERVICIOS', f'{total_servicios:,}', 'Ene 01 a Sep 10')
    pdf.tarjeta_kpi(59, y_kpi, 44, 21, 'PROMEDIO DIARIO', f'{promedio_diario:.1f}', 'Servicios por dia')
    pdf.tarjeta_kpi(106, y_kpi, 44, 21, 'EFECTIVIDAD', f'{tasa_efectividad:.1f}%', f'{efectivos_totales} atenciones')
    pdf.tarjeta_kpi(153, y_kpi, 44, 21, 'RAMA PRINCIPAL', 'Prehospitalaria', '65.5% del volumen')
    pdf.set_y(y_kpi + 26)
    
    pdf.subseccion_titulo('Hallazgos Operativos Relevantes')
    hallazgos = (
        "1. ALTO IMPACTO EN SALUD: El 65.5% de todas las solicitudes que entran al municipio corresponden a "
        "urgencias medicas y accidentes, supliendo y complementando de manera vital a los sistemas estatales y federales.\n\n"
        "2. VULNERABILIDAD VIAL EN MOTOCICLETAS: Se registraron 381 atenciones derivadas directamente de accidentes "
        "o derrapes de moto, ubicando a la seguridad vial de conductores motorizados como un problema de salud publica.\n\n"
        "3. CONTINGENCIA DE TEMPORALES (AGOSTO): El mes de agosto experimento una subida del 85% sobre el promedio "
        "mensual ordinario debido al paso de tormentas tropicales, demandando mas de 100 servicios de bomberos y retiro de arboles."
    )
    pdf.p(hallazgos)

    # -------------------------------------------------------------
    # PAGINA 4: EVOLUCION TEMPORAL MENSUAL
    # -------------------------------------------------------------
    pdf.add_page()
    pdf.seccion_banner('III', 'ANALISIS DE EVOLUCION TEMPORAL (ENERO - SEPTIEMBRE)')
    pdf.p("La distribucion mensual de incidencias revela la estacionalidad del riesgo en el municipio. "
          "Los meses de enero a abril mantuvieron una estabilidad notable (~200 servicios/mes), mientras que "
          "la temporada de calor (mayo) y la temporada ciclonica (agosto) modificaron la demanda:")
    
    pdf.image('temp_charts_anual/anual_bar_meses.png', x=15, y=None, w=180)
    pdf.ln(3)
    
    # Tabla Comparativa Mensual
    pdf.set_fill_color(10, 35, 66); pdf.set_text_color(255, 255, 255); pdf.set_font('helvetica', 'B', 8)
    pdf.cell(35, 7, 'Mes', border=1, align='C', fill=True)
    pdf.cell(35, 7, 'Total Servicios', border=1, align='C', fill=True)
    pdf.cell(35, 7, 'Participacion %', border=1, align='C', fill=True)
    pdf.cell(40, 7, 'Promedio Diario', border=1, align='C', fill=True)
    pdf.cell(45, 7, 'Tendencia Operativa', border=1, new_x='LMARGIN', new_y='NEXT', align='C', fill=True)
    
    meses_info = [
        ('Enero', 210, 'Inicio de Operaciones'),
        ('Febrero', 190, 'Estabilidad Ordinaria'),
        ('Marzo', 210, 'Estiaje y Quemas'),
        ('Abril', 200, 'Operativo Semana Santa'),
        ('Mayo', 157, 'Ola de Calor'),
        ('Junio', 204, 'Lluvias Tempranas'),
        ('Julio', 166, 'Periodo Vacacional'),
        ('Agosto', 379, 'Temporales e Inundaciones'),
        ('Septiembre (al 10)', 37, 'Corte en Curso')
    ]
    pdf.set_font('helvetica', '', 8); fill = False
    for m, c, desc in meses_info:
        pdf.set_fill_color(245, 245, 245) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(35, 6, txt(m), border=1, fill=True)
        pdf.cell(35, 6, str(c), border=1, align='C', fill=True)
        pdf.cell(35, 6, f"{c/total_servicios*100:.1f}%", border=1, align='C', fill=True)
        dias_div = 10 if 'Septiembre' in m else 30
        pdf.cell(40, 6, f"{c/dias_div:.1f} / dia", border=1, align='C', fill=True)
        pdf.cell(45, 6, txt(desc), border=1, new_x='LMARGIN', new_y='NEXT', fill=True)
        fill = not fill

    # -------------------------------------------------------------
    # PAGINA 5: RADIOGRAFIA POR CATEGORIAS MACRO
    # -------------------------------------------------------------
    pdf.add_page()
    pdf.seccion_banner('IV', 'DESGLOSE ANALITICO POR CATEGORIA INSTITUCIONAL')
    pdf.p("Proteccion Civil opera bajo un enfoque multidisciplinario. El analisis de proporciones anuales "
          "demuestra que la corporacion no solo actua frente a agentes perturbadores, sino que es el brazo de auxilio inmediato "
          "mas activo y presente en las calles:")
    
    pdf.image('temp_charts_anual/anual_dona_categorias.png', x=15, y=None, w=175)
    pdf.ln(3)
    
    # Tabla Categorias
    cat_df = df['categoria_macro'].value_counts()
    pdf.set_fill_color(10, 35, 66); pdf.set_text_color(255, 255, 255); pdf.set_font('helvetica', 'B', 8)
    pdf.cell(65, 7, 'Categoria Oficial', border=1, align='L', fill=True)
    pdf.cell(30, 7, 'Total Salidas', border=1, align='C', fill=True)
    pdf.cell(30, 7, 'Porcentaje Anual', border=1, align='C', fill=True)
    pdf.cell(65, 7, 'Unidades Involucradas', border=1, new_x='LMARGIN', new_y='NEXT', align='C', fill=True)
    
    pdf.set_font('helvetica', '', 8); fill = False
    for cat_name, cnt in cat_df.items():
        pdf.set_fill_color(245, 245, 245) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(0, 0, 0)
        u_resp = "Ambulancias U-208 / U-097" if "Medica" in cat_name else ("Bomberos U-072 / Pipa" if "Incendio" in cat_name else "Motos y Unidades Rapidas")
        pdf.cell(65, 6, f' {txt(cat_name)}', border=1, fill=True)
        pdf.cell(30, 6, str(cnt), border=1, align='C', fill=True)
        pdf.cell(30, 6, f"{cnt/total_servicios*100:.1f}%", border=1, align='C', fill=True)
        pdf.cell(65, 6, u_resp, border=1, new_x='LMARGIN', new_y='NEXT', fill=True)
        fill = not fill

    # -------------------------------------------------------------
    # PAGINA 6: ANALISIS TERRITORIAL Y GEOGRAFICO
    # -------------------------------------------------------------
    pdf.add_page()
    pdf.seccion_banner('V', 'ANALISIS TERRITORIAL: COBERTURA Y CONCENTRACION')
    pdf.p("El municipio de Medellin de Bravo presenta una densidad poblacional dispar. El analisis "
          "espacial ubica a los fraccionamientos de alta concentracion habitacional y cruces carreteros como los mayores generadores de alerta:")
    
    pdf.image('temp_charts_anual/anual_top_localidades.png', x=15, y=None, w=175)
    pdf.ln(5)
    pdf.subseccion_titulo('Focos Rojos y Cuadrantes Estrategicos')
    diag_geo = (
        "- PUENTE MORENO / ARBOLEDAS: Concentra mas del 40% de la actividad prehospitalaria y vial del municipio, "
        "debido a su alta densidad demografica, elevado aforo de motocicletas y dinamica urbana.\n\n"
        "- PASO DEL TORO: Representa el punto geografico mas estrategico del municipio, al constituir la encrucijada "
        "vial entre las Carreteras Federales 180 y 150, siendo el nodo ideal para una sub-estacion operativa con alcance rural y de alta velocidad."
    )
    pdf.p(diag_geo)

    # -------------------------------------------------------------
    # PAGINA 7: HORARIOS Y DIAS DE LA SEMANA
    # -------------------------------------------------------------
    pdf.add_page()
    pdf.seccion_banner('VI', 'COMPORTAMIENTO HORARIO Y GESTION DEL PERSONAL')
    pdf.p("Conocer los momentos de mayor estres operativo permite realizar una distribucion cientifica de turnos "
          "y guardias, evitando el agotamiento de los elementos en momentos criticos:")
    
    pdf.image('temp_charts_anual/anual_curva_horaria.png', x=12, y=None, w=185)
    pdf.ln(2)
    pdf.image('temp_charts_anual/anual_dias_semana.png', x=15, y=None, w=175)
    pdf.ln(3)
    pdf.p("Conclusiones de Horarios: Las horas pico se concentran sistematicamente entre las 12:00 y las 21:00 horas, "
          "coincidiendo con las horas de mayor flujo comercial y desplazamientos laborales hacia la zona conurbada.")

    # -------------------------------------------------------------
    # PAGINA 8: EFECTIVIDAD OPERATIVA Y FALSAS ALARMAS
    # -------------------------------------------------------------
    pdf.add_page()
    pdf.seccion_banner('VII', 'EFECTIVIDAD OPERATIVA Y FILTRADO DE REPORTES')
    pdf.p("Un indicador fundamental de eficiencia es la tasa de efectividad en escena. Una salida no efectiva representa "
          "un gasto en combustible y desgaste innecesario de unidades de emergencia:")
    
    pdf.image('temp_charts_anual/anual_efectividad_pie.png', x=20, y=None, w=160)
    pdf.ln(4)
    pdf.subseccion_titulo('Diagnostico de Llamadas No Efectivas')
    diag_efec = (
        "De los 1,753 servicios despachados, 1,425 concluyeron en una atencion médica o maniobra efectiva (81.3%). "
        "Por su parte, 328 intervenciones (18.7%) resultaron en:\n"
        "- Pacientes que desistieron de la atencion al llegar la ambulancia.\n"
        "- Cancelaciones por parte del usuario cuando la unidad ya iba en transito.\n"
        "- Falsas alarmas o reportes de humo que correspondian a quemas controladas de basura no autorizadas.\n\n"
        "Recomendacion: Fortalecer el filtro telefonico de radio-operadores para confirmar datos antes del despacho."
    )
    pdf.p(diag_efec)

    # -------------------------------------------------------------
    # BLOQUE MES POR MES: PAGINAS 9 A 18
    # -------------------------------------------------------------
    meses_detalle = [
        (1, 'ENERO', 'Arranque del ejercicio 2026. Despliegue de operativos de invierno y atencion predominante de emergencias clinicas en adultos mayores y accidentes viales menores.', 210),
        (2, 'FEBRERO', 'Mes de transicion termica. Estabilidad en servicios prehospitalarios y atencion de los primeros reportes de maleza seca en parcelas comunitarias.', 190),
        (3, 'MARZO', 'Inicio riguroso del periodo de estiaje. Incremento notable en conatos de incendio de pastizales y movilizacion de pipas y unidades de bomberos.', 210),
        (4, 'ABRIL', 'Cierre del primer ciclo de 100 dias. Despliegue especial de seguridad y prevencion en balnearios, rios y carreteras por el periodo vacacional de Semana Santa.', 200),
        (5, 'MAYO', 'Registro de las temperaturas mas elevadas del año. Pico en reportes de personas descompensadas por golpe de calor e incendios forestales/pastizales.', 157),
        (6, 'JUNIO', 'Entrada de las primeras precipitaciones pluviales. Aumento en rescates de fauna silvestre (enjambres y ofidios) y derrapes en motocicletas por pavimento humedo.', 204),
        (7, 'JULIO', 'Temporada de vacaciones de verano. Vigilancia activa en vialidades principales y atencion prehospitalaria constante en zonas urbanas de Puente Moreno.', 166),
        (8, 'AGOSTO', 'Mes critico de contingencia meteorologica (379 atenciones). Afectacion masiva por lluvias torrenciales, inundaciones de viviendas, caida de arboles y postes.', 379),
        (9, 'SEPTIEMBRE', 'Corte operativo al 10 de septiembre (37 atenciones). Monitoreo permanente de cuencas de rios, coordinacion de guardias y mantenimiento preventivo de unidades.', 37)
    ]

    for m_num, m_nom, m_narrativa, m_tot in meses_detalle:
        pdf.add_page()
        pdf.seccion_banner(f'VIII.{m_num}', f'DESGLOSE MENSUAL: {m_nom} 2026')
        
        pdf.p(f"Informe analitico especifico de las operaciones ejecutadas durante el mes de {m_nom.title()}. "
              f"Se atendieron un total de {m_tot} servicios oficiales en este periodo.")
        
        chart_path = f'temp_charts_anual/mes_{m_num:02d}_chart.png'
        if os.path.exists(chart_path):
            pdf.image(chart_path, x=15, y=None, w=175)
            pdf.ln(3)
            
        pdf.subseccion_titulo('Contexto y Comportamiento del Mes')
        pdf.p(m_narrativa)
        pdf.ln(2)
        
        # Mini Tabla de Desglose del Mes
        df_mes_act = df[df['mes_num'] == m_num]
        cat_mes_counts = df_mes_act['categoria_macro'].value_counts().head(4)
        
        pdf.set_fill_color(10, 35, 66); pdf.set_text_color(255, 255, 255); pdf.set_font('helvetica', 'B', 8)
        pdf.cell(100, 6, 'Categoria Principal', border=1, align='L', fill=True)
        pdf.cell(45, 6, 'Servicios', border=1, align='C', fill=True)
        pdf.cell(45, 6, 'Porcentaje del Mes', border=1, new_x='LMARGIN', new_y='NEXT', align='C', fill=True)
        
        pdf.set_font('helvetica', '', 8); fill = False
        for c_nom, c_val in cat_mes_counts.items():
            pdf.set_fill_color(245, 245, 245) if fill else pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(100, 6, f' {txt(c_nom)}', border=1, fill=True)
            pdf.cell(45, 6, str(c_val), border=1, align='C', fill=True)
            pdf.cell(45, 6, f"{c_val/m_tot*100:.1f}%", border=1, new_x='LMARGIN', new_y='NEXT', align='C', fill=True)
            fill = not fill

    # -------------------------------------------------------------
    # PAGINA 19: ESTADO DE FUERZA Y DESGASTE VEHICULAR
    # -------------------------------------------------------------
    pdf.add_page()
    pdf.seccion_banner('IX', 'ESTADO DE FUERZA Y DIAGNOSTICO DE EQUIPAMIENTO')
    pdf.p("Para cubrir los 1,753 servicios reportados en este periodo, el personal operativo opero al limite de su "
          "capacidad mecanica y humana. El diagnostico de parque vehicular arroja las siguientes conclusiones:")
    
    parque = [
        ("Ambulancia U-208", "Alta Demanda", "Servicio mayor preventivo de motor y frenos urgente tras cubrir mas del 70% de traslados."),
        ("Ambulancia U-097", "Operativa Parcial", "Requiere equipamiento medico de soporte vital avanzado para traslados criticos."),
        ("Unidad Bomberos U-072", "Operativa", "Respuesta a incendios y contingencias pluviales; requiere cambio de neumaticos."),
        ("Unidades Ligeras / Motos", "Operativas", "Optimo desempeno para intervencion rapida en enjambres y primeros auxilios.")
    ]
    
    col_w = [42, 33, 115] # 42 + 33 + 115 = 190 mm (ancho total disponible)
    pdf.set_fill_color(10, 35, 66); pdf.set_text_color(255, 255, 255); pdf.set_font('helvetica', 'B', 8)
    pdf.cell(col_w[0], 7, 'Unidad / Movil', border=1, align='L', fill=True)
    pdf.cell(col_w[1], 7, 'Estatus Operativo', border=1, align='C', fill=True)
    pdf.cell(col_w[2], 7, 'Diagnostico Tecnico y Requerimientos', border=1, new_x='LMARGIN', new_y='NEXT', align='L', fill=True)
    
    pdf.set_font('helvetica', '', 7.5); fill = False
    for u, st, diag in parque:
        pdf.set_fill_color(245, 245, 245) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(col_w[0], 7, f' {txt(u)}', border=1, fill=True)
        pdf.cell(col_w[1], 7, txt(st), border=1, align='C', fill=True)
        pdf.cell(col_w[2], 7, f' {txt(diag)}', border=1, new_x='LMARGIN', new_y='NEXT', fill=True)
        fill = not fill
        
    pdf.ln(6)
    pdf.subseccion_titulo('Consumo de Combustible e Insumos Medicos')
    pdf.p("El volumen de atenciones medicas provoco una rotacion acelerada de tanques de oxigeno medicinal, "
          "soluciones fisiologicas, collarines y material de curacion. Se sugiere etiquetar una partida presupuestal fija "
          "mensual para reposicion inmediata de insumos criticos.")

    # -------------------------------------------------------------
    # PAGINA 20: RECOMENDACIONES ESTRATEGICAS
    # -------------------------------------------------------------
    pdf.add_page()
    pdf.seccion_banner('X', 'RECOMENDACIONES ESTRATEGICAS Y PROSPECTIVA')
    pdf.p("Con base en la evidencia estadistica generada en este informe anual, se someten a consideracion de la "
          "Presidencia Municipal y del H. Cabildo las siguientes directrices prioritarias:")
    
    recoms = (
        "1. INSTALACION DE SUB-ESTACION OPERATIVA EN PASO DEL TORO:\n"
        "Paso del Toro se consolida como el punto mas estrategico del municipio al converger de forma directa las Carreteras "
        "Federales 180 (Costera del Golfo) y 150 (Mexico-Veracruz). Instalar una sub-estacion operativa en este crucero garantiza una "
        "cobertura inmediata hacia el corredor rural, tramos de alta velocidad y un arribo expedito hacia El Tejar y Puente Moreno.\n\n"
        "2. PROGRAMA PERMANENTE DE PREVENCION MOTOCICLISTA:\n"
        "Con 381 accidentes de moto registrados en el año, es urgente coordinar con Transito Municipal campañas obligatorias de uso "
        "de casco certificado y regulacion de velocidad en vialidades inter-fraccionamientos.\n\n"
        "3. PROGRAMA PREVENTIVO DE LLUVIAS Y TEMPORALES:\n"
        "Dado que agosto y septiembre registraron alta actividad por agentes perturbadores hidrometeorologicos, se debe calendarizar "
        "anualmente el desazolve continuo de canales, limpieza de alcantarillas y poda preventiva de arbolado de riesgo antes del temporal.\n\n"
        "4. RENOVACION Y ADQUISICION DE UNA NUEVA AMBULANCIA:\n"
        "La alta carga de trabajo de la U-208 hace inminente contar con una unidad de reemplazo de modelo reciente para evitar "
        "paralizar el servicio de emergencias cuando una unidad entre a mantenimiento preventivo.\n\n"
        "5. ADQUISICION DE MOTOCICLETA EQUIPADA PARA PRIMER RESPONDIENTE:\n"
        "Adquisicion de una motocicleta debidamente equipada como unidad de atencion a primer respondiente para minimizar los tiempos "
        "de respuesta y realizar la valoracion de triage en sitio. Esta medida permitira optimizar sustancialmente los costos de "
        "gasolina y reducir el tiempo de arribo derivado de las atenciones en Puente Moreno y Arboledas San Ramon, donde se concentra "
        "la mayor densidad de poblacion del municipio."
    )
    pdf.p(recoms)

    # -------------------------------------------------------------
    # PAGINA 21: HOJA DE FIRMAS INSTITUCIONAL
    # -------------------------------------------------------------
    pdf.add_page()
    pdf.seccion_banner('XI', 'VALIDACION INSTITUCIONAL Y RESPONSABILIDADES')
    pdf.p("El presente Informe de Gestion y Analitica Operativa Anual 2026 ha sido elaborado conforme a las normas "
          "tecnicas de proteccion civil y validado por la Direccion de la corporacion.")
    
    pdf.ln(35)
    # Cuadros de firmas
    y_firmas = pdf.get_y()
    
    pdf.set_draw_color(10, 35, 66)
    pdf.set_line_width(0.8)
    pdf.line(40, y_firmas, 170, y_firmas)
    
    pdf.set_xy(40, y_firmas + 4)
    pdf.set_font('helvetica', 'B', 12)
    pdf.set_text_color(10, 35, 66)
    pdf.cell(130, 6, 'LIC. DANIEL EDUARDO ROMERO PILAR', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('helvetica', '', 10)
    pdf.set_text_color(70, 70, 70)
    pdf.cell(0, 5, 'Director de Proteccion Civil y Bomberos Municipales', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 5, 'H. Ayuntamiento de Medellin de Bravo, Veracruz', align='C', new_x='LMARGIN', new_y='NEXT')
    
    pdf.ln(25)
    pdf.set_font('helvetica', 'I', 9)
    pdf.set_text_color(130, 130, 130)
    pdf.cell(0, 5, 'Documento oficial generado con telemetria de despacho y analitica avanzada.', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 5, 'Medellin de Bravo, Ver., a 11 de Septiembre de 2026.', align='C', new_x='LMARGIN', new_y='NEXT')

    # Guardar en ambas ubicaciones
    os.makedirs('Documentacion', exist_ok=True)
    os.makedirs('pdf', exist_ok=True)
    
    out_doc = 'Documentacion/Informe_Anual_Operativo_2026_PC_Medellin.pdf'
    out_pdf = 'pdf/Informe_Anual_Operativo_2026_PC_Medellin.pdf'
    
    pdf.output(out_doc)
    pdf.output(out_pdf)
    print(f"\n=======================================================")
    print(f"  INFORME ANUAL MAESTRO GENERADO EXITOSAMENTE (21 PAGINAS)")
    print(f"  Guardado en: {out_doc}")
    print(f"  Guardado en: {out_pdf}")
    print(f"=======================================================")

if __name__ == '__main__':
    df = cargar_datos()
    generar_todas_las_graficas(df)
    compilar_pdf_anual(df)
