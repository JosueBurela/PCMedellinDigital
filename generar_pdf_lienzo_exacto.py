# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
import os

pdf_path = 'Documentacion/Formato_Deslinde_Responsabilidad_Abejas.pdf'
c = canvas.Canvas(pdf_path, pagesize=letter)
PAGE_WIDTH, PAGE_HEIGHT = letter # (612.0, 792.0)

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

X_LEFT = 24
W_CONTENT = 564
X_RIGHT = X_LEFT + W_CONTENT

# 1. Banner Superior (y=696 a y=788)
banner_top = 'Documentacion/banner_superior_oficial.png'
if os.path.exists(banner_top):
    c.drawImage(banner_top, X_LEFT, 696, width=W_CONTENT, height=90, preserveAspectRatio=False)

# 2. Encabezado Institucional y Folio (y=642 a y=690)
c.setFillColor(C_AZUL_INST)
c.setFont("Helvetica-Bold", 8.8)
c.drawString(X_LEFT, 680, "H. AYUNTAMIENTO CONSTITUCIONAL DE MEDELLÍN DE BRAVO, VERACRUZ")

c.setFillColor(C_GUINDA)
c.setFont("Helvetica-Bold", 8.2)
c.drawString(X_LEFT, 668, "DIRECCIÓN MUNICIPAL DE PROTECCIÓN CIVIL Y BOMBEROS")

c.setFillColor(C_TEXTO_OSC)
c.setFont("Helvetica-Bold", 8.8)
c.drawString(X_LEFT, 656, "ACTA DE DESLINDE DE RESPONSABILIDAD Y CONSENTIMIENTO INFORMADO")

c.setFillColor(C_TEXTO_SEC)
c.setFont("Helvetica-Oblique", 7.6)
c.drawString(X_LEFT, 644, "SERVICIO OPERATIVO: CONTROL, RETIRO Y/O REUBICACIÓN DE ENJAMBRES (HIMENÓPTEROS)")

# Caja Folio
c.setFillColor(C_AZUL_CLARO)
c.setStrokeColor(C_BORDE_DARK)
c.setLineWidth(1)
c.roundRect(414, 640, 174, 48, 3, fill=1, stroke=1)

c.setFillColor(C_ROJO_FOLIO)
c.setFont("Helvetica-Bold", 8.5)
c.drawString(422, 674, "FOLIO: PC-MED/FAU/26-______")

c.setFillColor(C_TEXTO_SEC)
c.setFont("Helvetica-Bold", 7.5)
c.drawString(422, 662, "FECHA:")
c.setFont("Helvetica", 7.5)
c.drawString(456, 662, "____ / _________ / 2026")

c.setFont("Helvetica-Bold", 7.5)
c.drawString(422, 650, "HORA:")
c.setFont("Helvetica", 7.5)
c.drawString(454, 650, "____:____ hrs")

c.drawString(510, 650, "UNIDAD:")
c.setFont("Helvetica-Bold", 7.5)
c.setFillColor(C_AZUL_INST)
c.drawString(548, 650, "U-______")

def draw_header_bar(title, y_top, bg_color=C_AZUL_INST, height=15):
    c.setFillColor(bg_color)
    c.setStrokeColor(bg_color)
    c.rect(X_LEFT, y_top - height, W_CONTENT, height, fill=1, stroke=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 7.8)
    c.drawString(X_LEFT + 8, y_top - height + 4.5, title)

# 3. Sección I: Datos del Solicitante (y=552 a y=632)
draw_header_bar("I. DATOS DEL SOLICITANTE / PROPIETARIO / REPRESENTANTE LEGAL", 632, C_AZUL_INST, 15)
y_t1 = 617
h_t1 = 65
c.setFillColor(colors.white)
c.setStrokeColor(C_GRIS_BORDE)
c.setLineWidth(0.8)
c.rect(X_LEFT, y_t1 - h_t1, W_CONTENT, h_t1, fill=1, stroke=1)
c.line(X_LEFT, y_t1 - 22, X_RIGHT, y_t1 - 22)
c.line(X_LEFT, y_t1 - 44, X_RIGHT, y_t1 - 44)
c.line(400, y_t1, 400, y_t1 - 44)

c.setFillColor(C_AZUL_INST)
c.setFont("Helvetica-Bold", 7.8)
c.drawString(X_LEFT + 6, y_t1 - 15, "Nombre Completo del Solicitante:")
c.setFillColor(C_LINEA_GUIA)
c.setFont("Helvetica", 7.8)
c.drawString(X_LEFT + 140, y_t1 - 15, "__________________________________________________")

c.setFillColor(C_AZUL_INST)
c.setFont("Helvetica-Bold", 7.8)
c.drawString(406, y_t1 - 15, "No. INE:")
c.setFillColor(C_LINEA_GUIA)
c.setFont("Helvetica", 7.8)
c.drawString(446, y_t1 - 15, "____________________")

c.setFillColor(C_AZUL_INST)
c.setFont("Helvetica-Bold", 7.8)
c.drawString(X_LEFT + 6, y_t1 - 37, "Institución / Razón Social (si aplica):")
c.setFillColor(C_LINEA_GUIA)
c.setFont("Helvetica", 7.8)
c.drawString(X_LEFT + 155, y_t1 - 37, "____________________________________________")

c.setFillColor(C_AZUL_INST)
c.setFont("Helvetica-Bold", 7.8)
c.drawString(406, y_t1 - 37, "Teléfono:")
c.setFillColor(C_LINEA_GUIA)
c.setFont("Helvetica", 7.8)
c.drawString(446, y_t1 - 37, "(_____) _____________")

c.setFillColor(C_AZUL_INST)
c.setFont("Helvetica-Bold", 7.6)
c.drawString(X_LEFT + 6, y_t1 - 58, "Carácter del Solicitante:")
c.setFillColor(C_TEXTO_SEC)
c.setFont("Helvetica", 7.6)
c.drawString(X_LEFT + 110, y_t1 - 58, "[  ] Propietario      [  ] Arrendatario / Inquilino      [  ] Encargado / Administrador      [  ] Repr. Institucional      [  ] Vecino")

# 4. Sección II: Ubicación (y=462 a y=542)
draw_header_bar("II. UBICACIÓN EXACTA DEL INMUEBLE O PREDIO INTERVENIDO", 544, C_AZUL_INST, 15)
y_t2 = 529
h_t2 = 65
c.setFillColor(colors.white)
c.setStrokeColor(C_GRIS_BORDE)
c.setLineWidth(0.8)
c.rect(X_LEFT, y_t2 - h_t2, W_CONTENT, h_t2, fill=1, stroke=1)
c.line(X_LEFT, y_t2 - 22, X_RIGHT, y_t2 - 22)
c.line(X_LEFT, y_t2 - 44, X_RIGHT, y_t2 - 44)
c.line(360, y_t2, 360, y_t2 - 22)

c.setFillColor(C_AZUL_INST)
c.setFont("Helvetica-Bold", 7.8)
c.drawString(X_LEFT + 6, y_t2 - 15, "Calle y Número Ext. / Int.:")
c.setFillColor(C_LINEA_GUIA)
c.setFont("Helvetica", 7.8)
c.drawString(X_LEFT + 115, y_t2 - 15, "____________________________________")

c.setFillColor(C_AZUL_INST)
c.setFont("Helvetica-Bold", 7.8)
c.drawString(366, y_t2 - 15, "Colonia / Localidad:")
c.setFillColor(C_LINEA_GUIA)
c.setFont("Helvetica", 7.8)
c.drawString(452, y_t2 - 15, "____________________")

c.setFillColor(C_AZUL_INST)
c.setFont("Helvetica-Bold", 7.8)
c.drawString(X_LEFT + 6, y_t2 - 37, "Referencias del Inmueble (entre calles, color de fachada):")
c.setFillColor(C_LINEA_GUIA)
c.setFont("Helvetica", 7.8)
c.drawString(X_LEFT + 245, y_t2 - 37, "________________________________________________")

c.setFillColor(C_AZUL_INST)
c.setFont("Helvetica-Bold", 7.6)
c.drawString(X_LEFT + 6, y_t2 - 58, "Tipo de Inmueble:")
c.setFillColor(C_TEXTO_SEC)
c.setFont("Helvetica", 7.6)
c.drawString(X_LEFT + 86, y_t2 - 58, "[  ] Casa Habitación      [  ] Plantel Escolar      [  ] Comercio / Negocio      [  ] Terreno Baldío      [  ] Vía Pública      [  ] Otro")

# 5. Sección III: Diagnóstico Técnico (y=394 a y=456)
draw_header_bar("III. EVALUACIÓN TÉCNICA Y DIAGNÓSTICO DE RIESGO (USO EXCLUSIVO PROTECCIÓN CIVIL)", 456, C_AZUL_INST, 15)
y_t3 = 441
h_t3 = 48
c.setFillColor(colors.white)
c.setStrokeColor(C_GRIS_BORDE)
c.setLineWidth(0.8)
c.rect(X_LEFT, y_t3 - h_t3, W_CONTENT, h_t3, fill=1, stroke=1)
c.line(X_LEFT, y_t3 - 24, X_RIGHT, y_t3 - 24)
c.line(285, y_t3, 285, y_t3 - h_t3)

c.setFillColor(C_AZUL_INST)
c.setFont("Helvetica-Bold", 7.6)
c.drawString(X_LEFT + 6, y_t3 - 16, "Especie Detectada:")
c.setFillColor(C_TEXTO_SEC)
c.setFont("Helvetica", 7.6)
c.drawString(X_LEFT + 92, y_t3 - 16, "[  ] Abeja Melífera    [  ] Avispa    [  ] Otro")

c.setFillColor(C_AZUL_INST)
c.setFont("Helvetica-Bold", 7.6)
c.drawString(292, y_t3 - 16, "Ubicación del Nido:")
c.setFillColor(C_TEXTO_SEC)
c.setFont("Helvetica", 7.6)
c.drawString(380, y_t3 - 16, "[  ] Árbol   [  ] Muro   [  ] Plafón   [  ] Tinaco")

c.setFillColor(C_AZUL_INST)
c.setFont("Helvetica-Bold", 7.6)
c.drawString(X_LEFT + 6, y_t3 - 40, "Altura Aprox:")
c.setFillColor(C_TEXTO_SEC)
c.setFont("Helvetica", 7.6)
c.drawString(X_LEFT + 64, y_t3 - 40, "______ m   |   Acceso: [  ] Libre   [  ] Escalera")

c.setFillColor(C_AZUL_INST)
c.setFont("Helvetica-Bold", 7.6)
c.drawString(292, y_t3 - 40, "Acción Determinada:")
c.setFillColor(C_TEXTO_SEC)
c.setFont("Helvetica", 7.6)
c.drawString(388, y_t3 - 40, "[  ] Reubicación Sustentable   [  ] Control Físico")

# 6. Sección IV: Declaraciones del Ciudadano (y=288 a y=388, h=100)
draw_header_bar("IV. DECLARACIONES Y MEDIDAS DE SEGURIDAD (BAJO PROTESTA DE DECIR VERDAD)", 386, C_AZUL_INST, 15)
y_t4 = 371
h_t4 = 92
c.setFillColor(C_GRIS_FONDO)
c.setStrokeColor(C_GRIS_BORDE)
c.setLineWidth(0.8)
c.rect(X_LEFT, y_t4 - h_t4, W_CONTENT, h_t4, fill=1, stroke=1)

style_dec = ParagraphStyle(
    'Declaraciones',
    fontName='Helvetica',
    fontSize=7.1,
    leading=9.1,
    alignment=TA_LEFT,
    textColor=C_TEXTO_SEC
)

decs_html = [
    "<b>1. Autorización de Acceso:</b> Autorizo el libre ingreso del personal operativo y unidades de auxilio de Protección Civil y Bomberos al inmueble para realizar las maniobras pertinentes.",
    "<b>2. Personas Vulnerables y Alergias:</b> Declaro bajo protesta de decir verdad si habitan personas alérgicas a picaduras (anafilaxia): [  ] SÍ   [  ] NO. Me obligo a evacuar preventivamente a menores, adultos mayores y resguardar animales domésticos.",
    "<b>3. Perímetro de Seguridad:</b> Me obligo a acatar las instrucciones de seguridad, manteniendo puertas y ventanas cerradas, luces apagadas y a moradores a más de 30 metros del área de operación.",
    "<b>4. Conducta Biológica de Pecoreo:</b> Quedo debidamente enterado(a) de que abejas pecoreadoras retornarán naturalmente al sitio durante 24 a 48 horas, debiendo mantener precauciones sin que ello sea negligencia oficial.",
    "<b>5. Intervención en Estructuras:</b> En caso de requerirse aperturas mecánicas en falso plafón, muros, techumbres o ramas para extraer el nido, autorizo la maniobra asumiendo reparaciones sin reclamo a la corporación."
]

y_dec_pos = y_t4 - 13
for d_html in decs_html:
    p_dec = Paragraph(d_html, style_dec)
    pw, ph = p_dec.wrap(W_CONTENT - 16, 30)
    p_dec.drawOn(c, X_LEFT + 8, y_dec_pos - ph + 4)
    y_dec_pos -= (ph + 4.2)

# 7. Sección V: Deslinde Legal (y=196 a y=274)
draw_header_bar("V. FUNDAMENTO JURÍDICO Y CLÁUSULA DE DESLINDE LEGAL DE RESPONSABILIDAD", 274, C_GUINDA, 15)
y_t5 = 259
h_t5 = 66
c.setFillColor(C_AZUL_CLARO)
c.setStrokeColor(C_BORDE_DARK)
c.setLineWidth(1)
c.rect(X_LEFT, y_t5 - h_t5, W_CONTENT, h_t5, fill=1, stroke=1)

style_leg = ParagraphStyle(
    'Legal',
    fontName='Helvetica',
    fontSize=7.1,
    leading=9.5,
    alignment=TA_JUSTIFY,
    textColor=C_TEXTO_OSC
)
txt_legal = (
    "<b>FUNDAMENTO LEGAL:</b> Con fundamento en los Artículos 8° y 115 Constitucionales; 1°, 2°, 3°, 18, 38 y 41 de la "
    "Ley No. 856 de Protección Civil y la Reducción del Riesgo de Desastres para el Estado de Veracruz de Ignacio de la Llave; "
    "Ley de Fomento Apícola del Estado de Veracruz; y Reglamento de Protección Civil de Medellín de Bravo: "
    "El(la) suscrito(a) <font color='#801438'><b>DESLINDA DE TODA RESPONSABILIDAD LEGAL, CIVIL, PENAL, ADMINISTRATIVA Y PATRIMONIAL</b></font> "
    "a la Dirección de Protección Civil y Bomberos de Medellín de Bravo, a su personal operativo y al H. Ayuntamiento de Medellín "
    "de Bravo por cualquier picadura fortuita, daño material fortuito o consecuencia derivada antes, durante o después del procedimiento, "
    "manifestando que el servicio se brinda de manera voluntaria, informada y de buena fe a mi expresa solicitud."
)
p_legal = Paragraph(txt_legal, style_leg)
p_legal.wrapOn(c, W_CONTENT - 16, h_t5 - 10)
p_legal.drawOn(c, X_LEFT + 8, y_t5 - h_t5 + 7)

# 8. Sección VI: Firmas y Validación (y=56 a y=188, h=132)
draw_header_bar("VI. CONSTANCIA DE CONFORMIDAD Y FIRMAS DE VALIDACIÓN", 188, C_AZUL_INST, 15)
y_t6 = 173
h_t6 = 117
c.setFillColor(colors.white)
c.setStrokeColor(C_GRIS_BORDE)
c.setLineWidth(0.8)
c.rect(X_LEFT, y_t6 - h_t6, W_CONTENT, h_t6, fill=1, stroke=1)

c.line(X_LEFT + 195, y_t6, X_LEFT + 195, y_t6 - h_t6)
c.line(X_LEFT + 390, y_t6, X_LEFT + 390, y_t6 - h_t6)

# Col 1: Solicitante (w=195)
c.setFillColor(C_AZUL_INST)
c.setFont("Helvetica-Bold", 7.8)
c.drawCentredString(X_LEFT + 97, y_t6 - 15, "SOLICITANTE / PROPIETARIO")

c.setStrokeColor(C_BORDE_DARK)
c.line(X_LEFT + 15, y_t6 - 65, X_LEFT + 180, y_t6 - 65)

c.setFillColor(C_TEXTO_SEC)
c.setFont("Helvetica-Oblique", 6.8)
c.drawCentredString(X_LEFT + 97, y_t6 - 74, "Nombre y Firma de Conformidad")

c.setFillColor(C_AZUL_INST)
c.setFont("Helvetica-Bold", 7.2)
c.drawString(X_LEFT + 12, y_t6 - 91, "Nombre:")
c.setFillColor(C_LINEA_GUIA)
c.setFont("Helvetica", 7.2)
c.drawString(X_LEFT + 48, y_t6 - 91, "________________________")

c.setFillColor(C_AZUL_INST)
c.setFont("Helvetica-Bold", 7.2)
c.drawString(X_LEFT + 12, y_t6 - 106, "No. INE:")
c.setFillColor(C_LINEA_GUIA)
c.setFont("Helvetica", 7.2)
c.drawString(X_LEFT + 48, y_t6 - 106, "________________________")

# Col 2: Elemento PC (w=195)
c.setFillColor(C_AZUL_INST)
c.setFont("Helvetica-Bold", 7.8)
c.drawCentredString(X_LEFT + 195 + 97, y_t6 - 15, "ELEMENTO OPERATIVO A CARGO")

c.setStrokeColor(C_BORDE_DARK)
c.line(X_LEFT + 195 + 15, y_t6 - 65, X_LEFT + 195 + 180, y_t6 - 65)

c.setFillColor(C_TEXTO_SEC)
c.setFont("Helvetica-Oblique", 6.8)
c.drawCentredString(X_LEFT + 195 + 97, y_t6 - 74, "Firma del Mando / Oficial")

c.setFillColor(C_AZUL_INST)
c.setFont("Helvetica-Bold", 7.2)
c.drawString(X_LEFT + 195 + 12, y_t6 - 91, "Nombre:")
c.setFillColor(C_LINEA_GUIA)
c.setFont("Helvetica", 7.2)
c.drawString(X_LEFT + 195 + 48, y_t6 - 91, "________________________")

c.setFillColor(C_AZUL_INST)
c.setFont("Helvetica-Bold", 7.2)
c.drawString(X_LEFT + 195 + 12, y_t6 - 106, "Rango / Móvil:")
c.setFillColor(C_LINEA_GUIA)
c.setFont("Helvetica", 7.2)
c.drawString(X_LEFT + 195 + 72, y_t6 - 106, "___________________")

# Col 3: Sello Oficial (w=174)
c.setFillColor(C_GUINDA)
c.setFont("Helvetica-Bold", 7.8)
c.drawCentredString(X_LEFT + 390 + 87, y_t6 - 15, "SELLO OFICIAL DE VALIDACIÓN")

c.setFillColor(colors.HexColor("#94A3B8"))
c.setFont("Helvetica-Oblique", 7.0)
c.drawCentredString(X_LEFT + 390 + 87, y_t6 - 62, "[ Espacio reservado para sello ]")

c.setFillColor(C_AZUL_INST)
c.setFont("Helvetica-Bold", 7.0)
c.drawCentredString(X_LEFT + 390 + 87, y_t6 - 95, "DIRECCIÓN DE PROTECCIÓN CIVIL")
c.drawCentredString(X_LEFT + 390 + 87, y_t6 - 105, "Y BOMBEROS DE MEDELLÍN DE BRAVO")

# 9. Banner Inferior Oficial (Desde y=0 hasta y=52, sangrado total)
banner_foot = 'Documentacion/banner_inferior_oficial.png'
if os.path.exists(banner_foot):
    c.drawImage(banner_foot, 0, 0, width=612, height=52, preserveAspectRatio=False)

c.showPage()
c.save()

print("PDF generado con ajuste impecable:", pdf_path)
