import psycopg2
import json

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()

GROUP_JID = '120363042493725288@g.us'

query = '''
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
      AND (
          "message"::text ILIKE '%%*FECHA*%%'
          OR "message"::text ILIKE '%%*AMBULANCIA*%%'
          OR "message"::text ILIKE '%%*PACIENTE*%%'
          OR "message"::text ILIKE '%%TRASLADO%%'
      )
    ORDER BY "messageTimestamp" DESC
    LIMIT 10;
'''

cur.execute(query, (GROUP_JID,))
for row in cur.fetchall():
    print("=" * 80)
    print(f"FECHA MSG: {row[0]} | REMITENTE: {row[1]}")
    print("-" * 80)
    print(row[2])
    print("\n")

conn.close()
