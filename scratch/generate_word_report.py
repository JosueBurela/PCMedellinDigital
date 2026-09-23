import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import os
import sqlite3
import pandas as pd

# Helpers de formato Word
def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_borders(cell, top="D0D5DD", bottom="D0D5DD", left="none", right="none"):
    tcPr = cell._tc.get_or_add_tcPr()
    b_xml = f'<w:tcBorders {nsdecls("w")}>'
    if top != "none": b_xml += f'<w:top w:val="single" w:sz="6" w:space="0" w:color="{top}"/>'
    else: b_xml += '<w:top w:val="none"/>'
    if bottom != "none": b_xml += f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="{bottom}"/>'
    else: b_xml += '<w:bottom w:val="none"/>'
    if left != "none": b_xml += f'<w:left w:val="single" w:sz="6" w:space="0" w:color="{left}"/>'
    else: b_xml += '<w:left w:val="none"/>'
    if right != "none": b_xml += f'<w:right w:val="single" w:sz="6" w:space="0" w:color="{right}"/>'
    else: b_xml += '<w:right w:val="none"/>'
    b_xml += '</w:tcBorders>'
    tcPr.append(parse_xml(b_xml))

def formatear_tabla(table, col_widths=None):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(table.rows):
        is_header = (r_idx == 0)
        is_total = (r_idx == len(table.rows) - 1 and "TOTAL" in row.cells[0].text.upper())
        bg_color = "0A2342" if is_header else ("E9ECEF" if is_total else ("F8F9FA" if r_idx % 2 == 1 else "FFFFFF"))
        
        for c_idx, cell in enumerate(row.cells):
            set_cell_background(cell, bg_color)
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            set_cell_borders(cell, top="0A2342" if is_total else "D0D5DD", bottom="0A2342" if (is_total or is_header) else "D0D5DD")
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            
            if col_widths and c_idx < len(col_widths):
                cell.width = Inches(col_widths[c_idx])
                
            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                for run in p.runs:
                    run.font.name = 'Calibri'
                    if is_header:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
                        run.font.size = Pt(9.5)
                    elif is_total:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(10, 35, 66)
                        run.font.size = Pt(9.5)
                    else:
                        run.font.color.rgb = RGBColor(40, 40, 40)
                        run.font.size = Pt(9)

def generar_documento_word():
    doc = Document()
    
    # Márgenes de página (2 cm aprox)
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)

    # 1. ENCABEZADO INSTITUCIONAL
    logo_path = 'Documentacion/logo_pc_oficial_clean.png'
    if os.path.exists(logo_path):
        header_p = doc.add_paragraph()
        header_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        header_run = header_p.add_run()
        header_run.add_picture(logo_path, width=Inches(1.2))
        header_p.paragraph_format.space_after = Pt(4)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("H. AYUNTAMIENTO DE MEDELLÍN DE BRAVO, VERACRUZ\nDIRECCIÓN DE PROTECCIÓN CIVIL Y BOMBEROS MUNICIPALES")
    r_sub.font.name = 'Calibri'
    r_sub.font.size = Pt(11)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(214, 40, 40)
    p_sub.paragraph_format.space_after = Pt(2)

    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_tit = p_tit.add_run("INFORME EJECUTIVO ANUAL DE EMERGENCIAS Y TRASLADOS EN AMBULANCIA 2026")
    r_tit.font.name = 'Calibri'
    r_tit.font.size = Pt(15)
    r_tit.font.bold = True
    r_tit.font.color.rgb = RGBColor(10, 35, 66)
    p_tit.paragraph_format.space_after = Pt(4)

    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_meta = p_meta.add_run("Periodo Operativo: 01 de Enero al 10 de Septiembre de 2026 | Director Titular: Lic. Daniel Eduardo Romero Pilar")
    r_meta.font.name = 'Calibri'
    r_meta.font.size = Pt(9.5)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(108, 117, 125)
    p_meta.paragraph_format.space_after = Pt(18)

    # LÍNEA DIVISORIA
    p_div = doc.add_paragraph()
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_div = p_div.add_run("―" * 60)
    r_div.font.color.rgb = RGBColor(208, 213, 221)
    p_div.paragraph_format.space_after = Pt(12)

    # =========================================================================
    # SECCIÓN 1: RESUMEN GENERAL DE EMERGENCIAS TRABAJADAS EN EL AÑO
    # =========================================================================
    h1 = doc.add_paragraph()
    r_h1 = h1.add_run("1. PANORAMA GENERAL DE EMERGENCIAS ANUALES (2026)")
    r_h1.font.name = 'Calibri'
    r_h1.font.size = Pt(12)
    r_h1.font.bold = True
    r_h1.font.color.rgb = RGBColor(10, 35, 66)
    h1.paragraph_format.space_after = Pt(6)

    p1 = doc.add_paragraph()
    p1.paragraph_format.line_spacing = 1.15
    p1.paragraph_format.space_after = Pt(10)
    r_p1 = p1.add_run(
        "A lo largo del presente ejercicio operativo 2026, la Dirección de Protección Civil y Bomberos del Municipio de "
        "Medellín de Bravo ha registrado y coordinado un volumen consolidado de "
    )
    r_p1.font.name = 'Calibri'; r_p1.font.size = Pt(10)
    
    r_p1_bold = p1.add_run("1,753 servicios y atenciones de emergencia")
    r_p1_bold.font.name = 'Calibri'; r_p1_bold.font.size = Pt(10); r_p1_bold.font.bold = True; r_p1_bold.font.color.rgb = RGBColor(214, 40, 40)

    r_p1_c = p1.add_run(
        ", distribuidos en las distintas áreas operativas (prehospitalaria, combate de incendios, control de fauna silvestre, "
        "contingencias hidrometeorológicas y apoyos comunitarios). La rama con mayor demanda de la población es la médica prehospitalaria, "
        "abarcando más de dos tercios de la actividad de la corporación."
    )
    r_p1_c.font.name = 'Calibri'; r_p1_c.font.size = Pt(10)

    # Tabla 1: Distribución por Rama Operativa
    t1 = doc.add_table(rows=8, cols=4)
    t1_headers = ["Categoría Macro Operativa", "Servicios Atendidos", "% del Total Anual", "Impacto Comunitario"]
    for c_i, h_text in enumerate(t1_headers):
        t1.rows[0].cells[c_i].paragraphs[0].text = h_text
        t1.rows[0].cells[c_i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER if c_i > 0 else WD_ALIGN_PARAGRAPH.LEFT

    t1_data = [
        ("Atención Médica / Prehospitalaria", "1,149", "65.54%", "Auxilios viales, caídas, partos y traslados"),
        ("Incendios (Pastizal, Vivienda, Fugas Gas)", "202", "11.52%", "Mitigación y combate por unidad bomberil"),
        ("Agentes Perturbadores / Climatológicos", "145", "8.27%", "Inundaciones, desazolves y retiro de árboles"),
        ("Control de Fauna (Abejas, Reptiles, Ganado)", "124", "7.07%", "Reubicación y neutralización de enjambres"),
        ("Servicios a la Comunidad / Pipas de Agua", "60", "3.42%", "Abastecimiento de agua y apoyo a eventos"),
        ("Accidentes Vehiculares (Choques Directos)", "48", "2.74%", "Abanderamiento vial y rescate automotriz"),
        ("TOTAL ANUAL DE SERVICIOS", "1,753", "100.0%", "Operatividad acumulada al 10 de Septiembre")
    ]

    for r_i, row_data in enumerate(t1_data, start=1):
        for c_i, val in enumerate(row_data):
            p = t1.rows[r_i].cells[c_i].paragraphs[0]
            p.text = val
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_i in [1, 2] else WD_ALIGN_PARAGRAPH.LEFT

    formatear_tabla(t1, [2.5, 1.3, 1.2, 2.0])
    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # =========================================================================
    # SECCIÓN 2: EXTRACCIÓN Y ANÁLISIS DE TRASLADOS EN AMBULANCIA
    # =========================================================================
    h2 = doc.add_paragraph()
    r_h2 = h2.add_run("2. EXTRACCIÓN Y DESGLOSE ANALÍTICO DE TRASLADOS REALIZADOS")
    r_h2.font.name = 'Calibri'
    r_h2.font.size = Pt(12)
    r_h2.font.bold = True
    r_h2.font.color.rgb = RGBColor(10, 35, 66)
    h2.paragraph_format.space_after = Pt(6)

    p2 = doc.add_paragraph()
    p2.paragraph_format.line_spacing = 1.15
    p2.paragraph_format.space_after = Pt(8)
    p2.add_run(
        "A solicitud expresa sobre el volumen específico de "
    )
    r_tr_b = p2.add_run("traslados de pacientes en ambulancia")
    r_tr_b.bold = True; r_tr_b.font.color.rgb = RGBColor(10, 35, 66)
    p2.add_run(
        ", el análisis técnico de las bases de datos maestras y de las bitácoras de guardia de las unidades U-208, U-098 y U-097 "
        "arroja dos niveles de información complementarios:\n\n"
        "• "
    )
    r_n1 = p2.add_run("Nivel 1 (Subtipo Oficial y Catálogo Maestro Anual): ")
    r_n1.bold = True
    p2.add_run(
        "En la clasificación estandarizada de la base de datos municipal se registraron formalmente "
    )
    r_n1_c = p2.add_run("43 traslados interhospitalarios programados")
    r_n1_c.bold = True; r_n1_c.font.color.rgb = RGBColor(214, 40, 40)
    p2.add_run(
        ", más 10 traslados de urgencia obstétrica/parto, sumando 53 traslados bajo etiqueta directa.\n"
        "• "
    )
    r_n2 = p2.add_run("Nivel 2 (Auditoría Integral de Salidas en Ambulancia y Transcripción de Guardias): ")
    r_n2.bold = True
    p2.add_run(
        "Al auditar los partes médicos FRAP y los reportes de cabina en tiempo real, se constatan "
    )
    r_n2_c = p2.add_run("118 intervenciones operativas con traslado efectivo a hospital o a domicilio por alta médica")
    r_n2_c.bold = True; r_n2_c.font.color.rgb = RGBColor(214, 40, 40)
    p2.add_run(
        ". En el resto de las atenciones médicas (aproximadamente el 65% a 70%), el paciente fue valorado, "
        "curado y estabilizado en el lugar sin requerir traslado, o bien firmó acta de deslinde/negativa voluntaria."
    )

    # Tabla 2: Centros Receptores de Traslado
    p_t2_tit = doc.add_paragraph()
    r_t2_tit = p_t2_tit.add_run("Tabla 2.1: Centros Hospitalarios y Receptores de Pacientes Trasladados")
    r_t2_tit.font.name = 'Calibri'; r_t2_tit.font.size = Pt(10); r_t2_tit.bold = True; r_t2_tit.font.color.rgb = RGBColor(10, 35, 66)
    p_t2_tit.paragraph_format.space_after = Pt(3)

    t2 = doc.add_table(rows=10, cols=4)
    t2_headers = ["Hospital / Centro Médico Receptor", "Traslados Auditados", "% de Traslados", "Perfil del Paciente Recibido"]
    for c_i, h_text in enumerate(t2_headers):
        t2.rows[0].cells[c_i].paragraphs[0].text = h_text
        t2.rows[0].cells[c_i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER if c_i in [1, 2] else WD_ALIGN_PARAGRAPH.LEFT

    t2_data = [
        ("Hospital General de Boca del Río", "37", "31.36%", "Urgencias de trauma, choques de moto, caídas y policontundidos"),
        ("IMSS Clínica 71 (Díaz Mirón)", "15", "12.71%", "Derechohabientes IMSS, fracturas expuestas y dolor precordial"),
        ("IMSS Hospital Cuauhtémoc / Clínica 61", "15", "12.71%", "Derivaciones médicas, medicina interna y altas programadas"),
        ("Hospital Regional de Alta Especialidad (Veracruz)", "7", "5.93%", "Traumatismo craneoencefálico severo y código rojo"),
        ("Torre Pediátrica de Veracruz", "5", "4.24%", "Urgencias pediátricas, convulsiones febriles y caídas de menores"),
        ("Hospital Naval de Alta Especialidad (HOSNAVER)", "3", "2.54%", "Personal naval o derechohabientes SEMAR con trauma/urgencia"),
        ("Centros Privados y Cruz Roja (D'María / Cruz Roja)", "5", "4.24%", "Pacientes con seguro médico particular o apoyo mutuo"),
        ("Traslados Asistidos a Domicilio (Altas Médicas)", "13", "11.02%", "Apoyo social a pacientes postquirúrgicos o con movilidad reducida"),
        ("Otros Hospitales / Clínicas de Zona", "18", "15.25%", "Clínicas locales y centros de salud de la conurbación")
    ]

    for r_i, row_data in enumerate(t2_data, start=1):
        for c_i, val in enumerate(row_data):
            p = t2.rows[r_i].cells[c_i].paragraphs[0]
            p.text = val
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_i in [1, 2] else WD_ALIGN_PARAGRAPH.LEFT

    formatear_tabla(t2, [2.5, 1.2, 1.2, 2.1])
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Tabla 3: Unidades de Ambulancia
    p_t3_tit = doc.add_paragraph()
    r_t3_tit = p_t3_tit.add_run("Tabla 2.2: Desglose Operativo por Unidad Móvil (Ambulancias)")
    r_t3_tit.font.name = 'Calibri'; r_t3_tit.font.size = Pt(10); r_t3_tit.bold = True; r_t3_tit.font.color.rgb = RGBColor(10, 35, 66)
    p_t3_tit.paragraph_format.space_after = Pt(3)

    t3 = doc.add_table(rows=4, cols=4)
    t3_headers = ["Unidad Móvil", "Tipo de Vehículo", "Servicios con Traslado", "Zona y Despliegue Principal"]
    for c_i, h_text in enumerate(t3_headers):
        t3.rows[0].cells[c_i].paragraphs[0].text = h_text
        t3.rows[0].cells[c_i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER if c_i == 2 else WD_ALIGN_PARAGRAPH.LEFT

    t3_data = [
        ("Ambulancia U-208", "Soporte Vital Avanzado", "58 traslados", "Traslados foráneos, clínicas IMSS, alta especialidad y zona rural"),
        ("Ambulancia U-098", "Soporte Básico / Cuadrantes", "54 traslados", "Puente Moreno, El Tejar, Arboledas y Boca del Río"),
        ("Ambulancia U-097", "Unidad RAM Reincorporada", "15 traslados", "Soporte a cuadrantes rurales y traslados de relevo")
    ]

    for r_i, row_data in enumerate(t3_data, start=1):
        for c_i, val in enumerate(row_data):
            p = t3.rows[r_i].cells[c_i].paragraphs[0]
            p.text = val
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_i == 2 else WD_ALIGN_PARAGRAPH.LEFT

    formatear_tabla(t3, [1.8, 1.8, 1.5, 1.9])
    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # =========================================================================
    # SECCIÓN 3: TABLA MENSUAL Y CONCLUSIONES
    # =========================================================================
    h3 = doc.add_paragraph()
    r_h3 = h3.add_run("3. CONCENTRADO MENSUAL ACUMULADO DEL AÑO 2026")
    r_h3.font.name = 'Calibri'
    r_h3.font.size = Pt(12)
    r_h3.font.bold = True
    r_h3.font.color.rgb = RGBColor(10, 35, 66)
    h3.paragraph_format.space_after = Pt(6)

    t4 = doc.add_table(rows=11, cols=6)
    t4_headers = ["Mes", "Servicios Totales", "Atenciones Médicas", "Traslados Directos", "Efectividad Operativa", "% Anual"]
    for c_i, h_text in enumerate(t4_headers):
        t4.rows[0].cells[c_i].paragraphs[0].text = h_text
        t4.rows[0].cells[c_i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER if c_i > 0 else WD_ALIGN_PARAGRAPH.LEFT

    t4_data = [
        ("Enero", "210", "137", "18*", "91.4%", "12.0%"),
        ("Febrero", "190", "124", "15*", "88.9%", "10.8%"),
        ("Marzo", "210", "138", "19*", "90.0%", "12.0%"),
        ("Abril", "200", "131", "16*", "89.5%", "11.4%"),
        ("Mayo", "157", "132", "14*", "84.1%", "9.0%"),
        ("Junio", "204", "169", "21*", "82.8%", "11.6%"),
        ("Julio", "166", "136", "16*", "81.9%", "9.5%"),
        ("Agosto", "379", "163", "50", "89.2%", "21.6%"),
        ("Septiembre (al 10)", "37", "20", "3", "94.6%", "2.1%"),
        ("TOTAL CONSOLIDADO", "1,753", "1,149", "172*", "87.6%", "100.0%")
    ]

    for r_i, row_data in enumerate(t4_data, start=1):
        for c_i, val in enumerate(row_data):
            p = t4.rows[r_i].cells[c_i].paragraphs[0]
            p.text = val
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_i > 0 else WD_ALIGN_PARAGRAPH.LEFT

    formatear_tabla(t4, [1.8, 1.1, 1.1, 1.1, 1.1, 0.8])
    
    p_nota = doc.add_paragraph()
    r_nota = p_nota.add_run("* Nota Metodológica: Los meses de Enero a Julio incluyen traslados estimados y certificados con base en la tasa de derivación hospitalaria observada (entre el 12% y 15% del total de auxilios médicos atendidos), mientras que Agosto y Septiembre reflejan la captura directa de bitácora digital en cabina C5/WhatsApp.")
    r_nota.font.name = 'Calibri'; r_nota.font.size = Pt(8); r_nota.font.italic = True; r_nota.font.color.rgb = RGBColor(108, 117, 125)
    p_nota.paragraph_format.space_before = Pt(4)
    p_nota.paragraph_format.space_after = Pt(16)

    # BLOQUE DE FIRMAS
    p_f_tit = doc.add_paragraph()
    p_f_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_ftit = p_f_tit.add_run("ATENTAMENTE\n\"PREVENCIÓN, AUXILIO Y SERVICIO A LA COMUNIDAD\"\n\n\n\n_____________________________________________\nLIC. DANIEL EDUARDO ROMERO PILAR\nDIRECTOR DE PROTECCIÓN CIVIL Y BOMBEROS MUNICIPALES\nH. AYUNTAMIENTO DE MEDELLÍN DE BRAVO, VERACRUZ")
    r_ftit.font.name = 'Calibri'; r_ftit.font.size = Pt(9.5); r_ftit.font.bold = True; r_ftit.font.color.rgb = RGBColor(10, 35, 66)

    output_path = 'Documentacion/Informe_Oficial_Emergencias_y_Traslados_2026.docx'
    doc.save(output_path)
    print(f"Documento Word creado exitosamente en: {output_path}")

if __name__ == '__main__':
    generar_documento_word()
