import psycopg2
import json
from datetime import datetime

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()

GROUP_JID = '120363042493725288@g.us'

query = '''
    SELECT 
        to_timestamp("messageTimestamp") as fecha,
        "pushName",
        "messageType",
        COALESCE(
            "message"->>'conversation',
            "message"->'extendedTextMessage'->>'text',
            "message"->'imageMessage'->>'caption',
            "message"->'videoMessage'->>'caption',
            "message"->'documentMessage'->>'caption',
            ''
        ) as texto,
        "message"->'imageMessage' IS NOT NULL as tiene_imagen,
        "key"->>'id' as msg_id
    FROM "Message"
    WHERE "key"->>'remoteJid' = %s
      AND (
          "message"::text ILIKE '%%traslado%%'
          OR "message"::text ILIKE '%%sale%%'
          OR "message"::text ILIKE '%%paciente%%'
          OR "message"::text ILIKE '%%hospital%%'
          OR "message"::text ILIKE '%%clínica%%'
          OR "message"::text ILIKE '%%clinica%%'
      )
    ORDER BY "messageTimestamp" DESC
    LIMIT 30;
'''

cur.execute(query, (GROUP_JID,))
rows = cur.fetchall()

print(f"Encontrados registros coincidentes (mostrando ultimos {len(rows)}):")
for r in rows:
    fecha, remitente, mtype, txt, img, mid = r
    txt_clean = (txt or '').replace('\n', ' ')[:100]
    print(f"[{fecha.strftime('%Y-%m-%d %H:%M')}] {remitente or 'Sin remitente'} ({mtype}) [Img:{img}]: {txt_clean}")

conn.close()
