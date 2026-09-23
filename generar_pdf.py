import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os
import re

sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'

def crear_graficos(df):
    os.makedirs('temp_charts', exist_ok=True)
    
    # 1. Grfico de Dona
    plt.figure(figsize=(8, 6))
    cat_counts = df['Categoria'].value_counts()
    colores = sns.color_palette("Blues_r", len(cat_counts)) # Colores ms institucionales
    
    plt.pie(cat_counts, labels=cat_counts.index, autopct='%1.1f%%', startangle=140, 
            colors=colores, wedgeprops={'edgecolor': 'white', 'linewidth': 2})
    plt.title('Distribución de Servicios por Categoría', fontsize=14, fontweight='bold', color='#003366')
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    plt.tight_layout()
    plt.savefig('temp_charts/categorias_pie.png', dpi=300)
    plt.close()

    # 2. Grfico de Barras (Forzar 31 das)
    df['Fecha_Reporte'] = pd.to_datetime(df['Fecha_Reporte'])
    df['Dia'] = df['Fecha_Reporte'].dt.day
    daily_counts = df.groupby('Dia').size()
    
    # Asegurar que aparezcan los 31 das del mes
    full_month = pd.Series(0, index=range(1, 32))
    daily_counts = daily_counts.combine_first(full_month).astype(int)
    
    plt.figure(figsize=(10, 4))
    ax = sns.barplot(x=daily_counts.index, y=daily_counts.values, color='#1f4e79')
    plt.title('Incidencia Diaria de Reportes (Agosto 2026)', fontsize=14, fontweight='bold', color='#003366')
    plt.xlabel('Día del Mes', fontsize=11)
    plt.ylabel('Cantidad de Reportes', fontsize=11)
    
    for i, v in enumerate(daily_counts.values):
        if v > 0:
            ax.text(i, v + 0.5, str(v), ha='center', va='bottom', fontsize=9)
        
    plt.tight_layout()
    plt.savefig('temp_charts/servicios_diarios.png', dpi=300)
    plt.close()

def analizar_fauna(df):
    fauna_df = df[df['Categoria'] == 'Control de Fauna']
    conteos = {'Abejas/Avispas': 0, 'Serpientes/Reptiles': 0, 'Perros/Gatos': 0, 'Ganado/Vacas': 0, 'Otros': 0}
    
    for _, row in fauna_df.iterrows():
        texto = str(row['Transcripcion_Incidente']).lower()
        if 'abeja' in texto or 'avispa' in texto or 'enjambre' in texto or 'panal' in texto:
            conteos['Abejas/Avispas'] += 1
        elif 'serpiente' in texto or 'vibora' in texto or 'vbora' in texto or 'culebra' in texto or 'reptil' in texto:
            conteos['Serpientes/Reptiles'] += 1
        elif 'perro' in texto or 'gato' in texto or 'canino' in texto or 'felino' in texto:
            conteos['Perros/Gatos'] += 1
        elif 'vaca' in texto or 'toro' in texto or 'ganado' in texto or 'caballo' in texto:
            conteos['Ganado/Vacas'] += 1
        else:
            conteos['Otros'] += 1
            
    return conteos

class PDF(FPDF):
    def header(self):
        # Logos ms pequeos e institucionales
        try:
            self.image('portal/static/portal/img/logo_pc.png', 12, 10, 22)
        except: pass
        
        try:
            self.image('portal/static/portal/img/logo_medellin_grandeza.png', 170, 10, 25)
        except: pass
        
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(0, 51, 102) # Azul Marino institucional
        self.cell(0, 8, 'H. AYUNTAMIENTO DE MEDELLÍN DE BRAVO', border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 6, 'DIRECCIÓN DE PROTECCIÓN CIVIL', border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        
        self.set_font('helvetica', '', 11)
        self.set_text_color(80, 80, 80)
        self.cell(0, 6, 'REPORTE ESTADÍSTICO MENSUAL DE OPERACIONES', border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.cell(0, 6, 'PERIODO: AGOSTO 2026', border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Documento Generado por el Sistema de Análisis PCivil - Página {self.page_no()}', align='C')

def generar_reporte_pdf():
    df = pd.read_csv('reporte_mensual_agosto_limpio.csv')
    crear_graficos(df)
    
    pdf = PDF()
    pdf.add_page()
    
    # --- SECCIN 1: MTRICAS GLOBALES ---
    pdf.set_font('helvetica', 'B', 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, '1. MÉTRICAS GLOBALES DE SERVICIO', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_fill_color(240, 240, 240)
    pdf.ln(2)
    
    total_servicios = len(df)
    promedio_diario = round(total_servicios / 31, 1) # Mes de 31 das
    
    pdf.set_font('helvetica', '', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(95, 8, f'  Total de Incidentes Atendidos: {total_servicios}', border=1, fill=True)
    pdf.cell(95, 8, f'  Promedio Diario de Salidas: {promedio_diario}', border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
    pdf.ln(5)
    
    # --- SECCIN 2: DESGLOSE POR CATEGORA (TABLA) ---
    pdf.set_font('helvetica', 'B', 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, '2. CLASIFICACIÓN DE INCIDENTES', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)
    
    # Tabla de categoras
    cat_counts = df['Categoria'].value_counts()
    
    pdf.set_fill_color(0, 51, 102)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(90, 8, 'Categoría de Emergencia', border=1, align='C', fill=True)
    pdf.cell(50, 8, 'Total de Salidas', border=1, align='C', fill=True)
    pdf.cell(50, 8, 'Porcentaje (%)', border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C', fill=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('helvetica', '', 10)
    
    for cat, count in cat_counts.items():
        cat_clean = str(cat).replace('ó','o').replace('á','a').replace('é','e').replace('í','i').replace('ú','u')
        pct = f"{(count / total_servicios) * 100:.1f}%"
        pdf.cell(90, 8, f'  {cat_clean}', border=1, align='L')
        pdf.cell(50, 8, str(count), border=1, align='C')
        pdf.cell(50, 8, pct, border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        
    pdf.ln(5)
    
    # Dona chart
    pdf.image('temp_charts/categorias_pie.png', x=40, y=None, w=130)
    
    pdf.add_page()
    
    # --- SECCIN 3: COMPORTAMIENTO DIARIO ---
    pdf.set_font('helvetica', 'B', 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, '3. INCIDENCIA DIARIA', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Agregar nota sobre los datos
    pdf.set_font('helvetica', 'I', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, '* Nota: Informe validado al cierre del mes (31 de Agosto).', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.image('temp_charts/servicios_diarios.png', x=10, y=None, w=190)
    pdf.ln(5)
    
    # --- SECCIN 4: ANLISIS ESPECFICO (FAUNA) ---
    pdf.set_font('helvetica', 'B', 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, '4. DESGLOSE DE ATENCIÓN: CONTROL DE FAUNA', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)
    
    fauna_stats = analizar_fauna(df)
    
    pdf.set_fill_color(31, 78, 121)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(100, 8, 'Tipo de Fauna', border=1, align='C', fill=True)
    pdf.cell(90, 8, 'Reportes Atendidos', border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C', fill=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('helvetica', '', 10)
    
    total_fauna = sum(fauna_stats.values())
    
    for tipo, cantidad in fauna_stats.items():
        pdf.cell(100, 8, f'  {tipo}', border=1, align='L')
        pdf.cell(90, 8, str(cantidad), border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(100, 8, '  TOTAL FAUNA', border=1, align='L')
    pdf.cell(90, 8, str(total_fauna), border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    
    pdf.ln(15)
    
    # --- SECCIN 5: ANLISIS ESPECFICO (MEDICO) ---
    pdf.set_font('helvetica', 'B', 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, '5. DESGLOSE DE ATENCIÓN: PREHOSPITALARIA', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)
    
    med_df = df[df['Categoria'] == 'Atencin Mdica / Prehospitalaria']
    pdf.set_font('helvetica', '', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 6, text=f"Durante el periodo se atendieron un total de {len(med_df)} incidentes mdicos o prehospitalarios. Esto representa la principal demanda operativa (excluyendo reportes generales).")
    
    pdf_filename = "Reporte_Institucional_Agosto_PCivil.pdf"
    pdf.output(pdf_filename)
    print(f"¡PDF Generado! {pdf_filename}")

if __name__ == "__main__":
    generar_reporte_pdf()
