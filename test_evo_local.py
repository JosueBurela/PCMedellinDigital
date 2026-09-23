import psycopg2
import time
from datetime import datetime
conn = psycopg2.connect('postgresql://postgres:postgres@127.0.0.1:5432/evolution')
cur = conn.cursor()
yesterday = int(time.time()) - 86400 * 4
cur.execute(f'SELECT "messageTimestamp" FROM "Message" WHERE "messageTimestamp" >= {yesterday} ORDER BY "messageTimestamp" DESC LIMIT 5;')
for row in cur.fetchall():
    print(datetime.fromtimestamp(row[0]).strftime('%Y-%m-%d %H:%M:%S'))
