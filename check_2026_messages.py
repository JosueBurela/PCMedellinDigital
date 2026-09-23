import psycopg2

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()
GROUP_JID = '120363042493725288@g.us'

cur.execute('''
    SELECT 
        to_char(to_timestamp("messageTimestamp"), 'YYYY-MM') as mes,
        count(*)
    FROM "Message"
    WHERE "key"->>'remoteJid' = %s
    GROUP BY mes
    ORDER BY mes ASC;
''', (GROUP_JID,))

print(f"Desglose de mensajes por mes para el grupo {GROUP_JID}:")
for row in cur.fetchall():
    print(f"  Mes: {row[0]} -> {row[1]} mensajes")

conn.close()
