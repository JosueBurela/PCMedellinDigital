import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('whatsapp_messages.db')
c = conn.cursor()
c.execute("SELECT id, text_content FROM messages WHERE text_content LIKE '%boca del r%' LIMIT 5")
rows = c.fetchall()
print(f"Total con 'boca del r': {len(rows)}")
for r in rows:
    print(f"\n--- ID {r[0]} ---")
    print(r[1][:400])
conn.close()
