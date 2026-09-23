import psycopg2
import re
from datetime import datetime

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
        "message"
    FROM "Message"
    WHERE "key"->>'remoteJid' = %s
    ORDER BY "messageTimestamp" ASC
''', (GROUP_JID,))

rows = cur.fetchall()
print(f"Total mensajes procesados: {len(rows)}")

partes_medicos = []
salidas_unidades = []

for r in rows:
    msg_id, fecha, remitente, mtype, texto, tiene_img, msg_json = r
    if not texto:
        continue
    
    txt_lower = texto.lower()
    
    # Detección de partes de servicio / reporte médico
    es_parte = False
    if any(k in txt_lower for k in ['*nombre del paciente*', 'nombre del paciente', '*paciente*:', '*hospital de traslado*', 'hospital de traslado', '*ambulancia*:', '*tipo de servicio*']):
        es_parte = True
    elif 'paciente' in txt_lower and any(k in txt_lower for k in ['diagnostico', 'diagnóstico', 'traslado', 'edad']):
        es_parte = True
        
    if es_parte:
        partes_medicos.append({
            'id': msg_id,
            'fecha': fecha,
            'remitente': remitente,
            'texto': texto,
            'tiene_img': tiene_img
        })
        
    # Detección de salidas de unidades
    if any(txt_lower.strip().startswith(s) for s in ['sale unidad', 'sale la unidad', 'sale u', 'sale o', 'sale movil', 'sale móvil', 'unidad sale', 'u-']) or 'sale a ' in txt_lower or 'sale al ' in txt_lower:
        salidas_unidades.append({
            'id': msg_id,
            'fecha': fecha,
            'remitente': remitente,
            'texto': texto,
            'tiene_img': tiene_img
        })

print(f"\n--- RESUMEN ENCONTRADO EN EL HISTORIAL (Junio a Septiembre 2026) ---")
print(f"1. Fichas / Partes Médicos de Servicios y Pacientes: {len(partes_medicos)}")
print(f"2. Mensajes de 'Salida de Unidad' (Despachos/Gasolina/Servicios): {len(salidas_unidades)}")

# Clasificación de traslados dentro de los partes médicos
traslados_efectivos = []
traslados_negados = []
no_amerito = []
otros_partes = []

for p in partes_medicos:
    t = p['texto'].lower()
    if 'se niega a traslado' in t or 'niega traslado' in t or 'se niega' in t:
        traslados_negados.append(p)
    elif 'no ameritó traslado' in t or 'no amerito traslado' in t or 'no amerita traslado' in t:
        no_amerito.append(p)
    elif 'hospital de traslado' in t or 'traslado a' in t or 'hospital' in t or 'imss' in t or 'issste' in t or 'regional' in t:
        traslados_efectivos.append(p)
    else:
        otros_partes.append(p)

print(f"\nDesglose de Partes Médicos:")
print(f"  - Traslados a Hospital / Efectivos: {len(traslados_efectivos)}")
print(f"  - Paciente se negó a traslado: {len(traslados_negados)}")
print(f"  - No ameritó traslado: {len(no_amerito)}")
print(f"  - Otros reportes de atención en sitio: {len(otros_partes)}")

conn.close()
