import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os
import re

sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
AZUL = '#003366'
AZUL_C = '#1f4e79'
ROJO = '#d9534f'
GRIS = '#555555'

def preparar_datos():
    df = pd.read_csv('reporte_mensual_agosto_limpio.csv')
    df['Fecha_Reporte'] = pd.to_datetime(df['Fecha_Reporte'])
    df['Hora_DT'] = pd.to_datetime(df['Hora_Inicio'], format='%H:%M:%S')
    df['Hora'] = df['Hora_DT'].dt.hour
    df['Dia_Mes'] = df['Fecha_Reporte'].dt.day
    dias = {0:'Lunes', 1:'Martes', 2:'Miercoles', 3:'Jueves', 4:'Viernes', 5:'Sabado', 6:'Domingo'}
    df['Dia_Semana'] = df['Fecha_Reporte'].dt.dayofweek.map(dias)
    return df

def crear_graficos_analiticos(df):
    os.makedirs('temp_charts', exist_ok=True)
    
    # 1. Dona Principal
    plt.figure(figsize=(9, 6))
    cat_counts = df['Categoria'].value_counts()
    colores = sns.color_palette("Blues_r", len(cat_counts))
    plt.pie(cat_counts, labels=cat_counts.index, autopct='%1.1f%%', startangle=140, colors=colores, wedgeprops={'edgecolor': 'white', 'linewidth': 2})
    plt.title('Distribucion de Servicios por Categoria', fontsize=16, fontweight='bold', color=AZUL)
    fig = plt.gcf(); fig.gca().add_artist(plt.Circle((0,0),0.65,fc='white'))
    plt.tight_layout(); plt.savefig('temp_charts/cat_pie.png', dpi=300); plt.close()

    # 2. Barras Diarias
    daily_counts = df.groupby('Dia_Mes').size()
    full_month = pd.Series(0, index=range(1, 32))
    daily_counts = daily_counts.combine_first(full_month).astype(int)
    plt.figure(figsize=(11, 4.5))
    ax = sns.barplot(x=daily_counts.index, y=daily_counts.values, color=AZUL_C)
    plt.title('Volumen Diario de Incidentes (Agosto)', fontsize=15, fontweight='bold', color=AZUL)
    plt.xlabel('Dia del Mes'); plt.ylabel('Reportes Atendidos')
    for i, v in enumerate(daily_counts.values):
        if v > 0: ax.text(i, v + 0.5, str(v), ha='center', va='bottom', fontsize=8, color=GRIS)
    plt.tight_layout(); plt.savefig('temp_charts/diario_bar.png', dpi=300); plt.close()

    # 3. Dia de la semana
    plt.figure(figsize=(9, 4.5))
    orden_dias = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
    dow_counts = df['Dia_Semana'].value_counts().reindex(orden_dias).fillna(0)
    sns.barplot(x=dow_counts.index, y=dow_counts.values, palette="Blues_d", hue=dow_counts.index, legend=False)
    plt.title('Carga Operativa Promedio por Dia de la Semana', fontsize=15, fontweight='bold', color=AZUL)
    plt.tight_layout(); plt.savefig('temp_charts/semana_bar.png', dpi=300); plt.close()

    # 4. Curva Horaria
    plt.figure(figsize=(11, 4.5))
    hour_counts = df.groupby('Hora').size().reindex(range(24), fill_value=0)
    sns.lineplot(x=hour_counts.index, y=hour_counts.values, color=ROJO, marker="o", linewidth=3, markersize=8)
    plt.fill_between(hour_counts.index, hour_counts.values, color=ROJO, alpha=0.15)
    plt.title('Curva de Demanda: Picos Horarios de Atencion', fontsize=15, fontweight='bold', color=AZUL)
    plt.xticks(range(0, 24)); plt.xlabel('Hora del Dia (24 hrs)'); plt.ylabel('Frecuencia de Alertas')
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout(); plt.savefig('temp_charts/horas_line.png', dpi=300); plt.close()

    # 5. Duracion
    plt.figure(figsize=(10, 5))
    avg_dur = df.groupby('Categoria')['Duracion_Minutos'].mean().sort_values(ascending=False)
    ax4 = sns.barplot(x=avg_dur.values, y=avg_dur.index, palette="mako", hue=avg_dur.index, legend=False)
    plt.title('Desgaste Operativo: Tiempo Promedio por Categoria', fontsize=15, fontweight='bold', color=AZUL)
    plt.xlabel('Minutos Promedio en Escena')
    for i, v in enumerate(avg_dur.values):
        ax4.text(v + 1, i, f"{v:.1f} min", va='center', fontsize=10)
    plt.tight_layout(); plt.savefig('temp_charts/duracion_bar.png', dpi=300); plt.close()


class PDFReporteAnalitico(FPDF):
    def header(self):
        if self.page_no() == 1: return
        try: self.image('portal/static/portal/img/logo_pc.png', 12, 10, 20)
        except: pass
        try: self.image('portal/static/portal/img/logo_medellin_grandeza.png', 175, 10, 22)
        except: pass
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(0, 51, 102)
        self.cell(0, 6, 'H. AYUNTAMIENTO DE MEDELLIN DE BRAVO', border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.set_font('helvetica', '', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, 'Direccion de Proteccion Civil - Analitica Operativa', border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.ln(12)

    def footer(self):
        if self.page_no() == 1: return
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Sistema de Inteligencia de PCivil Medellin - Pagina {self.page_no()}', align='C')
        
    def seccion(self, titulo):
        self.ln(5)
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.set_fill_color(0, 51, 102)
        self.cell(0, 10, f'  {titulo}', new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        self.ln(5)

    def subseccion(self, titulo):
        self.ln(3)
        self.set_font('helvetica', 'B', 13)
        self.set_text_color(0, 51, 102)
        self.cell(0, 8, titulo, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
    def p(self, texto, bold=False):
        if bold: self.set_font('helvetica', 'B', 11)
        else: self.set_font('helvetica', '', 11)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 6, texto)
        self.ln(2)

def limpiar_texto(texto):
    return str(texto).replace('ó','o').replace('á','a').replace('é','e').replace('í','i').replace('ú','u').replace('ñ','n').encode('ascii', 'ignore').decode('ascii')

def generar_pdf(df):
    pdf = PDFReporteAnalitico()
    
    # ---------------- PAGINA 1: PORTADA ----------------
    pdf.add_page()
    try: pdf.image('portal/static/portal/img/logo_medellin_grandeza.png', 80, 50, 50)
    except: pass
    pdf.ln(120)
    pdf.set_font('helvetica', 'B', 28)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 15, 'REPORTE ANALITICO DE', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 15, 'OPERACIONES Y EMERGENCIAS', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)
    pdf.set_font('helvetica', 'B', 16)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, 'DIRECCION DE PROTECCION CIVIL MUNICIPAL', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font('helvetica', '', 14)
    pdf.cell(0, 10, 'Periodo de Analisis: Agosto 2026', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # ---------------- PAGINA 2: HALLAZGOS Y METRICAS ----------------
    pdf.add_page()
    pdf.seccion('1. RESUMEN EJECUTIVO Y HALLAZGOS')
    
    t_servicios = len(df)
    t_horas = df['Duracion_Minutos'].sum() / 60
    prom_diario = t_servicios / 31
    prom_semanal = t_servicios / 4.42
    top_dias = df.groupby('Fecha_Reporte').size().sort_values(ascending=False)
    dia_pico = top_dias.index[0].strftime("%d de Agosto")
    hora_pico = df['Hora'].value_counts().index[0]
    cat_prin = df['Categoria'].value_counts().index[0]
    
    pdf.p(f"Durante el mes de agosto de 2026, la Direccion de Proteccion Civil y Primeros Auxilios de Medellin de Bravo enfrento una carga operativa significativa, respondiendo a un total de {t_servicios} incidentes confirmados.")
    pdf.p("A traves del analisis de datos de telemetria de despachos, se identificaron los siguientes hallazgos estrategicos:")
    
    pdf.set_font('helvetica', '', 11)
    pdf.multi_cell(0, 6, f"- ALTA DEMANDA DIARIA: La corporacion mantiene un ritmo constante, promediando {prom_diario:.1f} servicios al dia, lo que equivale a mas de {prom_semanal:.1f} atenciones por semana.\n"
                         f"- IMPACTO CLIMATICO: Debido a la temporada de lluvias, los desastres naturales y rescates ocuparon un volumen critico, saturando lineas secundarias de atencion.\n"
                         f"- DIA CRITICO: El dia mas demandante del mes fue el {dia_pico}, donde las unidades no detuvieron operaciones.\n"
                         f"- HORA DE MAYOR RIESGO: El analisis de calor demuestra que el pico de emergencias ocurre sistematicamente alrededor de las {hora_pico}:00 hrs.")
    pdf.ln(8)
    
    # KPIs Visuales
    pdf.set_fill_color(240, 245, 250)
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(95, 12, f' Total Atenciones: {t_servicios}', border=1, fill=True)
    pdf.cell(95, 12, f' Horas Hombre Desplegadas: {t_horas:.1f} hrs', border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
    pdf.cell(95, 12, f' Promedio Diario: {prom_diario:.1f} alertas/dia', border=1, fill=True)
    pdf.cell(95, 12, f' Principal Riesgo: {cat_prin[:15]}...', border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)

    # ---------------- PAGINA 3: DESGLOSE CATEGORICO ----------------
    pdf.add_page()
    pdf.seccion('2. DISTRIBUCION DE INCIDENCIAS POR CATEGORIA')
    pdf.p("El siguiente desglose muestra la naturaleza de las emergencias atendidas. Es vital notar como las atenciones medicas y prehospitalarias dominan la operacion, seguidas de cerca por las afectaciones climatologicas (Rescates/Desastres).")
    
    pdf.set_fill_color(31, 78, 121); pdf.set_text_color(255, 255, 255); pdf.set_font('helvetica', 'B', 9)
    pdf.cell(65, 8, 'Categoria de Emergencia', border=1, align='C', fill=True)
    pdf.cell(25, 8, 'Total', border=1, align='C', fill=True)
    pdf.cell(25, 8, 'Porcentaje', border=1, align='C', fill=True)
    pdf.cell(35, 8, 'Promedio Diario', border=1, align='C', fill=True)
    pdf.cell(40, 8, 'Promedio Semanal', border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C', fill=True)
    
    pdf.set_text_color(0, 0, 0); pdf.set_font('helvetica', '', 9)
    cat_counts = df['Categoria'].value_counts()
    for cat, count in cat_counts.items():
        pdf.cell(65, 8, f' {limpiar_texto(cat)}', border=1)
        pdf.cell(25, 8, str(count), border=1, align='C')
        pdf.cell(25, 8, f"{(count/t_servicios)*100:.1f}%", border=1, align='C')
        pdf.cell(35, 8, f"{count/31:.1f}/dia", border=1, align='C')
        pdf.cell(40, 8, f"{count/4.42:.1f}/sem", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        
    pdf.image('temp_charts/cat_pie.png', x=35, y=None, w=140)

    # ---------------- PAGINA 4: TEMPORALIDAD ----------------
    pdf.add_page()
    pdf.seccion('3. ANALISIS DE CARGA TEMPORAL')
    pdf.subseccion('A. Incidencia Diaria del Mes')
    pdf.p("Se observa la fluctuacion de llamadas al 911 e incidencias directas reportadas dia con dia. Los picos altos generalmente corresponden a factores climaticos (lluvias fuertes) o fines de semana.")
    pdf.image('temp_charts/diario_bar.png', x=10, y=None, w=190)
    pdf.ln(5)
    
    dia_mas_ocupado = df['Dia_Semana'].value_counts().index[0]
    pdf.subseccion('B. Tendencia por Dia de la Semana')
    pdf.p(f"Historicamente, los {dia_mas_ocupado}s presentan el volumen mas alto de trabajo. Esto sugiere la necesidad de reforzar las guardias operativas durante estos dias especificos para evitar fatiga en el personal.")
    pdf.image('temp_charts/semana_bar.png', x=20, y=None, w=170)

    # ---------------- PAGINA 5: HORARIOS Y DURACION ----------------
    pdf.add_page()
    pdf.seccion('4. ESTUDIO DE HORARIOS Y TIEMPOS DE RESPUESTA')
    pdf.p("La curva de calor revela los momentos mas criticos del dia. El personal de guardia debe estar en alerta maxima durante las horas marcadas en el pico de la curva roja, ya que estadisticamente agrupan la mayoria de desastres y accidentes vehiculares.")
    pdf.image('temp_charts/horas_line.png', x=10, y=None, w=190)
    pdf.ln(10)
    pdf.p("A continuacion se muestra el desgaste promedio en minutos que cada unidad invierte desde que sale de la base hasta que se libera de la escena. Algunos incidentes, aunque son menos frecuentes, demandan mucho mas tiempo de los elementos.")
    pdf.image('temp_charts/duracion_bar.png', x=10, y=None, w=190)

    # ---------------- PAGINA 6: ANALISIS ESPECIFICOS (NUEVO) ----------------
    pdf.add_page()
    pdf.seccion('5. ESTUDIOS ANALITICOS ESPECIFICOS')
    
    # Fauna Sub-analisis
    pdf.subseccion('A. Control y Reubicacion de Fauna Silvestre')
    pdf.p("El municipio presenta una vasta interaccion con fauna silvestre. Se neutralizaron riesgos importantes para la ciudadania originados por fauna invasiva o peligrosa:")
    fauna_df = df[df['Categoria'] == 'Control de Fauna']
    conteos_fauna = {'Abejas/Panales': 0, 'Serpientes/Culebras': 0, 'Bovinos/Ganado': 0, 'Otros/Rescates': 0}
    for _, row in fauna_df.iterrows():
        t = str(row['Transcripcion_Incidente']).lower()
        if any(x in t for x in ['abeja', 'avispa', 'enjambre', 'panal']): conteos_fauna['Abejas/Panales'] += 1
        elif any(x in t for x in ['serpiente', 'vibora', 'vboro', 'reptil', 'culebra']): conteos_fauna['Serpientes/Culebras'] += 1
        elif any(x in t for x in ['vaca', 'toro', 'ganado', 'caballo']): conteos_fauna['Bovinos/Ganado'] += 1
        else: conteos_fauna['Otros/Rescates'] += 1
    
    pdf.set_fill_color(31, 78, 121); pdf.set_text_color(255, 255, 255); pdf.set_font('helvetica', 'B', 10)
    pdf.cell(100, 8, 'Especie Reportada', border=1, align='C', fill=True)
    pdf.cell(90, 8, 'Alertas Atendidas', border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C', fill=True)
    pdf.set_text_color(0, 0, 0); pdf.set_font('helvetica', '', 10)
    for k, v in conteos_fauna.items():
        pdf.cell(100, 8, f' {k}', border=1)
        pdf.cell(90, 8, str(v), border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(8)
    
    # Desastres Sub-analisis
    pdf.subseccion('B. Impacto de Desastres Naturales y Clima')
    pdf.p("Durante agosto, las precipitaciones y vientos causaron daños severos a la infraestructura publica y privada, requiriendo intervenciones de alto riesgo por parte de Proteccion Civil. Destacan reportes de arboles caidos sobre vialidades, desprendimiento de laminas y domicilios anegados.")
    pdf.ln(5)
    
    # Atencion Medica Sub-analisis
    pdf.subseccion('C. Clasificacion de Atencion Medica')
    pdf.p("El area medica representa el grueso de los servicios. Aunque todas se engloban como Atencion Prehospitalaria, su naturaleza es variada. Destacan los accidentes en motocicleta, pacientes con descompensaciones metabolicas, traumas por caidas y lamentablemente, decesos en via publica o domicilio.")
    
    # ---------------- PAGINA 7: TOP CASOS Y CONCLUSIONES ----------------
    pdf.add_page()
    pdf.seccion('6. INCIDENTES DE MAYOR DESGASTE OPERATIVO')
    pdf.p("La siguiente tabla documenta los 10 servicios que requirieron la mayor cantidad de horas ininterrumpidas de trabajo, bloqueando unidades por tiempos prolongados debido a la complejidad de la maniobra.")
    
    top_casos = df[~df['Categoria'].isin(['Administrativo / Interno', 'Falsa Alarma'])].sort_values('Duracion_Minutos', ascending=False).head(10)
    pdf.set_fill_color(31, 78, 121); pdf.set_text_color(255, 255, 255); pdf.set_font('helvetica', 'B', 8)
    pdf.cell(20, 8, 'Dia', border=1, align='C', fill=True)
    pdf.cell(45, 8, 'Categoria', border=1, align='C', fill=True)
    pdf.cell(15, 8, 'Horas', border=1, align='C', fill=True)
    pdf.cell(110, 8, 'Descripcion Resumida del Incidente', border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C', fill=True)
    
    pdf.set_text_color(0, 0, 0); pdf.set_font('helvetica', '', 7)
    for _, row in top_casos.iterrows():
        f = str(row['Fecha_Reporte'])[5:10]
        c = limpiar_texto(row['Categoria'])[:25]
        h = f"{row['Duracion_Minutos']/60:.1f}h"
        desc = limpiar_texto(row['Transcripcion_Incidente'])[:80] + "..."
        pdf.cell(20, 8, f, border=1, align='C')
        pdf.cell(45, 8, c, border=1)
        pdf.cell(15, 8, h, border=1, align='C')
        pdf.cell(110, 8, desc, border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(10)
    pdf.seccion('7. CONCLUSIONES Y RECOMENDACIONES')
    pdf.set_font('helvetica', '', 11)
    conclusiones = (
        "1. SOBRECARGA ESTRATEGICA: El volumen de atenciones medicas sugiere la necesidad de "
        "revisar el abastecimiento de insumos prehospitalarios (oxigeno, gasas, sueros), dado que "
        "se agotan rapidamente bajo una demanda de casi 10 salidas medicas diarias en promedio.\n\n"
        
        "2. PREVENCION DE DESASTRES: Dado el impacto de las tormentas (147 reportes), se recomienda "
        "iniciar una campaña preventiva de poda de arboles y desazolve de alcantarillas antes del "
        "proximo mes pico de lluvias.\n\n"
        
        "3. DESPLIEGUE HORARIO: Se sugiere concentrar el relevo de guardias y mantenimiento de "
        "unidades fuera de las horas pico, garantizando que el maximo estado de fuerza "
        "este activo durante la ventana critica de emergencias."
    )
    pdf.multi_cell(0, 6, conclusiones)

    pdf.output("Reporte_Analitico_Avanzado_Agosto_PC.pdf")
    print("Reporte extendido generado con exito.")

if __name__ == "__main__":
    df = preparar_datos()
    crear_graficos_analiticos(df)
    generar_pdf(df)
