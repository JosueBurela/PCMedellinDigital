import sqlite3
import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('whatsapp_messages.db')
c = conn.cursor()
c.execute("SELECT id, text_content FROM messages WHERE text_content LIKE '%Omar%'")
rows = c.fetchall()
print(f"Total en db con 'Omar': {len(rows)}")
for r in rows[:5]:
    print(f"[{r[0]}] {r[1][:200]}")
conn.close()

# En csv
df = pd.read_csv('reporte_mensual_agosto_limpio.csv')
print("\nTotal filas en reporte_mensual_agosto_limpio.csv:", len(df))
casos_con_paciente = df[df['Transcripcion_Incidente'].str.contains(r'paciente|traslad|hospital', case=False, na=False)]
print("Total casos con paciente/traslad/hospital en CSV:", len(casos_con_paciente))
