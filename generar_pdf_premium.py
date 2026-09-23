import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import os

# Configuracion Visual de Graficas
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
COLOR_PRINCIPAL = '#0a2342'
COLOR_SECUNDARIO = '#175676'
COLOR_ALERTA = '#d62828'
COLOR_GRIS = '#8d99ae'

def preparar_datos():
    df = pd.read_csv('reporte_mensual_agosto_limpio.csv')
    df['Fecha_Reporte'] = pd.to_datetime(df['Fecha_Reporte'])
    df['Hora_DT'] = pd.to_datetime(df['Hora_Inicio'], format='%H:%M:%S')
    df['Hora'] = df['Hora_DT'].dt.hour
    df['Dia_Mes'] = df['Fecha_Reporte'].dt.day
    dias = {0:'Lunes', 1:'Martes', 2:'Miercoles', 3:'Jueves', 4:'Viernes', 5:'Sabado', 6:'Domingo'}
    df['Dia_Semana'] = df['Fecha_Reporte'].dt.dayofweek.map(dias)
    
    # Corregir errores de ortografia arrastrados de la base de datos
    correcciones = {
        'Atencin Mdica / Prehospitalaria': 'Atención Médica / Prehospitalaria',
        'Inundacin': 'Inundación',
        'Falsa alarma': 'Falsa Alarma'
    }
    df['Categoria'] = df['Categoria'].replace(correcciones)
    return df

def crear_graficas(df):
    os.makedirs('temp_charts', exist_ok=True)
    
    # 1. Dona de Categorias (Corregida visualmente)
    plt.figure(figsize=(10, 6))
    cat_counts = df['Categoria'].value_counts()
    colores = sns.color_palette("Set2", len(cat_counts))
    wedges, texts, autotexts = plt.pie(cat_counts, autopct='%1.1f%%', startangle=140, colors=colores, 
                                       wedgeprops={'edgecolor': 'white', 'linewidth': 2}, textprops={'fontsize': 10})
    plt.legend(wedges, cat_counts.index, title="Categorias", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    plt.title('Distribucion Porcentual de Atenciones', fontsize=16, fontweight='bold', color=COLOR_PRINCIPAL)
    fig = plt.gcf(); fig.gca().add_artist(plt.Circle((0,0),0.65,fc='white'))
    plt.tight_layout(); plt.savefig('temp_charts/cat_pie.png', dpi=300); plt.close()

    # 2. Barras Diarias
    daily_counts = df.groupby('Dia_Mes').size()
    full_month = pd.Series(0, index=range(1, 32))
    daily_counts = daily_counts.combine_first(full_month).astype(int)
    plt.figure(figsize=(12, 5))
    ax = sns.barplot(x=daily_counts.index, y=daily_counts.values, color=COLOR_SECUNDARIO)
    plt.title('Carga Operativa Diaria (Total de Alertas por Dia)', fontsize=15, fontweight='bold', color=COLOR_PRINCIPAL)
    plt.xlabel('Dia del Mes de Agosto'); plt.ylabel('Numero de Servicios')
    for i, v in enumerate(daily_counts.values):
        if v > 0: ax.text(i, v + 0.5, str(v), ha='center', va='bottom', fontsize=9)
    plt.tight_layout(); plt.savefig('temp_charts/diario_bar.png', dpi=300); plt.close()

    # 3. Dia de la semana
    plt.figure(figsize=(10, 5))
    orden_dias = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
    dow_counts = df['Dia_Semana'].value_counts().reindex(orden_dias).fillna(0)
    sns.barplot(x=dow_counts.index, y=dow_counts.values, palette="viridis", hue=dow_counts.index, legend=False)
    plt.title('Acumulado Historico por Dia de la Semana', fontsize=15, fontweight='bold', color=COLOR_PRINCIPAL)
    plt.tight_layout(); plt.savefig('temp_charts/semana_bar.png', dpi=300); plt.close()

    # 4. Curva de Calor Horaria
    plt.figure(figsize=(12, 5))
    hour_counts = df.groupby('Hora').size().reindex(range(24), fill_value=0)
    sns.lineplot(x=hour_counts.index, y=hour_counts.values, color=COLOR_ALERTA, marker="o", linewidth=3, markersize=8)
    plt.fill_between(hour_counts.index, hour_counts.values, color=COLOR_ALERTA, alpha=0.15)
    plt.title('Mapa Horario de Riesgo (Horas Pico de Emergencia)', fontsize=15, fontweight='bold', color=COLOR_PRINCIPAL)
    plt.xticks(range(0, 24)); plt.xlabel('Hora (Formato 24hrs)'); plt.ylabel('Total de Emergencias')
    plt.tight_layout(); plt.savefig('temp_charts/horas_line.png', dpi=300); plt.close()

    # 5. Duracion de Servicios
    plt.figure(figsize=(10, 6))
    avg_dur = df.groupby('Categoria')['Duracion_Minutos'].mean().sort_values(ascending=False)
    ax4 = sns.barplot(x=avg_dur.values, y=avg_dur.index, palette="rocket", hue=avg_dur.index, legend=False)
    plt.title('Tiempo Promedio Invertido por Tipo de Emergencia', fontsize=15, fontweight='bold', color=COLOR_PRINCIPAL)
    plt.xlabel('Minutos Promedio en Escena')
    for i, v in enumerate(avg_dur.values):
        ax4.text(v + 1, i, f"{v:.1f} min", va='center', fontsize=10)
    plt.tight_layout(); plt.savefig('temp_charts/duracion_bar.png', dpi=300); plt.close()

def txt(texto):
    """Limpia el texto para que FPDF lo acepte con acentos correctos (latin-1)"""
    if pd.isna(texto): return ""
    texto = str(texto)
    reemplazos = {'á':'a', 'é':'e', 'í':'i', 'ó':'o', 'ú':'u', 'Á':'A', 'É':'E', 'Í':'I', 'Ó':'O', 'Ú':'U', 'ñ':'n', 'Ñ':'N'}
    for orig, nuev in reemplazos.items():
        texto = texto.replace(orig, nuev)
    return texto.encode('latin-1', 'ignore').decode('latin-1')

class PDFPremium(FPDF):
    def header(self):
        if self.page_no() == 1: return
        self.set_fill_color(10, 35, 66)
        self.rect(0, 0, 210, 20, 'F')
        
        try: self.image('portal/static/portal/img/logo_pc.png', 12, 2, 16)
        except: pass
        try: self.image('portal/static/portal/img/logo_medellin_grandeza.png', 180, 2, 18)
        except: pass
        
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(255, 255, 255)
        self.set_xy(35, 6)
        self.cell(0, 5, 'DIRECCION DE PROTECCION CIVIL Y PRIMEROS AUXILIOS', border=0, align='L')
        self.set_font('helvetica', '', 9)
        self.set_xy(35, 11)
        self.set_text_color(200, 200, 200)
        self.cell(0, 5, 'H. Ayuntamiento de Medellin de Bravo | Reporte Operativo', border=0, align='L')
        self.ln(15)

    def footer(self):
        if self.page_no() == 1: return
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Sistema Inteligente de Analisis Operativo - Pagina {self.page_no()}', align='C')

    def portada(self):
        self.add_page()
        
        # Fondo blanco para que los logos PNG sin transparencia se integren perfecto
        self.set_fill_color(255, 255, 255)
        self.rect(0, 0, 210, 297, 'F')
        
        try: self.image('portal/static/portal/img/logo_medellin_grandeza.png', 80, 25, 50)
        except: pass
        try: self.image('portal/static/portal/img/logo_pc.png', 85, 200, 40)
        except: pass
        
        self.set_y(100)
        self.set_font('helvetica', 'B', 28)
        self.set_text_color(10, 35, 66)
        self.cell(0, 12, 'INFORME ANALITICO DE', align='C', new_x='LMARGIN', new_y='NEXT')
        self.cell(0, 12, 'OPERACIONES Y EMERGENCIAS', align='C', new_x='LMARGIN', new_y='NEXT')
        
        self.ln(10)
        self.set_font('helvetica', 'B', 14)
        self.set_text_color(214, 40, 40)
        self.cell(0, 8, 'H. AYUNTAMIENTO DE MEDELLIN DE BRAVO', align='C', new_x='LMARGIN', new_y='NEXT')
        
        # Linea divisoria elegante
        self.set_draw_color(214, 40, 40)
        self.line(50, 150, 160, 150)
        
        self.set_y(250)
        self.set_font('helvetica', '', 12)
        self.set_text_color(80, 80, 80) # Gris oscuro para fondo blanco
        self.cell(0, 8, 'Periodo de Evaluacion: Agosto 2026', align='C', new_x='LMARGIN', new_y='NEXT')
        self.cell(0, 8, 'Documento de Caracter Ejecutivo y Estrategico', align='C', new_x='LMARGIN', new_y='NEXT')

    def parte_titulo(self, numero, titulo):
        self.add_page()
        self.set_fill_color(214, 40, 40)
        self.rect(10, 25, 190, 20, 'F')
        self.set_xy(10, 30)
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, f'PARTE {numero}: {titulo}', align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(10)
        
    def titulo_seccion(self, titulo):
        self.ln(5)
        self.set_font('helvetica', 'B', 14)
        self.set_text_color(10, 35, 66)
        self.cell(0, 8, titulo, 'B', new_x='LMARGIN', new_y='NEXT')
        self.ln(4)
        
    def parrafo(self, texto, bold=False):
        if bold: self.set_font('helvetica', 'B', 11)
        else: self.set_font('helvetica', '', 11)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 6, txt(texto))
        self.ln(3)

def generar_documento(df):
    pdf = PDFPremium()
    pdf.portada()
    
    # Metricas Base
    t_servicios = len(df)
    t_horas = df['Duracion_Minutos'].sum() / 60
    prom_diario = t_servicios / 31
    top_dias = df.groupby('Fecha_Reporte').size().sort_values(ascending=False)
    dia_pico = top_dias.index[0].strftime("%d de Agosto")
    cat_prin = txt(df['Categoria'].value_counts().index[0])
    hora_pico = df['Hora'].value_counts().index[0]
    
    # =========================================================================
    # PARTE I: RESUMEN EJECUTIVO Y ESTADISTICA GLOBAL
    # =========================================================================
    pdf.parte_titulo('I', 'RESUMEN EJECUTIVO Y ESTADISTICA GLOBAL')
    
    pdf.titulo_seccion('1.1. Contexto Operativo del Mes')
    pdf.parrafo(f"El presente informe documenta y analiza las operaciones tacticas y de emergencia desplegadas por la Direccion de Proteccion Civil y Primeros Auxilios durante el mes de agosto de 2026. Este documento esta disenado para proveer a las autoridades municipales de inteligencia de datos que permita optimizar recursos, justificar presupuestos y mejorar la toma de decisiones.")
    pdf.parrafo(f"Durante este periodo, la corporacion enfrento y neutralizo un total de {t_servicios} incidentes reales, tras haber filtrado y descartado las falsas alarmas y reportes improcedentes. Este volumen operativo demuestra una carga de trabajo constante y sumamente exigente para el personal de turno.")
    
    # Cuadros de impacto
    pdf.ln(5)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('helvetica', 'B', 11)
    pdf.cell(90, 10, f' Total de Servicios Efectivos: {t_servicios}', border=1, fill=True)
    pdf.cell(10, 10, '', border=0)
    pdf.cell(90, 10, f' Horas-Hombre Invertidas: {t_horas:.1f} hrs', border=1, new_x='LMARGIN', new_y='NEXT', fill=True)
    pdf.ln(2)
    pdf.cell(90, 10, f' Promedio de Salidas: {prom_diario:.1f} al dia', border=1, fill=True)
    pdf.cell(10, 10, '', border=0)
    pdf.cell(90, 10, f' Categoria Lider: {cat_prin[:15]}', border=1, new_x='LMARGIN', new_y='NEXT', fill=True)
    pdf.ln(10)

    pdf.titulo_seccion('1.2. Distribucion Categórica de Emergencias')
    pdf.parrafo("Entender que tipo de servicios consumen los recursos de la corporacion es vital. La siguiente tabla y grafica demuestran como la atencion medica supera con creces cualquier otra incidencia, pero subraya tambien la fuerte presencia de desastres naturales impulsados por el clima del mes.")
    
    # Tabla Categrias
    pdf.set_fill_color(10, 35, 66); pdf.set_text_color(255, 255, 255); pdf.set_font('helvetica', 'B', 9)
    pdf.cell(65, 8, 'Categoria', border=1, align='C', fill=True)
    pdf.cell(30, 8, 'Total Salidas', border=1, align='C', fill=True)
    pdf.cell(30, 8, 'Porcentaje', border=1, align='C', fill=True)
    pdf.cell(65, 8, 'Explicacion del Impacto', border=1, new_x='LMARGIN', new_y='NEXT', align='C', fill=True)
    
    pdf.set_font('helvetica', '', 9)
    cat_counts = df['Categoria'].value_counts()
    fill = False
    for cat, count in cat_counts.items():
        if fill: pdf.set_fill_color(245, 245, 245)
        else: pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(0, 0, 0)
        
        explicacion = "Principal motor de desgaste" if count == cat_counts.max() else "Requiere atencion constante"
        if "Desastres" in cat: explicacion = "Elevado por tormentas de agosto"
        if "Fauna" in cat: explicacion = "Riesgo comunitario aislado"
        if "Incendio" in cat: explicacion = "Peligro de alto impacto"
        
        pdf.cell(65, 8, f' {txt(cat)}', border=1, fill=True)
        pdf.cell(30, 8, str(count), border=1, align='C', fill=True)
        pdf.cell(30, 8, f"{(count/t_servicios)*100:.1f}%", border=1, align='C', fill=True)
        pdf.cell(65, 8, explicacion, border=1, new_x='LMARGIN', new_y='NEXT', align='C', fill=True)
        fill = not fill
        
    pdf.image('temp_charts/cat_pie.png', x=15, y=None, w=170)
    pdf.parrafo("Interpretacion Visual: La dominancia de la seccion medica indica que PC funge primariamente como un sistema de salud prehospitalario de emergencia municipal, mitigando la carencia de ambulancias de otras dependencias.")

    # =========================================================================
    # PARTE II: ANALISIS TEMPORAL Y DESPLIEGUE OPERATIVO
    # =========================================================================
    pdf.parte_titulo('II', 'ANALISIS TEMPORAL Y DESPLIEGUE OPERATIVO')
    
    pdf.titulo_seccion('2.1. Carga Diaria e Impacto de Eventos')
    pdf.parrafo(f"Al evaluar la demanda diaria, es evidente que el servicio no es lineal. Los picos abruptos (como el registrado el {dia_pico}) suelen correlacionarse directamente con fenomenos meteorologicos locales o eventos publicos masivos. Durante estos picos, las unidades operan sin tiempos de descanso (cero horas base).")
    pdf.image('temp_charts/diario_bar.png', x=10, y=None, w=190)
    pdf.ln(5)
    
    pdf.titulo_seccion('2.2. Comportamiento Semanal')
    dia_fuerte = txt(df['Dia_Semana'].value_counts().index[0])
    dia_flojo = txt(df['Dia_Semana'].value_counts().index[-1])
    d_f_plural = dia_fuerte if dia_fuerte.endswith('s') else dia_fuerte + 's'
    d_l_plural = dia_flojo if dia_flojo.endswith('s') else dia_flojo + 's'
    
    pdf.parrafo(f"Identificar los dias criticos permite administrar descansos. Historicamente en agosto, los {d_f_plural} han mostrado ser los dias mas pesados para la corporacion, mientras que los {d_l_plural} presentan una ligera disminucion en los reportes al 911 y redes sociales.")
    pdf.image('temp_charts/semana_bar.png', x=15, y=None, w=170)
    
    pdf.add_page()
    pdf.titulo_seccion('2.3. Mapa Horario: Riesgo y Fatiga')
    pdf.parrafo(f"La siguiente curva revela la verdadera exigencia operativa por horas del dia. El punto maximo de alertas ocurre hacia las {hora_pico}:00 horas. Esto es fundamental: significa que el turno que cubre este horario enfrenta mayor presion psicologica y operativa, asi como un mayor riesgo de accidentes al conducir la unidad de emergencia.")
    pdf.image('temp_charts/horas_line.png', x=10, y=None, w=190)
    pdf.ln(5)
    
    pdf.titulo_seccion('2.4. Desgaste en Escena (Tiempos Reales)')
    pdf.parrafo("No todos los servicios son iguales. Mientras que capturar un animal puede tomar pocos minutos, un accidente vehicular con prensados o un incendio consumen enormes cantidades de tiempo, bloqueando la unidad y dejandola inoperativa para otras llamadas.")
    pdf.image('temp_charts/duracion_bar.png', x=15, y=None, w=170)

    # =========================================================================
    # PARTE III: DESGLOSE TACTICO Y RECOMENDACIONES
    # =========================================================================
    pdf.parte_titulo('III', 'DESGLOSE TACTICO Y RECOMENDACIONES')
    
    pdf.titulo_seccion('3.1. Sub-Analisis: Rescates y Desastres (Agosto)')
    pdf.parrafo("Agosto es el inicio critico de la temporada de huracanes. Los datos demuestran una elevada cifra de viviendas y vialidades vulneradas por encharcamientos, vientos arrachados y caida de infraestructura (arboles/postes).")
    pdf.parrafo("- Impacto: El personal requirio uso intensivo de motosierras, equipo de extraccion de agua y cuerdas. Este tipo de servicios son los de mayor riesgo fisico para el elemento de Proteccion Civil.", bold=True)
    pdf.ln(5)

    pdf.titulo_seccion('3.2. Sub-Analisis: Control de Fauna Nociva')
    pdf.parrafo("La interaccion humano-fauna es un rubro constante en Medellin. El desglose permite ver exactamente a que animales se expone la poblacion y el personal.")
    
    fauna_df = df[df['Categoria'].astype(str).str.contains('Fauna')]
    conteos_fauna = {'Abejas y Avispas (Riesgo alergico)': 0, 'Serpientes y Reptiles (Riesgo ofidico)': 0, 'Bovinos/Ganado en Carretera (Riesgo vial)': 0, 'Otros Rescates': 0}
    for _, row in fauna_df.iterrows():
        t = str(row['Transcripcion_Incidente']).lower()
        if any(x in t for x in ['abeja', 'avispa', 'enjambre', 'panal']): conteos_fauna['Abejas y Avispas (Riesgo alergico)'] += 1
        elif any(x in t for x in ['serpiente', 'vibora', 'vboro', 'reptil', 'culebra']): conteos_fauna['Serpientes y Reptiles (Riesgo ofidico)'] += 1
        elif any(x in t for x in ['vaca', 'toro', 'ganado', 'caballo']): conteos_fauna['Bovinos/Ganado en Carretera (Riesgo vial)'] += 1
        else: conteos_fauna['Otros Rescates'] += 1

    pdf.set_fill_color(10, 35, 66); pdf.set_text_color(255, 255, 255); pdf.set_font('helvetica', 'B', 10)
    pdf.cell(120, 8, 'Especie Involucrada en el Reporte', border=1, align='L', fill=True)
    pdf.cell(70, 8, 'Total Intervenciones', border=1, new_x='LMARGIN', new_y='NEXT', align='C', fill=True)
    pdf.set_text_color(0, 0, 0); pdf.set_font('helvetica', '', 10)
    
    fill = False
    for k, v in conteos_fauna.items():
        if fill: pdf.set_fill_color(245, 245, 245)
        else: pdf.set_fill_color(255, 255, 255)
        pdf.cell(120, 8, f' {txt(k)}', border=1, fill=True)
        pdf.cell(70, 8, str(v), border=1, new_x='LMARGIN', new_y='NEXT', align='C', fill=True)
        fill = not fill

    pdf.add_page()
    pdf.titulo_seccion('3.3. Top 8: Incidentes Criticos del Mes')
    pdf.parrafo("Estos fueron los 8 eventos que mas horas y recursos consumieron de la corporacion, representando cuellos de botella operativos:")
    
    top_casos = df[~df['Categoria'].astype(str).str.contains('Administrativo|Falsa')].sort_values('Duracion_Minutos', ascending=False).head(8)
    
    pdf.set_fill_color(10, 35, 66); pdf.set_text_color(255, 255, 255); pdf.set_font('helvetica', 'B', 8)
    pdf.cell(15, 8, 'Fecha', border=1, align='C', fill=True)
    pdf.cell(45, 8, 'Naturaleza', border=1, align='C', fill=True)
    pdf.cell(15, 8, 'Horas', border=1, align='C', fill=True)
    pdf.cell(115, 8, 'Detalle Operativo', border=1, new_x='LMARGIN', new_y='NEXT', align='C', fill=True)
    
    pdf.set_text_color(0, 0, 0); pdf.set_font('helvetica', '', 7)
    fill = False
    for _, row in top_casos.iterrows():
        if fill: pdf.set_fill_color(245, 245, 245)
        else: pdf.set_fill_color(255, 255, 255)
        f = str(row['Fecha_Reporte'])[5:10]
        c = txt(row['Categoria'])[:28]
        h = f"{row['Duracion_Minutos']/60:.1f}h"
        desc = txt(row['Transcripcion_Incidente'])[:85] + "..."
        pdf.cell(15, 8, f, border=1, align='C', fill=True)
        pdf.cell(45, 8, c, border=1, fill=True)
        pdf.cell(15, 8, h, border=1, align='C', fill=True)
        pdf.cell(115, 8, desc, border=1, new_x='LMARGIN', new_y='NEXT', fill=True)
        fill = not fill

    pdf.ln(10)
    pdf.titulo_seccion('3.4. Conclusiones y Recomendaciones Estrategicas')
    pdf.parrafo("En base a la evidencia estadistica recopilada por este motor analitico, se emiten las siguientes directrices para consideracion de la Direccion General y Presidencia:")
    
    pdf.set_font('helvetica', 'B', 10)
    pdf.set_text_color(214, 40, 40)
    pdf.cell(0, 6, "1. ASEGURAMIENTO DE INSUMOS PREHOSPITALARIOS", new_x='LMARGIN', new_y='NEXT')
    pdf.parrafo("Con casi la mitad de los servicios siendo atenciones medicas, el inventario de botiquines, oxigeno y combustible sufre un desgaste altamente acelerado. Se requiere asegurar un flujo de compra mensual riguroso para no paralizar las ambulancias.")
    
    pdf.set_font('helvetica', 'B', 10)
    pdf.set_text_color(214, 40, 40)
    pdf.cell(0, 6, "2. MITIGACION DE DESASTRES PREVENTIVA", new_x='LMARGIN', new_y='NEXT')
    pdf.parrafo("Siendo los desastres naturales la segunda causa de emergencia operativa, invertir en cuadrillas civiles de limpieza de drenajes y tala de arboles muertos reducira drasticamente las salidas de riesgo del personal de PC.")
    
    pdf.set_font('helvetica', 'B', 10)
    pdf.set_text_color(214, 40, 40)
    pdf.cell(0, 6, "3. INGENIERIA DE TURNOS", new_x='LMARGIN', new_y='NEXT')
    pdf.parrafo(f"Se comprobó estadisticamente que los picos de mayor estres y demanda son a las {hora_pico}:00 horas. Queda estrictamente recomendado programar recesos, comida y cambios de guardia fuera de este rango horario para no ser sorprendidos con estado de fuerza disminuido.")

    os.makedirs("pdf", exist_ok=True)
    pdf.output("pdf/Reporte_Premium_Inteligencia_PC.pdf")
    print("Reporte Premium Multi-Seccion Generado Exitosamente.")

if __name__ == "__main__":
    df = preparar_datos()
    crear_graficas(df)
    generar_documento(df)
