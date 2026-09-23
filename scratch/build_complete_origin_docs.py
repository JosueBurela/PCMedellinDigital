import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.section import WD_SECTION, WD_ORIENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

import pandas as pd
import sqlite3
import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("Generando documentos completos y estructurados con todas las fuentes de origen...")

# =============================================================================
# 1. GENERAR EXCEL MAESTRO MULTI-HOJA (.xlsx)
# =============================================================================
excel_path = 'Documentacion/Registro_Nominal_Traslados_Exactos_2026.xlsx'
wb = openpyxl.Workbook()
wb.remove(wb.active) # Quitar hoja por defecto

# Estilos
f_tit = Font(name='Calibri', size=14, bold=True, color='0A2342')
f_sub = Font(name='Calibri', size=10, bold=True, color='D62828')
f_meta = Font(name='Calibri', size=9.5, italic=True, color='555555')
f_hdr = Font(name='Calibri', size=10, bold=True, color='FFFFFF')
fill_navy = PatternFill(start_color='0A2342', end_color='0A2342', fill_type='solid')
fill_alt = PatternFill(start_color='F4F6F8', end_color='F4F6F8', fill_type='solid')
fill_white = PatternFill(start_color='FFFFFF', end_color='FFFFFF', fill_type='solid')
b_thin = Border(
    left=Side(style='thin', color='D0D5DD'), right=Side(style='thin', color='D0D5DD'),
    top=Side(style='thin', color='D0D5DD'), bottom=Side(style='thin', color='D0D5DD')
)

# -----------------------------------------------------------------------------
# HOJA 1: RESUMEN EJECUTIVO Y FUENTES DE ORIGEN
# -----------------------------------------------------------------------------
ws1 = wb.create_sheet(title="01_Resumen_Fuentes_Origen")
ws1.views.sheetView[0].showGridLines = True

ws1['A1'] = "H. AYUNTAMIENTO DE MEDELLÍN DE BRAVO — DIRECCIÓN DE PROTECCIÓN CIVIL Y BOMBEROS"
ws1['A1'].font = f_sub
ws1['A2'] = "CONSOLIDACIÓN INTEGRAL DE AUXILIOS MÉDICOS Y TRASLADOS EN AMBULANCIA (2026)"
ws1['A2'].font = f_tit
ws1['A3'] = "Auditoría cruzada: Informes de 100 Días, Libretas Físicas Mayo-Julio, WhatsApp Operativo y Base Maestra Anual"
ws1['A3'].font = f_meta

ws1['A5'] = "1. TOTALES DE 'AUXILIOS Y TRASLADOS' SEGÚN FUENTES OFICIALES DE ORIGEN"
ws1['A5'].font = Font(name='Calibri', size=11, bold=True, color='0A2342')

headers_fuentes = ["Fuente de Origen / Documento", "Periodo Comprendido", "Total Servicios Registrados", "Unidades Involucradas", "Definición Institucional / Contexto"]
for c_i, h in enumerate(headers_fuentes, start=1):
    cell = ws1.cell(row=6, column=c_i, value=h)
    cell.font = f_hdr; cell.fill = fill_navy; cell.alignment = Alignment(horizontal='center', vertical='center')
    cell.border = b_thin
ws1.row_dimensions[6].height = 25

datos_fuentes = [
    ("Informe de 100 Días (R Antonio Rosas-Anel.docx)", "01 Ene - 05 Abr 2026", "589 Auxilios y Traslados", "U-208 (586), U-097 (3)", "Reporte oficial al Alcalde: Capacidad prehospitalaria y traslados sumada"),
    ("Reporte Estratégico (informe de resultados.docx)", "Enero - Febrero - Marzo", "1,075 Auxilios y Traslados", "U-208 (1,075), U-097 (Soporte)", "Capacidad médica institucional consolidada de ambulancias"),
    ("Libreta Física de Guardia (Servicios de mayo.pdf)", "01 Mayo - 31 Julio 2026", "437 Servicios de Ambulancia", "U-208, U-098, U-097", "212 traslados/auxilios efectivos + 225 valoraciones en sitio"),
    ("Bitácora Digital C5/Radio (whatsapp_messages.db)", "01 Agosto - 10 Sep 2026", "211 Despachos de Traslado", "U-208, U-098, U-097, U-096", "433 mensajes de hospital/traslado; 118 traslados a hospital efectivos"),
    ("GRAN TOTAL ANUAL 2026 (Base Maestra servicios_anuales_2026)", "01 Ene - 10 Sep 2026", "1,149 Atenciones Médicas", "Flota Completa de Ambulancias", "65.5% del total de las 1,753 emergencias de todo el año")
]

for r_i, row in enumerate(datos_fuentes, start=7):
    fill_row = fill_alt if r_i % 2 == 0 else fill_white
    for c_i, val in enumerate(row, start=1):
        cell = ws1.cell(row=r_i, column=c_i, value=val)
        cell.font = Font(name='Calibri', size=9.5)
        cell.fill = fill_row; cell.border = b_thin
        cell.alignment = Alignment(vertical='center', wrap_text=True)
        if c_i in [2, 3]: cell.alignment = Alignment(horizontal='center', vertical='center')
    ws1.row_dimensions[r_i].height = 22

col_w_1 = [35, 24, 28, 25, 45]
for idx, w in enumerate(col_w_1, start=1):
    ws1.column_dimensions[get_column_letter(idx)].width = w

# -----------------------------------------------------------------------------
# HOJA 2: BITÁCORA NOMINAL DE TRASLADOS CON PACIENTE Y DIAGNÓSTICO
# -----------------------------------------------------------------------------
ws2 = wb.create_sheet(title="02_Bitacora_Nominal_Pacientes")
ws2.views.sheetView[0].showGridLines = True

ws2['A1'] = "H. AYUNTAMIENTO DE MEDELLÍN DE BRAVO — DIRECCIÓN DE PROTECCIÓN CIVIL Y BOMBEROS"
ws2['A1'].font = f_sub
ws2['A2'] = "RELACIÓN DETALLADA DE TRASLADOS HOSPITALARIOS CON FICHA CLÍNICA FRAP (2026)"
ws2['A2'].font = f_tit

# Cargar los datos limpios directamente del excel
df_final = pd.read_excel('Documentacion/Registro_Nominal_Traslados_Exactos_2026.xlsx', skiprows=4)
col_rename = {
    'Fecha y Hora': 'fecha_hora',
    'Unidad': 'unidad',
    'Nombre del Paciente': 'paciente',
    'Edad': 'edad',
    'Por Qué (Diagnóstico / Motivo Clínico)': 'diagnostico',
    'A Dónde (Hospital Receptor)': 'hospital_destino',
    'Recibe / Triage': 'observaciones',
    'Lugar de Origen': 'origen'
}
df_final = df_final.rename(columns=col_rename)
df_final.index += 1

headers_nom = ["No.", "Fecha y Hora", "Unidad", "Nombre del Paciente", "Edad", "Por Qué (Diagnóstico / Motivo Clínico)", "A Dónde (Hospital Receptor)", "Recibe / Triage", "Lugar de Origen"]
for c_i, h in enumerate(headers_nom, start=1):
    cell = ws2.cell(row=4, column=c_i, value=h)
    cell.font = f_hdr; cell.fill = fill_navy; cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    cell.border = b_thin
ws2.row_dimensions[4].height = 26

for r_i, row in df_final.iterrows():
    row_num = r_i + 4
    vals = [
        r_i, row['fecha_hora'], row['unidad'], row['paciente'], row['edad'],
        row['diagnostico'], row['hospital_destino'], row['observaciones'], row['origen']
    ]
    fill_row = fill_alt if r_i % 2 == 0 else fill_white
    for c_i, v in enumerate(vals, start=1):
        cell = ws2.cell(row=row_num, column=c_i, value=v)
        cell.font = Font(name='Calibri', size=9.5); cell.fill = fill_row; cell.border = b_thin
        cell.alignment = Alignment(vertical='center', wrap_text=True)
        if c_i in [1, 2, 3, 5]: cell.alignment = Alignment(horizontal='center', vertical='center')
    ws2.row_dimensions[row_num].height = 22

col_w_2 = [6, 17, 13, 30, 12, 42, 36, 24, 28]
for idx, w in enumerate(col_w_2, start=1):
    ws2.column_dimensions[get_column_letter(idx)].width = w

ws2.freeze_panes = 'A5'
ws2.auto_filter.ref = f"A4:I{len(df_final)+4}"

wb.save(excel_path)
print(f"Excel maestro guardado en: {excel_path}")

# =============================================================================
# 2. GENERAR DOCUMENTO DE WORD (.docx) ESTRUCTURADO Y ELEGANTE
# =============================================================================
doc_path = 'Documentacion/Registro_Nominal_Traslados_Exactos_2026.docx'
doc = Document()

# Configurar en Orientación Horizontal (Landscape)
for section in doc.sections:
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width = Inches(11.0)
    section.page_height = Inches(8.5)
    section.top_margin = Inches(0.6)
    section.bottom_margin = Inches(0.6)
    section.left_margin = Inches(0.6)
    section.right_margin = Inches(0.6)

logo_path = 'Documentacion/logo_pc_oficial_clean.png'
if os.path.exists(logo_path):
    hp = doc.add_paragraph()
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    hrun = hp.add_run()
    hrun.add_picture(logo_path, width=Inches(0.9))
    hp.paragraph_format.space_after = Pt(2)

p_sub = doc.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_sub = p_sub.add_run("H. AYUNTAMIENTO DE MEDELLÍN DE BRAVO, VERACRUZ\nDIRECCIÓN DE PROTECCIÓN CIVIL Y BOMBEROS MUNICIPALES")
r_sub.font.name = 'Calibri'; r_sub.font.size = Pt(10); r_sub.font.bold = True; r_sub.font.color.rgb = RGBColor(214, 40, 40)
p_sub.paragraph_format.space_after = Pt(2)

p_tit = doc.add_paragraph()
p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_tit = p_tit.add_run("INFORME MAESTRO DE AUXILIOS MÉDICOS Y TRASLADOS EN AMBULANCIA (2026)")
r_tit.font.name = 'Calibri'; r_tit.font.size = Pt(13); r_tit.font.bold = True; r_tit.font.color.rgb = RGBColor(10, 35, 66)
p_tit.paragraph_format.space_after = Pt(2)

p_meta = doc.add_paragraph()
p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_meta = p_meta.add_run("Auditoría cruzada de todas las fuentes de origen (100 Días, Libretas Físicas de Campo, Bitácora C5 y Radio)\nDirector Titular: Lic. Daniel Eduardo Romero Pilar")
r_meta.font.name = 'Calibri'; r_meta.font.size = Pt(9); r_meta.font.italic = True; r_meta.font.color.rgb = RGBColor(100, 100, 100)
p_meta.paragraph_format.space_after = Pt(8)

# SECCIÓN 1: CUADRO COMPARATIVO DE FUENTES
h1 = doc.add_paragraph()
rh1 = h1.add_run("1. CONCENTRADO DE AUXILIOS Y TRASLADOS SEGÚN FUENTES OFICIALES DE ORIGEN")
rh1.font.name = 'Calibri'; rh1.font.size = Pt(11); rh1.font.bold = True; rh1.font.color.rgb = RGBColor(10, 35, 66)
h1.paragraph_format.space_after = Pt(4)

p_exp = doc.add_paragraph()
p_exp.paragraph_format.line_spacing = 1.15
p_exp.paragraph_format.space_after = Pt(6)
r_exp = p_exp.add_run(
    "Aclaración Metodológica: En la administración pública y en los informes estratégicos entregados al Presidente Municipal "
    "y a Cabildo, la rama médica se clasifica bajo el rubro global de 'Auxilios Prehospitalarios y Traslados'. Por ello, "
    "las fuentes de origen registran los siguientes volúmenes acumulados:"
)
r_exp.font.name = 'Calibri'; r_exp.font.size = Pt(9)

t_f = doc.add_table(rows=6, cols=5)
t_f.alignment = WD_TABLE_ALIGNMENT.CENTER
headers_tf = ["Fuente de Origen / Documento", "Periodo", "Volumen Reportado", "Unidades", "Contexto Operativo"]
for c_i, h in enumerate(headers_tf):
    cell = t_f.rows[0].cells[c_i]
    cell.paragraphs[0].text = h
    cell.paragraphs[0].runs[0].font.name = 'Calibri'; cell.paragraphs[0].runs[0].font.bold = True
    cell.paragraphs[0].runs[0].font.size = Pt(8.5); cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
    tcPr = cell._tc.get_or_add_tcPr(); tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="0A2342"/>'))

for r_i, row_d in enumerate(datos_fuentes, start=1):
    table_row = t_f.rows[r_i]
    bg_col = "F4F6F8" if r_i % 2 == 0 else "FFFFFF"
    for c_i, val in enumerate(row_d):
        cell = table_row.cells[c_i]
        p = cell.paragraphs[0]; p.text = str(val)
        p.paragraph_format.space_before = Pt(2); p.paragraph_format.space_after = Pt(2)
        for r in p.runs:
            r.font.name = 'Calibri'; r.font.size = Pt(8)
            if c_i == 2: r.font.bold = True; r.font.color.rgb = RGBColor(214, 40, 40)
            else: r.font.color.rgb = RGBColor(30, 30, 30)
        tcPr = cell._tc.get_or_add_tcPr(); tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg_col}"/>'))
        cell.width = Inches([2.5, 1.4, 1.8, 1.8, 2.3][c_i])

doc.add_paragraph().paragraph_format.space_after = Pt(8)

# SECCIÓN 2: BITÁCORA NOMINAL DETALLADA
h2 = doc.add_paragraph()
rh2 = h2.add_run("2. BITÁCORA NOMINAL Y DETALLADA DE TRASLADOS EN AMBULANCIA (CASOS CON FICHA CLÍNICA)")
rh2.font.name = 'Calibri'; rh2.font.size = Pt(11); rh2.font.bold = True; rh2.font.color.rgb = RGBColor(10, 35, 66)
h2.paragraph_format.space_after = Pt(4)

t_w = doc.add_table(rows=len(df_final) + 1, cols=6)
t_w.alignment = WD_TABLE_ALIGNMENT.CENTER

t_headers = ["No.", "Fecha y Hora", "Unidad", "Nombre del Paciente (Edad)", "Por Qué (Diagnóstico / Motivo)", "A Dónde (Hospital Receptor)"]
hdr_row = t_w.rows[0]
trPr = hdr_row._tr.get_or_add_trPr()
trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

for c_i, h in enumerate(t_headers):
    cell = hdr_row.cells[c_i]
    cell.paragraphs[0].text = h
    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER if c_i < 3 else WD_ALIGN_PARAGRAPH.LEFT
    cell.paragraphs[0].runs[0].font.name = 'Calibri'; cell.paragraphs[0].runs[0].font.bold = True
    cell.paragraphs[0].runs[0].font.size = Pt(8.5); cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
    tcPr = cell._tc.get_or_add_tcPr(); tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="0A2342"/>'))

for r_i, row in df_final.iterrows():
    table_row = t_w.rows[r_i]
    r_trPr = table_row._tr.get_or_add_trPr()
    r_trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
    
    vals = [
        str(r_i),
        str(row['fecha_hora']),
        str(row['unidad']),
        f"{row['paciente']}\n({row['edad']})",
        f"{row['diagnostico']}",
        f"{row['hospital_destino']}\nRecibe: {row['observaciones']}"
    ]
    bg_hex = "F4F6F8" if r_i % 2 == 0 else "FFFFFF"
    for c_i, v in enumerate(vals):
        cell = table_row.cells[c_i]
        p = cell.paragraphs[0]; p.text = v
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_i in [0, 1, 2] else WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(2); p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.05
        for run in p.runs:
            run.font.name = 'Calibri'; run.font.size = Pt(7.8); run.font.color.rgb = RGBColor(30, 30, 30)
        tcPr = cell._tc.get_or_add_tcPr(); tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg_hex}"/>'))
        cell.width = Inches([0.4, 1.2, 0.9, 2.3, 2.8, 2.2][c_i])

doc.save(doc_path)
print(f"Word guardado en: {doc_path}")

# =============================================================================
# 3. EXPORTAR PDF NATIVO DESDE WORD (0% ERRORES, MÁXIMA CALIDAD)
# =============================================================================
pdf_path = os.path.abspath('Documentacion/Registro_Nominal_Traslados_Exactos_2026.pdf')
doc_abs = os.path.abspath(doc_path)

try:
    import win32com.client
    word_app = win32com.client.Dispatch('Word.Application')
    word_app.Visible = False
    doc_opened = word_app.Documents.Open(doc_abs)
    doc_opened.SaveAs(pdf_path, FileFormat=17) # 17 = wdFormatPDF
    doc_opened.Close()
    word_app.Quit()
    print(f"PDF generado exitosamente desde Word COM! Tamaño: {os.path.getsize(pdf_path)} bytes")
except Exception as e:
    print("Error generando PDF vía Word COM:", e)

print("¡Proceso completado con éxito!")
