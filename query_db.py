import psycopg2
from datetime import datetime
conn = psycopg2.connect('postgresql://postgres:postgres@127.0.0.1:5432/evolution')
cur = conn.cursor()
cur.execute('SELECT MIN("messageTimestamp") FROM "Message";')
row = cur.fetchone()
print(row[0])
