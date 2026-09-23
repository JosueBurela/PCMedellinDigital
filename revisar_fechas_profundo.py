import psycopg2
from datetime import datetime

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()
GROUP_JID = '120363042493725288@g.us'

# 1. En el grupo de Protección Civil
cur.execute('''
    SELECT count(*), min("messageTimestamp"), max("messageTimestamp")
    FROM "Message"
    WHERE "key"->>'remoteJid' = %s
''', (GROUP_JID,))
row = cur.fetchone()
print(f"Total mensajes en Protección Civil: {row[0]}")
if row[1] and row[2]:
    print(f"  -> Más antiguo en PC: {datetime.fromtimestamp(row[1])}")
    print(f"  -> Más reciente en PC: {datetime.fromtimestamp(row[2])}")

# 2. En toda la base de datos (para ver hasta qué fecha ha alcanzado la sincronización)
cur.execute('''
    SELECT count(*), min("messageTimestamp"), max("messageTimestamp")
    FROM "Message"
''')
g_row = cur.fetchone()
print(f"\nTotal general en la base de datos: {g_row[0]}")
if g_row[1] and g_row[2]:
    print(f"  -> Mensaje más antiguo global: {datetime.fromtimestamp(g_row[1])}")
    print(f"  -> Mensaje más reciente global: {datetime.fromtimestamp(g_row[2])}")

# 3. Revisar si hay otros grupos o chats con fechas anteriores a junio
cur.execute('''
    SELECT "key"->>'remoteJid', min("messageTimestamp")
    FROM "Message"
    GROUP BY "key"->>'remoteJid'
    ORDER BY min("messageTimestamp") ASC
    LIMIT 5;
''')
print("\nChats con fechas más antiguas registradas hasta el momento:")
for r in cur.fetchall():
    d = datetime.fromtimestamp(r[1]) if r[1] else 'N/A'
    print(f"  {r[0]} -> {d}")

conn.close()
