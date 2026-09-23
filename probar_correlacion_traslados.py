import psycopg2
import re
import pandas as pd
from datetime import datetime, timedelta

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()

GROUP_JID = '120363042493725288@g.us'

# Obtener todos los mensajes del grupo ordenados cronológicamente
cur.execute('''
    SELECT 
        "id",
        to_timestamp("messageTimestamp") as fecha_msg,
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
        "key"->>'id' as wa_id,
        "message"
    FROM "Message"
    WHERE "key"->>'remoteJid' = %s
    ORDER BY "messageTimestamp" ASC
''', (GROUP_JID,))

todos_los_mensajes = cur.fetchall()
print(f"Total mensajes cargados: {len(todos_los_mensajes)}")

# Analicemos los términos usados para traslados
patrones_traslado = [
    r'traslado', r'paciente', r'hospital', r'cl[ií]nica', r'urgencia',
    r'ambulancia', r'dx:', r'frap', r'atropellado', r'choque', r'derrapado'
]

mensajes_traslado = []
for idx, m in enumerate(todos_los_mensajes):
    mid, fecha, push, mtype, txt, tiene_img, wa_id, mjson = m
    if not txt:
        continue
    txt_lower = txt.lower()
    if any(re.search(p, txt_lower) for p in patrones_traslado):
        mensajes_traslado.append((idx, m))

print(f"Mensajes que mencionan términos de atención médica / traslado / ambulancia: {len(mensajes_traslado)}")

# Ver muestras de salidas específicas de ambulancias
salidas_amb = []
for idx, m in enumerate(todos_los_mensajes):
    mid, fecha, push, mtype, txt, tiene_img, wa_id, mjson = m
    if not txt:
        continue
    txt_lower = txt.lower().strip()
    if txt_lower.startswith('sale') and any(u in txt_lower for u in ['097', '098', '208', 'ambulancia']):
        salidas_amb.append((fecha, push, txt, tiene_img))

print(f"\nTotal mensajes de 'Sale ambulancia / Sale unidad 097, 098, 208': {len(salidas_amb)}")
print("Primeras 5 salidas de ambulancia registradas:")
for s in salidas_amb[:5]:
    print(f"  [{s[0].strftime('%Y-%m-%d %H:%M')}] {s[1]} (Tiene foto: {s[3]}): {s[2]}")

print("\nÚltimas 5 salidas de ambulancia registradas:")
for s in salidas_amb[-5:]:
    print(f"  [{s[0].strftime('%Y-%m-%d %H:%M')}] {s[1]} (Tiene foto: {s[3]}): {s[2]}")

conn.close()
