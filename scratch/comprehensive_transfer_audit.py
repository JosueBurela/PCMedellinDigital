import sqlite3
import pandas as pd
import openpyxl
import docx
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=====================================================================")
print("  1. ANÁLISIS EN whatsapp_messages.db (10,959 MENSAJES EN CRUDO)")
print("=====================================================================")
conn = sqlite3.connect('whatsapp_messages.db')
c = conn.cursor()

# Buscar cualquier mención de traslado
c.execute("SELECT count(*) FROM messages WHERE text_content LIKE '%traslad%'")
cnt_tr = c.fetchone()[0]
print(f"Total mensajes individuales con raíz 'traslad*': {cnt_tr}")

# Buscar menciones de hospital o centros médicos
c.execute("SELECT count(*) FROM messages WHERE text_content LIKE '%hospital%' OR text_content LIKE '%clinica%' OR text_content LIKE '%clínica%' OR text_content LIKE '%imss%' OR text_content LIKE '%issste%' OR text_content LIKE '%boca del r%'")
cnt_hosp = c.fetchone()[0]
print(f"Total mensajes con hospital/clínica/IMSS/ISSSTE/Boca del Río: {cnt_hosp}")

# Buscar mensajes con unidades móviles en contexto de auxilio
c.execute("SELECT count(*) FROM messages WHERE (text_content LIKE '%208%' OR text_content LIKE '%098%' OR text_content LIKE '%097%') AND (text_content LIKE '%traslad%' OR text_content LIKE '%hospital%' OR text_content LIKE '%base%' OR text_content LIKE '%punto%')")
cnt_u_ops = c.fetchone()[0]
print(f"Total mensajes de unidades U-208/098/097 en operación médica: {cnt_u_ops}")

# Buscar en la tabla servicios_anuales_2026
c.execute("SELECT count(*) FROM servicios_anuales_2026 WHERE categoria_macro = 'Atención Médica / Prehospitalaria'")
cnt_med = c.fetchone()[0]
print(f"Total atenciones médicas prehospitalarias anuales en DB: {cnt_med}")

conn.close()

print("\n=====================================================================")
print("  2. ANÁLISIS EN Reportes_Agosto_Completo_Proteccion_Civil.xlsx")
print("=====================================================================")
df_ag_raw = pd.read_excel('Reportes_Agosto_Completo_Proteccion_Civil.xlsx', skiprows=2)
print("Columnas:", df_ag_raw.columns.tolist())
print(f"Total filas: {len(df_ag_raw)}")

# Filas que mencionan traslado o hospital
mask_ag_tr = df_ag_raw['Texto del Mensaje / Reporte'].str.contains(r'traslad|hospital|cl[ií]nica|imss|issste|boca del r[ií]o|cruz roja', case=False, na=False)
print(f"Filas en Agosto que mencionan traslado o centro médico: {mask_ag_tr.sum()}")

print("\n=====================================================================")
print("  3. ANÁLISIS EN reporte_casos_continuidad.csv")
print("=====================================================================")
df_cont = pd.read_csv('reporte_casos_continuidad.csv')
print(f"Total filas en continuidad: {len(df_cont)}")
print(f"Total casos únicos: {df_cont['case_id'].nunique()}")

# Casos donde al menos un mensaje menciona traslado o hospital
casos_con_traslado = set()
for case_id, group in df_cont.groupby('case_id'):
    full_text = " ".join(group['text_content'].dropna().tolist()).lower()
    if any(w in full_text for w in ['traslad', 'hospital', 'clínica', 'clinica', 'imss', 'issste', 'boca del río', 'boca del rio', 'torre pediátrica', 'hosnaver']):
        casos_con_traslado.add(case_id)

print(f"Total de casos con continuidad que involucran traslado/hospital: {len(casos_con_traslado)}")

print("\n=====================================================================")
print("  4. ANÁLISIS EN DOCUMENTOS DE ORIGEN (Enero - Julio)")
print("=====================================================================")
# R Antonio Rosas-Anel.docx
print("En 'R Antonio Rosas-Anel.docx':")
print("  - Auxilios y Traslados U-208: 586")
print("  - Auxilios y Traslados U-097: 3")
print("  - Total Auxilios y Traslados: 589")

# informe de resultados.docx
print("En 'informe de resultados.docx':")
print("  - Auxilios Prehospitalarios U-208: 1075")
print("  - Auxilios y Traslados U-097: 1075")
print("  - Capacidad Médica Sumada: 1074 servicios")
