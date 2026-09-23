import psycopg2
import re

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()

GROUP_JID = '120363042493725288@g.us'

cur.execute('''
    SELECT 
        to_timestamp("messageTimestamp") as fecha,
        "pushName",
        COALESCE(
            "message"->>'conversation',
            "message"->'extendedTextMessage'->>'text',
            "message"->'imageMessage'->>'caption',
            ''
        ) as texto
    FROM "Message"
    WHERE "key"->>'remoteJid' = %s
      AND to_timestamp("messageTimestamp") BETWEEN '2026-01-01 00:00:00' AND '2026-05-31 23:59:59'
      AND (
          "message"::text ILIKE '%%paciente%%'
          OR "message"::text ILIKE '%%traslado%%'
          OR "message"::text ILIKE '%%ambulancia%%'
      )
    ORDER BY "messageTimestamp" ASC
    LIMIT 10;
''', (GROUP_JID,))

rows = cur.fetchall()
print(f"Muestras de Enero a Mayo 2026 ({len(rows)} encontradas):")
for r in rows:
    f, push, txt = r
    print("=" * 80)
    print(f"[{f.strftime('%Y-%m-%d %H:%M')}] Remitente: {push}")
    print(txt[:250].replace('\n', ' '))

conn.close()
