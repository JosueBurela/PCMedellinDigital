import psycopg2
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()

cur.execute('''
    SELECT "id", "remoteJid", "name", "instanceId"
    FROM "Chat"
    WHERE "name" ILIKE '%protec%civil%medell%'
''')
for r in cur.fetchall():
    print("Chat:", r)

conn.close()
