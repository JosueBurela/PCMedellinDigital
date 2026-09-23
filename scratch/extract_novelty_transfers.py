import sqlite3
import pandas as pd
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('whatsapp_messages.db')
c = conn.cursor()
c.execute("""
SELECT id, datetime(message_timestamp, 'unixepoch', 'localtime') as dt, text_content
FROM messages
WHERE text_content LIKE '%novedades del día%' OR text_content LIKE '%novedades del dia%'
ORDER BY message_timestamp ASC
""")
rows = c.fetchall()
print(f"Total mensajes de novedades diarias: {len(rows)}")

traslados_novedades = []

for r in rows:
    msg_id, dt, text = r
    # Dividir por horas (ej: 09:33 sale unidad...)
    # Regex para buscar horas tipo 07:05, 12:55, etc.
    lineas = re.split(r'(?=\b\d{1,2}:\d{2}\b)', text)
    for l in lineas:
        l_clean = l.strip().replace('\n', ' ')
        l_low = l_clean.lower()
        if any(w in l_low for w in ['traslada', 'traslado', 'trasladar', 'hospital', 'clínica', 'clinica', 'cruz roja', 'imss', 'issste', 'hg', 'hosnaver']):
            if not any(w in l_low for w in ['no ameritó traslado', 'no amerito traslado', 'no requirió traslado']):
                traslados_novedades.append({
                    'msg_id': msg_id,
                    'fecha_guardia': dt,
                    'evento_texto': l_clean
                })

print(f"\nTotal eventos de traslados extraídos de novedades: {len(traslados_novedades)}")
for i, tn in enumerate(traslados_novedades):
    print(f"[{i+1}] ({tn['fecha_guardia']}) {tn['evento_texto']}")

conn.close()
