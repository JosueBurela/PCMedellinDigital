# -*- coding: utf-8 -*-
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def generar_pdf():
    pdf_path = 'Documentacion/Acta_Intercambio_Motosierras_PC_ImagenUrbana.pdf'
    c = canvas.Canvas(pdf_path, pagesize=letter)
    PAGE_WIDTH, PAGE_HEIGHT = letter # 612 x 792

    C_AZUL_INST = colors.HexColor("#0A2342")
    C_GUINDA    = colors.HexColor("#801438")
    C_AZUL_CLARO= colors.HexColor("#F1F5F9")
    C_GRIS_FONDO= colors.HexColor("#F8FAFC")
    C_GRIS_BORDE= colors.HexColor("#CBD5E1")
    C_BORDE_DARK= colors.HexColor("#94A3B8")
    C_TEXTO_OSC = colors.HexColor("#0F172A")
    C_TEXTO_SEC = colors.HexColor("#334155")
    C_ROJO_FOLIO= colors.HexColor("#B91C1C")
    C_LINEA_GUIA= colors.HexColor("#64748B")
    C_VERDE_OK  = colors.HexColor("#15803D")

    X_LEFT = 24
    W_CONTENT = 564
    X_RIGHT = X_LEFT + W_CONTENT

    # 1. Banner Superior Oficial (y=696 a y=786)
    banner_top = 'Documentacion/banner_superior_oficial.png'
    if os.path.exists(banner_top):
        c.drawImage(banner_top, X_LEFT, 696, width=W_CONTENT, height=90, preserveAspectRatio=False)

    # 2. Encabezado Institucional y Folio (y=644 a y=692)
    c.setFillColor(C_AZUL_INST)
    c.setFont("Helvetica-Bold", 8.8)
    c.drawString(X_LEFT, 680, "H. AYUNTAMIENTO CONSTITUCIONAL DE MEDELLÍN DE BRAVO, VERACRUZ")

    c.setFillColor(C_GUINDA)
    c.setFont("Helvetica-Bold", 8.2)
    c.drawString(X_LEFT, 668, "PROTECCIÓN CIVIL Y BOMBEROS  •  DIRECCIÓN DE IMAGEN URBANA")

    c.setFillColor(C_TEXTO_OSC)
    c.setFont("Helvetica-Bold", 8.8)
    c.drawString(X_LEFT, 656, "ACTA CIRCUNSTANCIADA DE ENTREGA-RECEPCIÓN E INTERCAMBIO DE HERRAMIENTA")

    c.setFillColor(C_TEXTO_SEC)
    c.setFont("Helvetica-Oblique", 7.6)
    c.drawString(X_LEFT, 644, "COORDINACIÓN INTERDEPARTAMENTAL: ÁREA DE PARQUES Y JARDINES / BRIGADA PC")

    # Caja Folio y Control
    c.setFillColor(C_AZUL_CLARO)
    c.setStrokeColor(C_BORDE_DARK)
    c.setLineWidth(1)
    c.roundRect(414, 640, 174, 48, 3, fill=1, stroke=1)

    c.setFillColor(C_ROJO_FOLIO)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(422, 674, "FOLIO: PC-MED/ACT-HERR/26-____")

    c.setFillColor(C_TEXTO_SEC)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(422, 662, "FECHA:")
    c.setFont("Helvetica", 7.5)
    c.drawString(456, 662, "14 / Septiembre / 2026")

    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(422, 650, "ASUNTO:")
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(C_AZUL_INST)
    c.drawString(464, 650, "Intercambio de Motosierras")

    def draw_header_bar(title, y_top, bg_color=C_AZUL_INST, height=15):
        c.setFillColor(bg_color)
        c.setStrokeColor(bg_color)
        c.rect(X_LEFT, y_top - height, W_CONTENT, height, fill=1, stroke=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 7.8)
        c.drawString(X_LEFT + 8, y_top - height + 4.5, title)

    # 3. Sección I: Dependencias y Personal Interviniente (y=578 a y=634)
    draw_header_bar("I. DEPENDENCIAS Y PERSONAL INTERVINIENTE EN LA ENTREGA-RECEPCIÓN", 634, C_AZUL_INST, 15)
    y_t1 = 619
    h_t1 = 44
    c.setFillColor(colors.white)
    c.setStrokeColor(C_GRIS_BORDE)
    c.setLineWidth(0.8)
    c.rect(X_LEFT, y_t1 - h_t1, W_CONTENT, h_t1, fill=1, stroke=1)
    c.line(285 + X_LEFT, y_t1, 285 + X_LEFT, y_t1 - h_t1) # Divisor vertical

    # Col 1: Imagen Urbana / Parques y Jardines
    c.setFillColor(C_GUINDA)
    c.setFont("Helvetica-Bold", 7.6)
    c.drawString(X_LEFT + 8, y_t1 - 13, "ÁREA DE PARQUES Y JARDINES (IMAGEN URBANA):")
    c.setFillColor(C_TEXTO_OSC)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(X_LEFT + 8, y_t1 - 25, "Personal Comisionado: ")
    c.setFont("Helvetica", 7.5)
    c.drawString(X_LEFT + 104, y_t1 - 25, "C. Mariano Molina Quintal")
    c.setFont("Helvetica-Oblique", 7.0)
    c.setFillColor(C_TEXTO_SEC)
    c.drawString(X_LEFT + 8, y_t1 - 37, "Acción: Entrega Motosierra Hyundai y Recibe Motosierra Stihl")

    # Col 2: Protección Civil y Bomberos
    c.setFillColor(C_AZUL_INST)
    c.setFont("Helvetica-Bold", 7.6)
    c.drawString(X_LEFT + 293, y_t1 - 13, "DIRECCIÓN DE PROTECCIÓN CIVIL Y BOMBEROS:")
    c.setFillColor(C_TEXTO_OSC)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(X_LEFT + 293, y_t1 - 25, "Personal Receptor: ")
    c.setFont("Helvetica", 7.5)
    c.drawString(X_LEFT + 375, y_t1 - 25, "C. Francisco Lara Fernández")
    c.setFont("Helvetica-Oblique", 7.0)
    c.setFillColor(C_TEXTO_SEC)
    c.drawString(X_LEFT + 293, y_t1 - 37, "Acción: Entrega Motosierra Stihl y Recibe Motosierra Hyundai")

    # 4. Sección II: Cuadro Comparativo de Equipos (y=452 a y=568)
    draw_header_bar("II. ESPECIFICACIONES TÉCNICAS DE LOS EQUIPOS INTERCAMBIADOS (SALIDA Y ENTRADA)", 570, C_AZUL_INST, 15)
    y_t2 = 555
    h_t2 = 104
    c.setFillColor(colors.white)
    c.setStrokeColor(C_GRIS_BORDE)
    c.setLineWidth(0.8)
    c.rect(X_LEFT, y_t2 - h_t2, W_CONTENT, h_t2, fill=1, stroke=1)
    c.line(X_LEFT + 282, y_t2, X_LEFT + 282, y_t2 - h_t2)

    # Sub-encabezados de columna
    c.setFillColor(colors.HexColor("#FEE2E2")) # Fondo rojizo suave para equipo que sale
    c.rect(X_LEFT, y_t2 - 16, 282, 16, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#991B1B"))
    c.setFont("Helvetica-Bold", 7.6)
    c.drawString(X_LEFT + 10, y_t2 - 11, "EQUIPO QUE SALE (DE PC A PARQUES Y JARDINES):")

    c.setFillColor(colors.HexColor("#DCFCE7")) # Fondo verde suave para equipo que entra
    c.rect(X_LEFT + 282, y_t2 - 16, 282, 16, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#166534"))
    c.setFont("Helvetica-Bold", 7.6)
    c.drawString(X_LEFT + 292, y_t2 - 11, "EQUIPO QUE ENTRA (DE PARQUES Y JARDINES A PC):")

    specs_sale = [
        ("Tipo de Equipo:", "Motosierra de Combustión Profesional"),
        ("Marca Oficial:", "STIHL"),
        ("Modelo:", "MS 310 (MS310)"),
        ("Color y Rasgos:", "Naranja con cubierta superior blanca"),
        ("Espada y Barra:", "Barra Stihl Rollomatic con cadena de corte montada"),
        ("Estado Físico:", "Operativa / Buenas condiciones de servicio"),
        ("Destinatario:", "C. Mariano Molina Quintal (Parques y Jardines)")
    ]

    specs_entra = [
        ("Tipo de Equipo:", "Motosierra de Combustión"),
        ("Marca Oficial:", "HYUNDAI"),
        ("Modelo:", "860 Turbo"),
        ("Color y Rasgos:", "Gris claro con cubierta superior azul"),
        ("Espada y Barra:", "Barra de corte con cadena dentada montada"),
        ("Estado Físico:", "Operativa / Recibida para servicio operativo"),
        ("Receptor PC:", "C. Francisco Lara Fernández (Protección Civil)")
    ]

    for idx, ((lbl_s, val_s), (lbl_e, val_e)) in enumerate(zip(specs_sale, specs_entra)):
        y_row = y_t2 - 27 - (idx * 11)
        # Sale
        c.setFillColor(C_AZUL_INST)
        c.setFont("Helvetica-Bold", 7.2)
        c.drawString(X_LEFT + 8, y_row, lbl_s)
        c.setFillColor(C_TEXTO_OSC if idx in (1,2) else C_TEXTO_SEC)
        c.setFont("Helvetica-Bold" if idx in (1,2) else "Helvetica", 7.2)
        c.drawString(X_LEFT + 80, y_row, val_s)

        # Entra
        c.setFillColor(C_AZUL_INST)
        c.setFont("Helvetica-Bold", 7.2)
        c.drawString(X_LEFT + 292, y_row, lbl_e)
        c.setFillColor(C_TEXTO_OSC if idx in (1,2) else C_TEXTO_SEC)
        c.setFont("Helvetica-Bold" if idx in (1,2) else "Helvetica", 7.2)
        c.drawString(X_LEFT + 368, y_row, val_e)

    # 5. Sección III: Motivo y Acuerdos Administrativos (y=384 a y=444)
    draw_header_bar("III. MOTIVO Y DECLARACIÓN ADMINISTRATIVA (PARA CONOCIMIENTO DE LOS MANDOS)", 444, C_GUINDA, 15)
    y_t3 = 429
    h_t3 = 54
    c.setFillColor(C_AZUL_CLARO)
    c.setStrokeColor(C_BORDE_DARK)
    c.setLineWidth(1)
    c.rect(X_LEFT, y_t3 - h_t3, W_CONTENT, h_t3, fill=1, stroke=1)

    style_mot = ParagraphStyle(
        'Motivo',
        fontName='Helvetica',
        fontSize=7.2,
        leading=9.8,
        alignment=TA_JUSTIFY,
        textColor=C_TEXTO_OSC
    )
    txt_motivo = (
        "<b>CLÁUSULA DE CONOCIMIENTO Y RESGUARDO:</b> En la Base Operativa de Protección Civil de Medellín de Bravo, Ver., "
        "se hace constar el intercambio de las motosierras descritas entre el área de <b>Parques y Jardines (Dirección de Imagen Urbana)</b> "
        "y la <b>Dirección de Protección Civil y Bomberos</b>, con el objetivo de redistribuir la herramienta de trabajo para tareas "
        "de poda, desrame preventivo y atención de emergencias en el Municipio. Ambas partes declaran haber verificado presencialmente "
        "el funcionamiento mecánico, motor y accesorios de los equipos al momento de la entrega-recepción, asumiendo su resguardo patrimonial "
        "y reportando este acto formal para conocimiento y registro de los titulares de ambas dependencias."
    )
    p_mot = Paragraph(txt_motivo, style_mot)
    p_mot.wrapOn(c, W_CONTENT - 16, h_t3 - 8)
    p_mot.drawOn(c, X_LEFT + 8, y_t3 - h_t3 + 6)

    # 6. Sección IV: Evidencia Fotográfica y Notas de Inspección (y=210 a y=370)
    draw_header_bar("IV. REGISTRO FOTOGRÁFICO DE VERIFICACIÓN EN SITIO", 370, C_AZUL_INST, 15)
    y_t4 = 355
    h_t4 = 145
    c.setFillColor(colors.white)
    c.setStrokeColor(C_GRIS_BORDE)
    c.setLineWidth(0.8)
    c.rect(X_LEFT, y_t4 - h_t4, W_CONTENT, h_t4, fill=1, stroke=1)

    # Insertar la foto real del usuario con marco elegante
    photo_path = 'Documentacion/foto_intercambio_ajustada.jpg'
    w_foto = 84
    h_foto = 135
    x_foto = X_LEFT + 12
    y_foto = y_t4 - h_t4 + 5

    if os.path.exists(photo_path):
        c.setStrokeColor(C_BORDE_DARK)
        c.setLineWidth(1)
        c.rect(x_foto - 2, y_foto - 2, w_foto + 4, h_foto + 4, fill=0, stroke=1)
        c.drawImage(photo_path, x_foto, y_foto, width=w_foto, height=h_foto, preserveAspectRatio=False)

    # Texto al costado derecho de la fotografía
    x_info = X_LEFT + 110
    w_info = W_CONTENT - 120

    c.setFillColor(C_AZUL_INST)
    c.setFont("Helvetica-Bold", 8.2)
    c.drawString(x_info, y_t4 - 18, "CONSTANCIA FOTOGRÁFICA DE LA INSPECCIÓN Y TRASPASO")

    c.setFillColor(C_TEXTO_SEC)
    c.setFont("Helvetica-Oblique", 7.4)
    c.drawString(x_info, y_t4 - 30, "Fotografía tomada al momento del intercambio físico en patio operativo de la base.")

    notas_tecnicas = [
        "<b>Identificación de la evidencia:</b> En la imagen superior se aprecia al <b>C. Mariano Molina Quintal</b> sosteniendo la motosierra <b>Stihl MS 310</b> que sale de Protección Civil para ser integrada al servicio de Parques y Jardines.",
        "<b>Equipo receptor en sitio:</b> En primer plano en el suelo se ubica la motosierra <b>Hyundai 860 Turbo</b> entregada formalmente a Protección Civil para el resguardo del <b>C. Francisco Lara Fernández</b>.",
        "<b>Estado de los componentes:</b> Ambos equipos cuentan con barra de espada montada, cadena de aserrado, mangos de sujeción ergonómicos y tanques de combustible y mezcla revisados sin fugas aparentes.",
        "<b>Destino operativo:</b> Los equipos quedan dados de alta en la bitácora interna de herramientas para conocimiento de los mandos y supervisión periódica de inventarios."
    ]

    style_nota = ParagraphStyle(
        'NotasFoto',
        fontName='Helvetica',
        fontSize=7.1,
        leading=9.2,
        alignment=TA_LEFT,
        textColor=C_TEXTO_SEC
    )

    y_nota_cursor = y_t4 - 44
    for nota in notas_tecnicas:
        p_n = Paragraph(f"• {nota}", style_nota)
        pw, ph = p_n.wrap(w_info, 40)
        p_n.drawOn(c, x_info, y_nota_cursor - ph + 4)
        y_nota_cursor -= (ph + 3.5)

    # 7. Sección V: Firmas de Conformidad y Vo.Bo. de Mandos (y=56 a y=205, h=148)
    draw_header_bar("V. CONSTANCIA DE CONFORMIDAD Y VALIDACIÓN DE MANDOS", 205, C_AZUL_INST, 15)
    y_t5 = 190
    h_t5 = 134
    c.setFillColor(colors.white)
    c.setStrokeColor(C_GRIS_BORDE)
    c.setLineWidth(0.8)
    c.rect(X_LEFT, y_t5 - h_t5, W_CONTENT, h_t5, fill=1, stroke=1)

    # Grid 2 x 2 de firmas
    w_col = W_CONTENT / 2 # 282 pt
    h_row_sig = h_t5 / 2   # 67 pt
    c.line(X_LEFT + w_col, y_t5, X_LEFT + w_col, y_t5 - h_t5) # Línea vertical media
    c.line(X_LEFT, y_t5 - h_row_sig, X_RIGHT, y_t5 - h_row_sig) # Línea horizontal media

    # Cuadrante 1 (Superior Izquierdo): Entrega Mariano
    c.setFillColor(C_GUINDA)
    c.setFont("Helvetica-Bold", 7.4)
    c.drawCentredString(X_LEFT + (w_col/2), y_t5 - 12, "ENTREGA POR PARQUES Y JARDINES:")
    c.setStrokeColor(C_BORDE_DARK)
    c.line(X_LEFT + 25, y_t5 - 42, X_LEFT + w_col - 25, y_t5 - 42)
    c.setFillColor(C_AZUL_INST)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(X_LEFT + (w_col/2), y_t5 - 51, "C. MARIANO MOLINA QUINTAL")
    c.setFillColor(C_TEXTO_SEC)
    c.setFont("Helvetica", 6.8)
    c.drawCentredString(X_LEFT + (w_col/2), y_t5 - 60, "Área de Parques y Jardines • Imagen Urbana")

    # Cuadrante 2 (Superior Derecho): Recibe Francisco Lara
    c.setFillColor(C_AZUL_INST)
    c.setFont("Helvetica-Bold", 7.4)
    c.drawCentredString(X_LEFT + w_col + (w_col/2), y_t5 - 12, "RECIBE POR PROTECCIÓN CIVIL:")
    c.setStrokeColor(C_BORDE_DARK)
    c.line(X_LEFT + w_col + 25, y_t5 - 42, X_RIGHT - 25, y_t5 - 42)
    c.setFillColor(C_AZUL_INST)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(X_LEFT + w_col + (w_col/2), y_t5 - 51, "C. FRANCISCO LARA FERNÁNDEZ")
    c.setFillColor(C_TEXTO_SEC)
    c.setFont("Helvetica", 6.8)
    c.drawCentredString(X_LEFT + w_col + (w_col/2), y_t5 - 60, "Elemento Operativo • Protección Civil y Bomberos")

    # Cuadrante 3 (Inferior Izquierdo): Vo.Bo. Imagen Urbana
    c.setFillColor(C_GUINDA)
    c.setFont("Helvetica-Bold", 7.4)
    c.drawCentredString(X_LEFT + (w_col/2), y_t5 - h_row_sig - 12, "VO. BO. DIRECCIÓN DE IMAGEN URBANA:")
    c.setStrokeColor(C_BORDE_DARK)
    c.line(X_LEFT + 25, y_t5 - h_row_sig - 42, X_LEFT + w_col - 25, y_t5 - h_row_sig - 42)
    c.setFillColor(C_AZUL_INST)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(X_LEFT + (w_col/2), y_t5 - h_row_sig - 51, "LIC. PASTOR PÉREZ SALDAÑA")
    c.setFillColor(C_TEXTO_SEC)
    c.setFont("Helvetica", 6.8)
    c.drawCentredString(X_LEFT + (w_col/2), y_t5 - h_row_sig - 60, "Director de Imagen Urbana • Medellín de Bravo")

    # Cuadrante 4 (Inferior Derecho): Vo.Bo. Protección Civil
    c.setFillColor(C_AZUL_INST)
    c.setFont("Helvetica-Bold", 7.4)
    c.drawCentredString(X_LEFT + w_col + (w_col/2), y_t5 - h_row_sig - 12, "VO. BO. DIRECCIÓN DE PROTECCIÓN CIVIL:")
    c.setStrokeColor(C_BORDE_DARK)
    c.line(X_LEFT + w_col + 25, y_t5 - h_row_sig - 42, X_RIGHT - 25, y_t5 - h_row_sig - 42)
    c.setFillColor(C_AZUL_INST)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(X_LEFT + w_col + (w_col/2), y_t5 - h_row_sig - 51, "LIC. DANIEL EDUARDO ROMERO PILAR")
    c.setFillColor(C_TEXTO_SEC)
    c.setFont("Helvetica", 6.8)
    c.drawCentredString(X_LEFT + w_col + (w_col/2), y_t5 - h_row_sig - 60, "Titular de Protección Civil y Bomberos Medellín")

    # 8. Banner Inferior Oficial (y=0 a y=52, sangrado total)
    banner_foot = 'Documentacion/banner_inferior_oficial.png'
    if os.path.exists(banner_foot):
        c.drawImage(banner_foot, 0, 0, width=612, height=52, preserveAspectRatio=False)

    c.showPage()
    c.save()
    print("PDF del Acta de Intercambio generado exitosamente:", pdf_path)

def generar_docx():
    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = Inches(0.24)
    sec.bottom_margin = Inches(0.22)
    sec.left_margin = Inches(0.48)
    sec.right_margin = Inches(0.48)
    
    W_TOTAL = Inches(7.54)
    
    # Banner superior
    p_ban = doc.add_paragraph()
    p_ban.paragraph_format.space_before = Pt(0)
    p_ban.paragraph_format.space_after = Pt(2)
    r_ban = p_ban.add_run()
    r_ban.add_picture('Documentacion/banner_superior_oficial.png', width=W_TOTAL, height=Inches(1.10))
    
    # Encabezado
    t_hdr = doc.add_table(rows=1, cols=2)
    t_hdr.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_i, c_f = t_hdr.rows[0].cells
    c_i.width = Inches(5.34)
    c_f.width = Inches(2.20)
    
    p = c_i.paragraphs[0]
    r = p.add_run("H. AYUNTAMIENTO DE MEDELLÍN DE BRAVO, VERACRUZ\n")
    r.bold = True
    r.font.size = Pt(9.0)
    r = p.add_run("PROTECCIÓN CIVIL Y BOMBEROS  •  DIRECCIÓN DE IMAGEN URBANA\n")
    r.bold = True
    r.font.size = Pt(8.0)
    r = p.add_run("ACTA CIRCUNSTANCIADA DE ENTREGA-RECEPCIÓN DE HERRAMIENTA\n")
    r.bold = True
    r.font.size = Pt(8.8)
    r = p.add_run("INTERCAMBIO OPERATIVO: PARQUES Y JARDINES / PROTECCIÓN CIVIL")
    r.italic = True
    r.font.size = Pt(7.5)
    
    p2 = c_f.paragraphs[0]
    r = p2.add_run("FOLIO: PC-MED/ACT-HERR/26-____\n")
    r.bold = True
    r.font.size = Pt(8.5)
    r.font.color.rgb = RGBColor(185, 28, 28)
    r = p2.add_run("FECHA: 14 / Septiembre / 2026\n")
    r.font.size = Pt(7.5)
    r = p2.add_run("ASUNTO: Intercambio de Motosierras")
    r.font.size = Pt(7.5)
    r.bold = True
    
    # Tabla de equipos
    t_eq = doc.add_table(rows=8, cols=2)
    t_eq.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_eq.rows[0].cells[0].text = "EQUIPO QUE SALE (DE PC A PARQUES Y JARDINES)"
    t_eq.rows[0].cells[1].text = "EQUIPO QUE ENTRA (DE PARQUES Y JARDINES A PC)"
    
    filas_datos = [
        ("Tipo:", "Motosierra de Combustión", "Tipo:", "Motosierra de Combustión"),
        ("Marca:", "STIHL", "Marca:", "HYUNDAI"),
        ("Modelo:", "MS 310 (MS310)", "Modelo:", "860 Turbo"),
        ("Color:", "Naranja con cubierta blanca", "Color:", "Gris claro con cubierta azul"),
        ("Espada:", "Barra Stihl Rollomatic con cadena", "Espada:", "Barra de corte con cadena"),
        ("Estado:", "Operativa / Buenas condiciones", "Estado:", "Operativa / Recibida en servicio"),
        ("Entrega/Recibe:", "C. Mariano Molina Quintal (Parques y Jardines)", "Entrega/Recibe:", "C. Francisco Lara Fernández (Protección Civil)")
    ]
    for idx, (l1, v1, l2, v2) in enumerate(filas_datos):
        row = t_eq.rows[idx + 1]
        row.cells[0].text = f"{l1} {v1}"
        row.cells[1].text = f"{l2} {v2}"
        
    # Firmas
    t_sig = doc.add_table(rows=2, cols=2)
    t_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_sig.rows[0].cells[0].text = "ENTREGA (PARQUES Y JARDINES):\n\n_______________________________\nC. MARIANO MOLINA QUINTAL\nÁrea de Parques y Jardines"
    t_sig.rows[0].cells[1].text = "RECIBE (PROTECCIÓN CIVIL):\n\n_______________________________\nC. FRANCISCO LARA FERNÁNDEZ\nElemento Operativo de Protección Civil"
    t_sig.rows[1].cells[0].text = "VO. BO. DIRECCIÓN DE IMAGEN URBANA:\n\n_______________________________\nLIC. PASTOR PÉREZ SALDAÑA\nDirector de Imagen Urbana"
    t_sig.rows[1].cells[1].text = "VO. BO. PROTECCIÓN CIVIL Y BOMBEROS:\n\n_______________________________\nLIC. DANIEL EDUARDO ROMERO PILAR\nTitular de Protección Civil y Bomberos"
    
    # Banner pie
    p_foot = doc.add_paragraph()
    p_foot.paragraph_format.space_before = Pt(4)
    r_foot = p_foot.add_run()
    r_foot.add_picture('Documentacion/banner_inferior_oficial.png', width=W_TOTAL, height=Inches(0.48))
    
    docx_path = 'Documentacion/Acta_Intercambio_Motosierras_PC_ImagenUrbana.docx'
    doc.save(docx_path)
    print("DOCX del Acta de Intercambio generado exitosamente:", docx_path)

if __name__ == '__main__':
    generar_pdf()
    generar_docx()
