import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('whatsapp_messages.db')
c = conn.cursor()
c.execute("SELECT count(*) FROM messages WHERE text_content LIKE '%AMBULANCIA%'")
print(f"Total con AMBULANCIA: {c.fetchone()[0]}")

c.execute("SELECT count(*) FROM messages WHERE text_content LIKE '%PARAMEDICO%' OR text_content LIKE '%PARAMÉDICO%'")
print(f"Total con PARAMEDICO: {c.fetchone()[0]}")

c.execute("SELECT id, datetime(message_timestamp, 'unixepoch', 'localtime') as dt, text_content FROM messages WHERE text_content LIKE '%OPERADOR%' LIMIT 10")
rows = c.fetchall()
print(f"\nTotal filas mostradas: {len(rows)}")
for r in rows:
    print(f"[{r[1]}] {r[2][:150].replace('\n', ' ')}")

conn.close()
