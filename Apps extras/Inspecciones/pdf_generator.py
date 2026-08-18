import os
import sys
import subprocess
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Determinar el directorio base real (evitando la carpeta _internal de PyInstaller)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Buscar logos en la carpeta assets del ejecutable o en sys._MEIPASS
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
if getattr(sys, 'frozen', False) and not os.path.exists(ASSETS_DIR):
    MEI_ASSETS = os.path.join(getattr(sys, '_MEIPASS', BASE_DIR), "assets")
    if os.path.exists(MEI_ASSETS):
        ASSETS_DIR = MEI_ASSETS

def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    return OUTPUT_DIR

def get_asset_path(filename):
    p = os.path.join(ASSETS_DIR, filename)
    if os.path.exists(p):
        return p
    return None

def split_50_chars(text, max_len=50):
    """
    Divide un texto en renglones de máximo 50 caracteres respetando espacios y guiones.
    """
    if not text or len(text) <= max_len:
        return [text] if text else []
    
    words = []
    current = ""
    for ch in text:
        current += ch
        if ch in [" ", "-"]:
            words.append(current)
            current = ""
    if current:
        words.append(current)
        
    lines = []
    current_line = ""
    for w in words:
        if len(current_line) + len(w) <= max_len:
            current_line += w
        else:
            if current_line:
                lines.append(current_line.rstrip())
            current_line = w
    if current_line:
        lines.append(current_line.rstrip())
    return lines

def generar_latex_tex(orden, items, filepath_tex):
    """
    Genera un archivo fuente LaTeX (.tex) con límite estricto de 50 caracteres por renglón
    en RUTAS, INSPECTOR y OPERADOR para evitar que se extienda a la derecha.
    """
    fecha_texto = orden.get("fecha_texto", "")
    horario = orden.get("horario", "")
    rutas_raw = orden.get("rutas_resumen", "")
    inspector_raw = orden.get("inspector", "")
    operador_raw = orden.get("operador", "")
    director = orden.get("director", "L.E.D. DANIEL EDUARDO ROMERO PILAR")

    path_med_raw = get_asset_path("logo_medellin.png")
    path_pc_raw = get_asset_path("logo_proteccion_civil.png")
    path_esc_raw = get_asset_path("logo_escudo.png")

    path_med = path_med_raw.replace("\\", "/") if path_med_raw else ""
    path_pc = path_pc_raw.replace("\\", "/") if path_pc_raw else ""
    path_esc = path_esc_raw.replace("\\", "/") if path_esc_raw else ""

    # Escapar caracteres especiales de LaTeX
    def sanitize(text):
        if not text:
            return ""
        replacements = {
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}",
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        return text

    def format_50_latex(text):
        lines = split_50_chars(text, max_len=50)
        sanitized_lines = [sanitize(l) for l in lines]
        return r" \\" + "\n  " if len(sanitized_lines) > 1 else sanitized_lines[0] if sanitized_lines else ""

    # Formatear aplicando el límite estricto de 50 caracteres por renglón
    rutas_lines = [sanitize(l) for l in split_50_chars(rutas_raw, 50)]
    rutas_tex = (r" \\" + "\n  ").join(rutas_lines)

    inspector_lines = [sanitize(l) for l in split_50_chars(inspector_raw, 50)]
    inspector_tex = (r" \\" + "\n  ").join(inspector_lines)

    operador_lines = [sanitize(l) for l in split_50_chars(operador_raw, 50)]
    operador_tex = (r" \\" + "\n  ").join(operador_lines)

    rows_latex = []
    for item in items:
        num = item.get("numero", "")
        ruta = sanitize(str(item.get("ruta", "")))
        est = sanitize(str(item.get("establecimiento", "")))
        mes = sanitize(str(item.get("mes_pago", "")))
        real = sanitize(str(item.get("realizado", "")))
        pend = sanitize(str(item.get("pendiente", "")))
        rows_latex.append(f"  {num} & {ruta} & {est} & {mes} & {real} & {pend} \\\\ \\hline")

    tabla_body = "\n".join(rows_latex)

    logo_med_tex = rf"\includegraphics[height=2.2cm]{{{path_med}}}" if path_med else ""
    logo_pc_tex = rf"\includegraphics[height=1.9cm]{{{path_pc}}}" if path_pc else ""
    logo_esc_tex = rf"\raggedleft\includegraphics[height=2.2cm]{{{path_esc}}}" if path_esc else ""

    tex_content = """\\documentclass[11pt,letterpaper]{article}
\\usepackage[utf8]{inputenc}
\\usepackage[spanish]{babel}
\\usepackage[margin=1.2cm]{geometry}
\\usepackage{tabularx}
\\usepackage{array}
\\usepackage{multirow}
\\usepackage{graphicx}
\\usepackage{titlesec}

\\pagestyle{empty}

\\begin{document}

% Encabezado con los 3 Logos Oficiales
\\noindent
\\begin{tabularx}{\\textwidth}{@{} p{4.5cm} >{\\centering\\arraybackslash}X p{3.5cm} @{}}
""" + logo_med_tex + " & " + logo_pc_tex + " & " + logo_esc_tex + """ \\\\
\\end{tabularx}

\\vspace{0.3cm}

% Titulo Principal Dependencia
\\begin{center}
    {\\LARGE \\textbf{DIRECCIÓN MUNICIPAL DE PROTECCIÓN CIVIL}}\\\\[1.2em]
\\end{center}

\\vspace{-0.4cm}

% Datos de la Orden (FECHA Y HORARIO)
\\noindent
\\begin{tabularx}{\\textwidth}{@{} X r @{}}
\\textbf{FECHA:} """ + sanitize(fecha_texto) + """ & \\textbf{HORARIO:} """ + sanitize(horario) + """ \\\\
\\end{tabularx}

\\vspace{0.15cm}

% RUTAS, INSPECTOR Y OPERADOR (Límite estricto 50 caracteres por renglón)
\\noindent
\\begin{tabularx}{\\textwidth}{@{} l X @{}}
\\textbf{RUTAS:} & """ + rutas_tex + """ \\\\[0.15cm]
\\textbf{INSPECTOR:} & """ + inspector_tex + """ \\\\[0.15cm]
\\textbf{OPERADOR:} & """ + operador_tex + """
\\end{tabularx}

\\vspace{0.4cm}

% Titulo Sección
\\begin{center}
    {\\Large \\textbf{INSPECCIONES A REALIZAR}}
\\end{center}

\\vspace{0.2cm}

% Tabla de Inspecciones
\\noindent
\\begin{tabularx}{\\textwidth}{| c | >{\\raggedright\\arraybackslash}p{3.0cm} | X | c | p{2.2cm} | p{2.2cm} |}
\\hline
\\textbf{Nº} & \\textbf{RUTA} & \\textbf{ESTABLECIMIENTO} & \\textbf{MES DE PAGO} & \\textbf{REALIZADO} & \\textbf{PENDIENTE} \\\\ \\hline
""" + tabla_body + """
\\end{tabularx}

\\vfill

% Firma del Director Municipal
\\begin{center}
    \\textbf{""" + sanitize(director) + """}\\\\[0.2em]
    \\textbf{DIRECTOR MUNICIPAL DE LA UNIDAD DE}\\\\[0.2em]
    \\textbf{PROTECCIÓN CIVIL DE MEDELLÍN DE BRAVO, VER.}
\\end{center}

\\end{document}
"""
    with open(filepath_tex, "w", encoding="utf-8") as f:
        f.write(tex_content)
    return filepath_tex

def generar_pdf_reportlab(orden, items, filepath_pdf):
    """
    Genera directamente un PDF aplicando el límite estricto de 50 caracteres por renglón
    en RUTAS, INSPECTOR y OPERADOR para que cada renglón salte de línea limpiamente.
    """
    doc = SimpleDocTemplate(
        filepath_pdf,
        pagesize=letter,
        leftMargin=30,
        rightMargin=30,
        topMargin=25,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        alignment=1, # Centered
        textColor=colors.HexColor('#1E293B')
    )

    sub_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        alignment=1, # Centered
        textColor=colors.HexColor('#0F172A')
    )

    meta_label = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1E293B')
    )

    meta_wrap_style = ParagraphStyle(
        'MetaWrap',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1E293B')
    )

    tbl_header_style = ParagraphStyle(
        'TblHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=10,
        alignment=1, # Center
        textColor=colors.HexColor('#0F172A')
    )

    tbl_cell_style = ParagraphStyle(
        'TblCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#1E293B')
    )

    tbl_cell_center = ParagraphStyle(
        'TblCellCenter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        alignment=1, # Center
        textColor=colors.HexColor('#1E293B')
    )

    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        alignment=1, # Centered
        textColor=colors.HexColor('#0F172A')
    )

    story = []

    # 1. Cargar e Insertar los 3 Logos Oficiales en el Encabezado Superior
    path_med = get_asset_path("logo_medellin.png")
    path_pc = get_asset_path("logo_proteccion_civil.png")
    path_esc = get_asset_path("logo_escudo.png")

    logo_med_img = Image(path_med, width=70, height=70) if path_med else ""
    logo_pc_img = Image(path_pc, width=65, height=57) if path_pc else ""
    logo_esc_img = Image(path_esc, width=54, height=65) if path_esc else ""

    header_logos_table = Table(
        [[logo_med_img, logo_pc_img, logo_esc_img]],
        colWidths=[180, 192, 180]
    )
    header_logos_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))

    story.append(header_logos_table)
    story.append(Spacer(1, 10))

    # Título Principal
    story.append(Paragraph("DIRECCIÓN MUNICIPAL DE PROTECCIÓN CIVIL", title_style))
    story.append(Spacer(1, 12))

    # Encabezado con Fecha y Horario
    fecha_text = orden.get("fecha_texto", "")
    horario_text = orden.get("horario", "")
    rutas_raw = orden.get("rutas_resumen", "")
    inspector_raw = orden.get("inspector", "")
    operador_raw = orden.get("operador", "")
    director_text = orden.get("director", "L.E.D. DANIEL EDUARDO ROMERO PILAR")

    # Aplicar el límite estricto de 50 caracteres por renglón usando <br/> en ReportLab
    rutas_lines = split_50_chars(rutas_raw, max_len=50)
    rutas_html = "<br/>".join(rutas_lines)

    inspector_lines = split_50_chars(inspector_raw, max_len=50)
    inspector_html = "<br/>".join(inspector_lines)

    operador_lines = split_50_chars(operador_raw, max_len=50)
    operador_html = "<br/>".join(operador_lines)

    meta_table_data = [
        [
            Paragraph(f"<b>FECHA:</b> {fecha_text}", meta_label),
            Paragraph(f"<b>HORARIO:</b> {horario_text}", ParagraphStyle('RightMeta', parent=meta_label, alignment=2))
        ],
        [Paragraph(f"<b>RUTAS:</b> {rutas_html}", meta_wrap_style), ""],
        [Paragraph(f"<b>INSPECTOR:</b> {inspector_html}", meta_wrap_style), ""],
        [Paragraph(f"<b>OPERADOR:</b> {operador_html}", meta_wrap_style), ""]
    ]

    meta_table = Table(meta_table_data, colWidths=[360, 192])
    meta_table.setStyle(TableStyle([
        ('SPAN', (0, 1), (1, 1)),
        ('SPAN', (0, 2), (1, 2)),
        ('SPAN', (0, 3), (1, 3)),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))

    story.append(meta_table)
    story.append(Spacer(1, 12))

    # Subtítulo "INSPECCIONES A REALIZAR"
    story.append(Paragraph("INSPECCIONES A REALIZAR", sub_title_style))
    story.append(Spacer(1, 8))

    # Tabla de Inspecciones
    table_data = [
        [
            Paragraph("Nº", tbl_header_style),
            Paragraph("RUTA", tbl_header_style),
            Paragraph("ESTABLECIMIENTO", tbl_header_style),
            Paragraph("MES DE PAGO", tbl_header_style),
            Paragraph("REALIZADO", tbl_header_style),
            Paragraph("PENDIENTE", tbl_header_style)
        ]
    ]

    for item in items:
        num = str(item.get("numero", ""))
        ruta = str(item.get("ruta", ""))
        est = str(item.get("establecimiento", ""))
        mes = str(item.get("mes_pago", ""))
        real = str(item.get("realizado", ""))
        pend = str(item.get("pendiente", ""))

        table_data.append([
            Paragraph(num, tbl_cell_center),
            Paragraph(ruta, tbl_cell_style),
            Paragraph(est, tbl_cell_style),
            Paragraph(mes, tbl_cell_center),
            Paragraph(real, tbl_cell_style),
            Paragraph(pend, tbl_cell_style)
        ])

    col_widths = [30, 115, 187, 80, 70, 70]
    tbl = Table(table_data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.6, colors.HexColor('#475569')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))

    story.append(tbl)
    story.append(Spacer(1, 20))

    # Pie de página con firma
    footer_text = f"""<b>{director_text}</b><br/>
DIRECTOR MUNICIPAL DE LA UNIDAD DE<br/>
PROTECCION CIVIL DE MEDELLIN DE BRAVO, VER."""
    
    story.append(KeepTogether([
        Paragraph(footer_text, footer_style)
    ]))

    doc.build(story)
    return filepath_pdf

def exportar_orden_completa(orden_data, base_filename=None):
    """
    Genera tanto el archivo PDF como el fuente LaTeX (.tex).
    Guarda siempre los archivos en la carpeta 'output' de la raíz del proyecto.
    Versionado automático (_v1, _v2, _v3...). Abre la carpeta o PDF tras exportar.
    """
    out_dir = ensure_output_dir()
    orden = orden_data["orden"]
    items = orden_data["items"]
    
    fecha_corta = orden.get("fecha_corta", "orden")
    orden_id = orden.get("id", "0")
    
    if not base_filename:
        prefix = f"Inspeccion_{fecha_corta}_ID{orden_id}"
        version = 1
        while True:
            candidate_pdf = os.path.join(out_dir, f"{prefix}_v{version}.pdf")
            candidate_tex = os.path.join(out_dir, f"{prefix}_v{version}.tex")
            if not os.path.exists(candidate_pdf) and not os.path.exists(candidate_tex):
                base_filename = f"{prefix}_v{version}"
                break
            version += 1
        
    filepath_tex = os.path.join(out_dir, f"{base_filename}.tex")
    filepath_pdf = os.path.join(out_dir, f"{base_filename}.pdf")
    
    # 1. Generar código LaTeX .tex
    generar_latex_tex(orden, items, filepath_tex)
    
    # 2. Intentar compilar con pdflatex si está instalado
    compiled_with_latex = False
    try:
        res = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", f"-output-directory={out_dir}", filepath_tex],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10
        )
        if res.returncode == 0:
            compiled_with_latex = True
    except Exception:
        compiled_with_latex = False
        
    # 3. Si no hay pdflatex o falla, generar PDF nativo impecable con ReportLab
    if not compiled_with_latex or not os.path.exists(filepath_pdf):
        generar_pdf_reportlab(orden, items, filepath_pdf)

    # 4. Abrir el PDF automáticamente en Windows Explorer
    try:
        if os.name == 'nt' and os.path.exists(filepath_pdf):
            os.startfile(filepath_pdf)
    except Exception:
        pass

    return {
        "tex": filepath_tex,
        "pdf": filepath_pdf,
        "filename": base_filename
    }
