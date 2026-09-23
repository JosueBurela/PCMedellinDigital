import sqlite3
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('whatsapp_messages.db')
c = conn.cursor()
c.execute("""
SELECT id, datetime(message_timestamp, 'unixepoch', 'localtime') as dt, text_content
FROM messages
WHERE (text_content LIKE '%traslad%' OR text_content LIKE '%hospital%')
  AND (text_content LIKE '%PX:%' OR text_content LIKE '%Paciente%' OR text_content LIKE '%se traslada%')
ORDER BY message_timestamp ASC
""")
rows = c.fetchall()
print(f"Total mensajes candidatos: {len(rows)}")

for r in rows:
    t = r[2].replace('\n', ' ')
    # Buscar si hay un nombre propio con mayúsculas
    m = re.search(r'(?:px|paciente|ciudadano|traslado autorizado)[:\s]+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,3})', t)
    if m:
        name = m.group(1).strip()
        # Filtrar si son palabras comunes
        if not any(w in name.lower() for w in ['femenina', 'masculino', 'adulto', 'menor', 'que', 'en', 'por', 'al', 'se', 'del', 'con']):
            print(f"[{r[1]}] Nombre: '{name}'")
            print(f"  Texto: {t[:120]}")
            print("-" * 60)

conn.close()
