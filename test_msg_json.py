import psycopg2
import json

conn = psycopg2.connect('postgresql://postgres:postgres@127.0.0.1:5432/evolution')
cur = conn.cursor()
cur.execute('''SELECT "message", "pushName", "key"->>'participant' FROM "Message" WHERE "key"->>'remoteJid' = '120363042493725288@g.us' ORDER BY "messageTimestamp" DESC LIMIT 1;''')
row = cur.fetchone()
print(json.dumps(row[0], indent=2))
