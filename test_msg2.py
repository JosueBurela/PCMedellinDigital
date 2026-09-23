import psycopg2
import json

conn = psycopg2.connect('postgresql://postgres:postgres@127.0.0.1:5432/evolution')
cur = conn.cursor()
cur.execute('''SELECT "pushName", "key"->>'participant' FROM "Message" WHERE "key"->>'remoteJid' = '120363042493725288@g.us' ORDER BY "messageTimestamp" DESC LIMIT 15;''')
rows = cur.fetchall()
for r in rows:
    print(f"Push: {r[0]}, Participant: {r[1]}")
