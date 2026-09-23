import psycopg2
from datetime import datetime
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()

# Columnas de Chat
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'Chat'")
print("Columnas de Chat:", [c[0] for c in cur.fetchall()])

# Buscar en Chat los nombres
cur.execute('''
    SELECT "id", "name"
    FROM "Chat"
    WHERE "name" ILIKE '%protec%' OR "name" ILIKE '%medell%' OR "name" ILIKE '%semana%' OR "name" ILIKE '%reporte%' OR "name" ILIKE '%guardia%'
''')
print("\n=== GRUPOS RELACIONADOS EN CHAT ===")
for r in cur.fetchall():
    print(r)

# Buscar en Message todos los remoteJid de grupos (@g.us) y sus fechas
cur.execute('''
    SELECT 
        "key"->>'remoteJid' as jid,
        count(*) as total,
        min("messageTimestamp") as min_ts,
        max("messageTimestamp") as max_ts
    FROM "Message"
    WHERE "key"->>'remoteJid' LIKE '%@g.us'
    GROUP BY "key"->>'remoteJid'
    ORDER BY total DESC;
''')
print("\n=== GRUPOS EN MESSAGE CON FECHAS ===")
for r in cur.fetchall():
    min_d = datetime.fromtimestamp(r[2]) if r[2] else 'N/A'
    max_d = datetime.fromtimestamp(r[3]) if r[3] else 'N/A'
    print(f"JID: {r[0]} | Total: {r[1]} | Desde: {min_d} Hasta: {max_d}")

conn.close()
