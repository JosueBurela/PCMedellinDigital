import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('whatsapp_messages.db')
c = conn.cursor()
c.execute("SELECT id, text_content FROM messages WHERE text_content LIKE '%paciente%' LIMIT 5")
rows = c.fetchall()
print(f"Total encontrados con 'paciente': {len(rows)}")
for r in rows:
    print(f"\n--- ID: {r[0]} ---")
    print(r[1][:500])
conn.close()
