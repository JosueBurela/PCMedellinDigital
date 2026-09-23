import psycopg2
import re
import pandas as pd
from datetime import datetime, timedelta

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
print(f"Total mensajes en 2026 para Protección Civil Medellín: {len(todos_2026)}")

# Palabras clave de incendios
regex_fuego = re.compile(r'\b(incendio|incendios|quema|quemas|pastizal|pastizales|fuego|conato|humo|sofoca|sofocad|sofocaci[oó]n|bomberos?|llantas?|basurero|chispas?)\b', re.IGNORECASE)

# Palabras de salida / despacho
regex_salida = re.compile(r'\b(sale|salida|en ruta|al punto|acude|atender|reportan|reporte de)\b', re.IGNORECASE)

servicios_incendios = []

for idx, m in enumerate(todos_2026):
    mid, fecha, push, mtype, texto, tiene_img, wa_id = m
    if not texto:
        continue
    t_lower = texto.lower()
    
    # Debe tener relación con fuego / incendio
    if not regex_fuego.search(t_lower):
        continue
        
    # Filtrar falsos positivos médicos (ej: "quemadura" de piel en accidente)
    if 'quemadura de' in t_lower or 'quemadura por' in t_lower or 'quemaduras en' in t_lower:
        if not any(k in t_lower for k in ['pastizal', 'casa', 'basura', 'fuego', 'sofoc', 'pipa', 'apagar']):
            continue

    # Detectar si es salida o reporte operativo
    es_salida = False
    if regex_salida.search(t_lower):
        es_salida = True
    elif any(k in t_lower for k in ['incendio de pastizal', 'incendio en', 'quema de basura', 'quema de pastizal', 'conato de incendio']):
        es_salida = True
        
    if es_salida:
        # Extraer unidad
        m_u = re.search(r'(unidad\s*\d+|u-\d+|m[oó]vil\s*\d+|pipa|096|072|073|047|041|097|098|208)', t_lower)
        unidad = m_u.group(0).upper() if m_u else "Unidad Bomberos / PC"
        
        # Extraer tipo de incendio
        tipo_incendio = "Incendio no especificado"
        if 'pastizal' in t_lower:
            tipo_incendio = "Incendio de Pastizal / Maleza"
        elif 'casa' in t_lower or 'habitaci[oó]n' in t_lower or 'domicilio' in t_lower:
            tipo_incendio = "Incendio en Casa Habitación / Domicilio"
        elif 'basura' in t_lower or 'basurero' in t_lower:
            tipo_incendio = "Quema / Incendio de Basura"
        elif 'llanta' in t_lower:
            tipo_incendio = "Incendio de Llantas"
        elif 'veh[ií]culo' in t_lower or 'auto' in t_lower or 'carro' in t_lower or 'camioneta' in t_lower or 'moto' in t_lower:
            tipo_incendio = "Incendio de Vehículo"
        elif 'comercio' in t_lower or 'local' in t_lower or 'taller' in t_lower:
            tipo_incendio = "Incendio en Comercio / Taller"
        elif 'conato' in t_lower:
            tipo_incendio = "Conato de Incendio"
        elif 'quema' in t_lower:
            tipo_incendio = "Quema de Vegetación / Residuos"

        # Extraer ubicación si se menciona
        m_loc = re.search(r'(?:en\s+|colonia\s+|fracc\w*\s+|localidad\s+|carretera\s+|calle\s+)([A-Za-zÁÉÍÓÚáéíóúñÑ0-9\s]{4,35}?)(?:,|\.|\s+sale|\s+se|\s+con|\s+por|\n|$)', texto, re.IGNORECASE)
        ubicacion = m_loc.group(1).strip() if m_loc else "Medellín de Bravo"
        
        servicios_incendios.append({
            'id': mid,
            'wa_id': wa_id,
            'fecha': fecha,
            'fecha_str': fecha.strftime('%Y-%m-%d'),
            'hora_str': fecha.strftime('%H:%M'),
            'mes': fecha.strftime('%Y-%m'),
            'unidad': unidad,
            'tipo_incendio': tipo_incendio,
            'ubicacion': ubicacion,
            'remitente': push or "Personal PC",
            'tiene_foto': 'SÍ' if tiene_img else 'NO',
            'texto_original': texto.replace('\n', ' ').strip()
        })

print(f"\nTotal salidas / despachos a incendios identificados en 2026: {len(servicios_incendios)}")

df_inc = pd.DataFrame(servicios_incendios)

# Conteo por tipo de incendio
print("\n--- DISTRIBUCIÓN POR TIPO DE INCENDIO ---")
print(df_inc['tipo_incendio'].value_counts())

# Conteo por mes en 2026
print("\n--- DISTRIBUCIÓN POR MES (2026) ---")
print(df_inc['mes'].value_counts().sort_index())

# Conteo por unidad
print("\n--- UNIDADES QUE ACUDIERON A INCENDIOS ---")
print(df_inc['unidad'].value_counts().head(10))

# Guardar a Excel para que el usuario lo tenga listo
excel_incendios = "c:/Users/burel/OneDrive/Documentos/PCivil Digital/Registro_Salidas_Incendios_Medellin_2026.xlsx"
df_inc.to_excel(excel_incendios, index=False)
print(f"\nExcel guardado en: {excel_incendios}")

# Mostrar 15 salidas reales con formato limpio
print("\n--- MUESTRA DE 15 SALIDAS REALES A INCENDIOS ---")
for i, r in df_inc.head(15).iterrows():
    f = r['fecha'].strftime('%Y-%m-%d %H:%M')
    u = r['unidad']
    ti = r['tipo_incendio']
    loc = r['ubicacion']
    txt = r['texto_original'][:80]
    # codificar a ascii seguro para terminal
    linea = f"[{f}] {u:15s} | {ti:32s} | Ubic: {loc[:25]:25s} | {txt}"
    print(linea.encode('ascii', errors='replace').decode('ascii'))

conn.close()
