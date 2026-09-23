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
      AND "message"::text ILIKE '%%*NOMBRE DEL PACIENTE*%%'
    ORDER BY "messageTimestamp" DESC
    LIMIT 5;
''', (GROUP_JID,))

rows = cur.fetchall()
for i, r in enumerate(rows, 1):
    print(f"=== MUESTRA {i} ({r[0]} - {r[1]}) ===")
    print(r[2])
    print("\n")

conn.close()
