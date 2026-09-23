import psycopg2
import re
from datetime import datetime

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()

GROUP_JID = '120363042493725288@g.us'

# Buscar todos los mensajes del grupo
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
    ORDER BY "messageTimestamp" ASC
''', (GROUP_JID,))

rows = cur.fetchall()
print(f"Total mensajes cargados: {len(rows)}")

palabras_clave = [
    'incendio', 'quema', 'pastizal', 'fuego', 'conato', 'humo', 
    'basurero', 'llantas', 'sofoc', 'chispazo', 'chispas'
]

mensajes_incendios = []
salidas_incendios = []

for r in rows:
    db_id, fecha, remitente, mtype, texto, tiene_img, wa_id = r
    if not texto:
        continue
    t_lower = texto.lower()
    
    # Excluir falsos positivos comunes si los hubiera
    if any(p in t_lower for p in palabras_clave):
        mensajes_incendios.append(r)
        
        # Detectar si es una salida directa de unidad
        es_salida = False
        if any(t_lower.strip().startswith(s) for s in ['sale', 'unidad sale', 'u-']) or 'sale a ' in t_lower or 'sale al ' in t_lower or 'sale en apoyo' in t_lower or 'al punto' in t_lower:
            es_salida = True
        elif 'reporte de' in t_lower or 'reportan' in t_lower:
            es_salida = True
            
        if es_salida:
            salidas_incendios.append(r)

print(f"\nResultados encontrados en el historial (Junio a Septiembre 2026):")
print(f"  - Total mensajes relacionados con fuego / incendios / quemas: {len(mensajes_incendios)}")
print(f"  - Mensajes de SALIDAS / REPORTES a atender incendios: {len(salidas_incendios)}")

print("\n--- PRIMERAS 10 SALIDAS DE INCENDIOS ---")
for s in salidas_incendios[:10]:
    t_clean = s[4].replace('\n', ' ')[:90]
    print(f"[{s[1].strftime('%Y-%m-%d %H:%M')}] {s[2] or 'Sin remitente'} (Foto: {s[5]}): {t_clean}")

print("\n--- ÚLTIMAS 10 SALIDAS DE INCENDIOS ---")
for s in salidas_incendios[-10:]:
    t_clean = s[4].replace('\n', ' ')[:90]
    print(f"[{s[1].strftime('%Y-%m-%d %H:%M')}] {s[2] or 'Sin remitente'} (Foto: {s[5]}): {t_clean}")

conn.close()
