import psycopg2
import re
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

print("Conectando a PostgreSQL para procesar incendios...")
conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()

GROUP_JID = '120363042493725288@g.us'

cur.execute('''
    SELECT 
        "id",
        to_timestamp("messageTimestamp") as fecha,
        "pushName",
        "messageType",
        COALESCE(
            "message"->>'conversation',
            "message"->'extendedTextMessage'->>'text',
            "message"->'imageMessage'->>'caption',
            "message"->'videoMessage'->>'caption',
            ''
        ) as texto,
        "message"->'imageMessage' IS NOT NULL as tiene_imagen,
        "key"->>'id' as wa_id
    FROM "Message"
    WHERE "key"->>'remoteJid' = %s
      AND to_timestamp("messageTimestamp") >= '2026-01-01 00:00:00'
    ORDER BY "messageTimestamp" ASC
''', (GROUP_JID,))

todos_2026 = cur.fetchall()
print(f"Total mensajes en 2026: {len(todos_2026)}")

regex_fuego = re.compile(r'\b(incendio|incendios|quema|quemas|pastizal|pastizales|fuego|conato|humo|sofoca|sofocad|sofocaci[oó]n|bomberos?|llantas?|basurero|chispas?)\b', re.IGNORECASE)
regex_salida = re.compile(r'\b(sale|salida|en ruta|al punto|acude|atender|reportan|reporte de|sofocando|sofocado|controlado)\b', re.IGNORECASE)

MAPA_MESES = {
    '01': 'Enero', '02': 'Febrero', '03': 'Marzo', '04': 'Abril',
    '05': 'Mayo', '06': 'Junio', '07': 'Julio', '08': 'Agosto',
    '09': 'Septiembre', '10': 'Octubre', '11': 'Noviembre', '12': 'Diciembre'
}

servicios = []
vistos = set()

for r in todos_2026:
    mid, fecha, push, mtype, texto, tiene_img, wa_id = r
    if not texto:
        continue
    t_lower = texto.lower()
    
    if not regex_fuego.search(t_lower):
        continue
        
    # Filtrar falsos positivos médicos
    if 'quemadura de' in t_lower or 'quemadura por' in t_lower or 'quemaduras en' in t_lower:
        if not any(k in t_lower for k in ['pastizal', 'casa', 'basura', 'fuego', 'sofoc', 'pipa', 'apagar']):
            continue

    es_incendio_op = False
    if regex_salida.search(t_lower):
        es_incendio_op = True
    elif any(k in t_lower for k in ['incendio de pastizal', 'incendio en', 'quema de basura', 'quema de pastizal', 'conato de incendio']):
        es_incendio_op = True
        
    if not es_incendio_op:
        continue

    # Deduplicar si el mismo reporte se repitió en menos de 10 minutos
    clave_dedup = (texto[:35].lower(), fecha.strftime('%Y-%m-%d-%H'))
    if clave_dedup in vistos:
        continue
    vistos.add(clave_dedup)

    # Identificar unidad
    unidad = "Guardia de Bomberos PC"
    m_u = re.search(r'(unidad\s*\d+|u-\d+|m[oó]vil\s*\d+|pipa|096|072|073|047|041|097|098|208)', t_lower)
    if m_u:
        u_raw = m_u.group(0).upper()
        if '072' in u_raw: unidad = "Unidad 072 (Bomberos / Ataque)"
        elif '073' in u_raw: unidad = "Unidad 073 (Pipa / Agua)"
        elif '096' in u_raw or 'O96' in u_raw: unidad = "Unidad 096 (Rescate / Apoyo)"
        elif '047' in u_raw: unidad = "Unidad 047"
        elif '041' in u_raw: unidad = "Unidad 041"
        elif '097' in u_raw: unidad = "Unidad 097 (Ambulancia en Apoyo)"
        elif '098' in u_raw: unidad = "Unidad 098 (Ambulancia en Apoyo)"
        elif '208' in u_raw: unidad = "Unidad 208 (Ambulancia en Apoyo)"
        elif 'PIPA' in u_raw: unidad = "Pipa de Bomberos"

    # Identificar tipo de incendio
    if 'pastizal' in t_lower:
        tipo = "Incendio de Pastizal / Maleza"
    elif any(k in t_lower for k in ['casa', 'habitaci[oó]n', 'domicilio', 'vivienda']):
        tipo = "Incendio en Casa Habitación / Domicilio"
    elif 'basura' in t_lower or 'basurero' in t_lower:
        tipo = "Quema / Incendio de Basura"
    elif 'llanta' in t_lower:
        tipo = "Incendio de Llantas"
    elif any(k in t_lower for k in ['veh[ií]culo', 'auto', 'carro', 'camioneta', 'moto', 'trailer']):
        tipo = "Incendio de Vehículo"
    elif any(k in t_lower for k in ['comercio', 'local', 'taller', 'bodega']):
        tipo = "Incendio en Comercio / Bodega"
    elif 'conato' in t_lower:
        tipo = "Conato de Incendio"
    elif 'quema' in t_lower:
        tipo = "Quema de Vegetación / Residuos"
    else:
        tipo = "Incendio Forestal / Terreno Baldío"

    # Identificar ubicación
    ubicacion = "Medellín de Bravo (No especificado)"
    m_loc = re.search(r'(?:en\s+|colonia\s+|fracc\w*\s+|localidad\s+|carretera\s+|calle\s+|camino\s+)([A-Za-zÁÉÍÓÚáéíóúñÑ0-9\s]{4,35}?)(?:,|\.|\s+sale|\s+se|\s+con|\s+por|\s+entre|\n|$)', texto, re.IGNORECASE)
    if m_loc:
        loc_cand = m_loc.group(1).strip()
        if len(loc_cand) > 3 and not loc_cand.lower().startswith('el punto') and not loc_cand.lower().startswith('apoyo'):
            ubicacion = loc_cand.title()
    elif 'puente moreno' in t_lower: ubicacion = "Fracc. Lagos de Puente Moreno"
    elif 'el tejar' in t_lower: ubicacion = "Localidad El Tejar"
    elif 'playa de vacas' in t_lower: ubicacion = "Localidad Playa de Vacas"
    elif 'moralillo' in t_lower: ubicacion = "Localidad El Moralillo"
    elif 'los robles' in t_lower: ubicacion = "Localidad Los Robles"
    elif 'paso del toro' in t_lower: ubicacion = "Localidad Paso del Toro"
    elif 'rancho del padre' in t_lower: ubicacion = "Rancho del Padre"
    elif 'san ramón' in t_lower or 'san ramon' in t_lower: ubicacion = "Fracc. Arboledas San Ramón"

    # Despachador / Autoridad
    despacha = "Reporte Ciudadano a Base"
    if 'c5' in t_lower or '911' in t_lower: despacha = "C5 / 911"
    elif 'polic' in t_lower: despacha = "Policía Municipal / Estatal"
    elif 'agente' in t_lower: despacha = "Agente Municipal"

    # Estatus de la atención
    estatus = "Servicio Atendido por Bomberos"
    if 'sofoc' in t_lower:
        estatus = "Incendio Sofocado y Enfriado"
    elif 'controla' in t_lower:
        estatus = "Incendio Controlado"
    elif 'falsa alarma' in t_lower or 'sin novedad' in t_lower:
        estatus = "Controlado / Sin Riesgo a Población"

    mes_num = fecha.strftime('%m')
    nombre_mes = MAPA_MESES.get(mes_num, mes_num)

    servicios.append({
        'Fecha': fecha.strftime('%Y-%m-%d'),
        'Hora': fecha.strftime('%H:%M'),
        'Mes': nombre_mes,
        'Unidad': unidad,
        'Tipo_Incendio': tipo,
        'Estatus_Servicio': estatus,
        'Ubicacion': ubicacion,
        'Tiene_Foto': 'SÍ' if tiene_img else 'NO',
        'Despachador_Origen': despacha,
        'Personal_Remitente': push or "Personal Operativo",
        'Texto_Reporte': texto.replace('\n', ' ').strip()[:300]
    })

print(f"Total servicios de incendios únicos en 2026: {len(servicios)}")

# Generar Excel oficial con OpenPyXL
output_path = "c:/Users/burel/OneDrive/Documentos/PCivil Digital/Registro_Oficial_Incendios_Medellin_2026.xlsx"
wb = openpyxl.Workbook()

# ==========================================
# HOJA 1: REGISTRO GENERAL DE INCENDIOS
# ==========================================
ws = wb.active
ws.title = "Registro de Incendios 2026"
ws.views.sheetView[0].showGridLines = True

RED_HEADER = "822727"        # Rojo / Borgoña formal de Bomberos
NAVY_TITLE = "1B365D"
WHITE = "FFFFFF"
GRAY_BORDER = "D1D5DB"
ZEBRA_FILL = "FFF5F5"        # Tinte tenue rojizo institucional

ws.merge_cells('A1:K1')
ws['A1'] = "H. AYUNTAMIENTO DE MEDELLÍN DE BRAVO, VERACRUZ"
ws['A1'].font = Font(name='Arial', size=14, bold=True, color=NAVY_TITLE)
ws['A1'].alignment = Alignment(horizontal='center', vertical='center')

ws.merge_cells('A2:K2')
ws['A2'] = "DIRECCIÓN MUNICIPAL DE PROTECCIÓN CIVIL Y CUERPO DE BOMBEROS"
ws['A2'].font = Font(name='Arial', size=11, bold=True, color="7F1D1D")
ws['A2'].alignment = Alignment(horizontal='center', vertical='center')

ws.merge_cells('A3:K3')
ws['A3'] = "BITÁCORA OFICIAL DE SALIDAS Y ATENCIÓN A INCENDIOS Y QUEMAS (ENERO - SEPTIEMBRE 2026)"
ws['A3'].font = Font(name='Arial', size=10, italic=True, color="4B5563")
ws['A3'].alignment = Alignment(horizontal='center', vertical='center')

ws.row_dimensions[1].height = 24
ws.row_dimensions[2].height = 18
ws.row_dimensions[3].height = 18
ws.row_dimensions[4].height = 8
ws.row_dimensions[5].height = 28

columnas = [
    ("No. Folio", 10, 'center'),
    ("Fecha", 12, 'center'),
    ("Hora", 9, 'center'),
    ("Mes", 12, 'center'),
    ("Unidad de Bomberos", 26, 'center'),
    ("Tipo de Incendio", 34, 'left'),
    ("Estatus / Resultado", 30, 'center'),
    ("Ubicación / Localidad", 34, 'left'),
    ("Evidencia Foto", 14, 'center'),
    ("Origen del Reporte", 26, 'left'),
    ("Texto del Despacho Oficial", 55, 'left')
]

thin_border = Border(
    left=Side(style='thin', color=GRAY_BORDER),
    right=Side(style='thin', color=GRAY_BORDER),
    top=Side(style='thin', color=GRAY_BORDER),
    bottom=Side(style='thin', color=GRAY_BORDER)
)

header_fill = PatternFill(start_color=RED_HEADER, end_color=RED_HEADER, fill_type="solid")
header_font = Font(name='Arial', size=10, bold=True, color=WHITE)

for col_idx, (col_name, col_width, col_align) in enumerate(columnas, 1):
    cell = ws.cell(row=5, column=col_idx)
    cell.value = col_name
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    cell.border = thin_border
    col_letter = get_column_letter(col_idx)
    ws.column_dimensions[col_letter].width = col_width

data_font = Font(name='Arial', size=9)
zebra_pattern = PatternFill(start_color=ZEBRA_FILL, end_color=ZEBRA_FILL, fill_type="solid")
white_pattern = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

# Formato de tipo de incendio
fill_pastizal = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
font_pastizal = Font(name='Arial', size=9, bold=True, color="92400E")

fill_casa = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
font_casa = Font(name='Arial', size=9, bold=True, color="991B1B")

fill_vehiculo = PatternFill(start_color="FFEDD5", end_color="FFEDD5", fill_type="solid")
font_vehiculo = Font(name='Arial', size=9, bold=True, color="9A3412")

for row_idx, r in enumerate(servicios):
    current_row = row_idx + 6
    ws.row_dimensions[current_row].height = 20
    is_even = (row_idx % 2 == 0)
    row_fill = white_pattern if is_even else zebra_pattern
    
    valores = [
        row_idx + 1,
        r['Fecha'],
        r['Hora'],
        r['Mes'],
        r['Unidad'],
        r['Tipo_Incendio'],
        r['Estatus_Servicio'],
        r['Ubicacion'],
        r['Tiene_Foto'],
        r['Despachador_Origen'],
        r['Texto_Reporte']
    ]
    
    for col_idx, val in enumerate(valores, 1):
        cell = ws.cell(row=current_row, column=col_idx, value=val)
        cell.font = data_font
        cell.border = thin_border
        cell.fill = row_fill
        
        align_type = columnas[col_idx - 1][2]
        cell.alignment = Alignment(horizontal=align_type, vertical='center')
        
        if col_idx == 6: # Tipo de Incendio
            if "Pastizal" in str(val):
                cell.fill = fill_pastizal
                cell.font = font_pastizal
            elif "Casa Habitación" in str(val):
                cell.fill = fill_casa
                cell.font = font_casa
            elif "Vehículo" in str(val):
                cell.fill = fill_vehiculo
                cell.font = font_vehiculo

ws.auto_filter.ref = f"A5:K{len(servicios) + 5}"
ws.freeze_panes = "A6"

# ==========================================
# HOJA 2: ESTADÍSTICAS Y GRÁFICAS DE INCENDIOS
# ==========================================
ws2 = wb.create_sheet(title="Estadísticas de Incendios 2026")
ws2.views.sheetView[0].showGridLines = True

ws2['A1'] = "ANÁLISIS ESTADÍSTICO DE INCENDIOS - PROTECCIÓN CIVIL Y BOMBEROS MEDELLÍN (2026)"
ws2['A1'].font = Font(name='Arial', size=13, bold=True, color="7F1D1D")

df_s = pd.DataFrame(servicios)
total_inc = len(df_s)

# Tabla 1: Por Tipo
ws2['A3'] = "INCENDIOS POR CLASIFICACIÓN"
ws2['A3'].font = Font(name='Arial', size=11, bold=True, color=RED_HEADER)
ws2['A4'] = "Tipo de Incendio"
ws2['B4'] = "Total Servicios"
ws2['C4'] = "Porcentaje"
for c in ['A4', 'B4', 'C4']:
    ws2[c].fill = header_fill
    ws2[c].font = header_font
    ws2[c].alignment = Alignment(horizontal='center')

r_idx = 5
for t_inc, cant in df_s['Tipo_Incendio'].value_counts().items():
    ws2.cell(row=r_idx, column=1, value=t_inc).font = data_font
    ws2.cell(row=r_idx, column=2, value=cant).alignment = Alignment(horizontal='center')
    ws2.cell(row=r_idx, column=3, value=f"{(cant/total_inc)*100:.1f}%").alignment = Alignment(horizontal='center')
    r_idx += 1

# Tabla 2: Por Mes
ws2['E3'] = "INCENDIOS POR MES (TEMPORADA DE ESTIAJE)"
ws2['E3'].font = Font(name='Arial', size=11, bold=True, color=RED_HEADER)
ws2['E4'] = "Mes"
ws2['F4'] = "Total Servicios"
ws2['G4'] = "Porcentaje"
for c in ['E4', 'F4', 'G4']:
    ws2[c].fill = header_fill
    ws2[c].font = header_font
    ws2[c].alignment = Alignment(horizontal='center')

r_idx2 = 5
for m_num, m_name in MAPA_MESES.items():
    cant = len(df_s[df_s['Mes'] == m_name])
    if cant > 0:
        ws2.cell(row=r_idx2, column=5, value=m_name).font = data_font
        ws2.cell(row=r_idx2, column=6, value=cant).alignment = Alignment(horizontal='center')
        ws2.cell(row=r_idx2, column=7, value=f"{(cant/total_inc)*100:.1f}%").alignment = Alignment(horizontal='center')
        r_idx2 += 1

# Tabla 3: Por Unidad
ws2['A17'] = "DESPACHOS POR UNIDAD MÓVIL"
ws2['A17'].font = Font(name='Arial', size=11, bold=True, color=RED_HEADER)
ws2['A18'] = "Unidad"
ws2['B18'] = "Salidas"
for c in ['A18', 'B18']:
    ws2[c].fill = header_fill
    ws2[c].font = header_font
    ws2[c].alignment = Alignment(horizontal='center')

r_idx3 = 19
for u_name, cant in df_s['Unidad'].value_counts().head(8).items():
    ws2.cell(row=r_idx3, column=1, value=u_name).font = data_font
    ws2.cell(row=r_idx3, column=2, value=cant).alignment = Alignment(horizontal='center')
    r_idx3 += 1

for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
    ws2.column_dimensions[col].width = 34 if col in ['A', 'E'] else 16

try:
    wb.save(output_path)
    print(f"\nArchivo guardado exitosamente en: {output_path}")
except PermissionError:
    alt_path = "c:/Users/burel/OneDrive/Documentos/PCivil Digital/Registro_Oficial_Incendios_Medellin_2026_V1.xlsx"
    wb.save(alt_path)
    print(f"\nGuardado en archivo alternativo: {alt_path}")
    output_path = alt_path

conn.close()
