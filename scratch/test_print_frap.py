import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('whatsapp_messages.db')
c = conn.cursor()
c.execute("SELECT id, text_content FROM messages WHERE text_content LIKE '%HOSPITAL DE TRASLADO%' LIMIT 3")
rows = c.fetchall()
for r in rows:
    print(f"\n--- ID: {r[0]} ---")
    print(r[1])
conn.close()
