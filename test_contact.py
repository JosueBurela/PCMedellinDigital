import psycopg2

conn = psycopg2.connect('postgresql://postgres:postgres@127.0.0.1:5432/evolution')
cur = conn.cursor()
cur.execute('''SELECT * FROM "Contact" LIMIT 5;''')
rows = cur.fetchall()
for r in rows:
    print(r)
