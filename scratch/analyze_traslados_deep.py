import sqlite3
import pandas as pd
import sys

# Forzar salida en utf-8
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('whatsapp_messages.db')

print("=================================================================")
print("          1. ANÁLISIS DE LA TABLA servicios_anuales_2026         ")
print("=================================================================")
df_anual = pd.read_sql_query("SELECT * FROM servicios_anuales_2026", conn)
print(f"Total general de registros anuales: {len(df_anual)}")

# Subtipo exacto
print("\n--- Subtipos en servicios_anuales_2026 ---")
print(df_anual['subtipo_servicio'].value_counts())

# Resumen de servicios donde dice 'traslado' explícitamente
print("\n--- Análisis de texto en 'resumen_servicio' y 'subtipo_servicio' ---")
con_traslado_positivo = df_anual[
    (df_anual['subtipo_servicio'] == 'Traslado Interhospitalario') |
    (df_anual['resumen_servicio'].str.contains('traslado', case=False, na=False) & 
     ~df_anual['resumen_servicio'].str.contains('sin requerimiento de traslado', case=False, na=False))
]
print(f"Total servicios con traslado positivo/efectuado en tabla anual: {len(con_traslado_positivo)}")
print(con_traslado_positivo['subtipo_servicio'].value_counts())
print("\nDesglose por mes de traslados confirmados:")
print(con_traslado_positivo.groupby(['mes_num', 'mes']).size())

print("\n--- Servicios donde se indica 'sin requerimiento de traslado / cancelado' ---")
sin_traslado = df_anual[df_anual['resumen_servicio'].str.contains('sin requerimiento de traslado', case=False, na=False)]
print(f"Total servicios sin requerimiento de traslado: {len(sin_traslado)}")
print(sin_traslado.groupby(['mes_num', 'mes']).size())


print("\n=================================================================")
print("      2. ANÁLISIS DETALLADO DE CASOS DE WHATSAPP (AGOSTO-SEPT)   ")
print("=================================================================")
# Ver los casos de agosto y septiembre agrupados
# Revisar cuántos casos de WhatsApp tuvieron traslado a hospital
# Palabras clave de traslado efectivo a hospital:
# 'traslad', 'hospital', 'regional', 'clínica 71', 'milan', 'torre médica', 'imss', 'issste', 'cruz roja'

messages_df = pd.read_sql_query("""
    SELECT id, remote_jid, push_name, text_content, datetime(message_timestamp, 'unixepoch', 'localtime') as fecha_hora, message_timestamp
    FROM messages 
    WHERE text_content IS NOT NULL AND text_content != ''
    ORDER BY message_timestamp ASC
""", conn)

# Buscar mensajes de traslados efectivos
kw_traslado = ['traslad', 'se traslada', 'fue trasladado', 'se realiza traslado', 'trasladando', 'traslado a', 'traslado al']
kw_hospital = ['hospital', 'clinica 71', 'clínica 71', 'imss', 'issste', 'regional', 'milan', 'milanés', 'boca del río', 'boca del rio', 'torre medica', 'torre médica', 'alta especialidad']

msg_traslados = messages_df[messages_df['text_content'].str.contains('|'.join(kw_traslado), case=False, na=False)]
print(f"Total mensajes individuales que mencionan traslado: {len(msg_traslados)}")

# Ver qué dicen esos mensajes
print("\nMuestra de 20 mensajes de traslado:")
for idx, r in msg_traslados.head(20).iterrows():
    txt_clean = r['text_content'].replace('\n', ' ')
    print(f"[{r['fecha_hora']}] {r['push_name']}: {txt_clean[:120]}")

conn.close()
