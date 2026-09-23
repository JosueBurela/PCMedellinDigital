import psycopg2
import time
from datetime import datetime

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()
GROUP_JID = '120363042493725288@g.us'

cur.execute('SELECT count(*), min("messageTimestamp"), max("messageTimestamp") FROM "Message" WHERE "key"->>\'remoteJid\' = %s', (GROUP_JID,))
row1 = cur.fetchone()
print(f"Total actual: {row1[0]} mensajes en el grupo de PC.")
print(f"Rango de fechas actual en DB: {datetime.fromtimestamp(row1[1])} hasta {datetime.fromtimestamp(row1[2])}")

# Revisar total general en la base de datos
cur.execute('SELECT count(*) FROM "Message"')
print(f"Total general en la base de datos: {cur.fetchone()[0]} mensajes")

conn.close()
