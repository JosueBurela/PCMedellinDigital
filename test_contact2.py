import psycopg2
conn = psycopg2.connect('postgresql://postgres:postgres@127.0.0.1:5432/evolution')
cur = conn.cursor()
cur.execute('SELECT "remoteJid", "pushName" FROM "Contact" WHERE "remoteJid" LIKE \'%lid%\' LIMIT 20;')
for r in cur.fetchall(): print(r)
