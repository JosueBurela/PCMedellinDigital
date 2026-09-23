import openpyxl
import pandas as pd
import sqlite3

print("=== 1. Registro_Anual_Operativo_2026_PC_Medellin.xlsx ===")
wb_anual = openpyxl.load_workbook('Documentacion/Registro_Anual_Operativo_2026_PC_Medellin.xlsx', data_only=True)
print("Hojas:", wb_anual.sheetnames)
for s in wb_anual.sheetnames:
    ws = wb_anual[s]
    print(f"Hoja {s}: {ws.max_row} filas, {ws.max_column} cols")

print("\n=== 2. SERVICIOS ANUALES 2026 EN DB ===")
conn = sqlite3.connect('whatsapp_messages.db')
df = pd.read_sql_query("SELECT * FROM servicios_anuales_2026", conn)
print("Total servicios anuales:", len(df))
print(df['categoria_macro'].value_counts())
print("\nSubtipos:")
print(df['subtipo_servicio'].value_counts())

print("\nEfectividad:")
print(df['efectividad'].value_counts())

print("\nFuente datos:")
print(df['fuente_datos'].value_counts())

print("\nMeses y totales:")
print(df.groupby(['mes_num', 'mes']).size())

print("\nBúsqueda de 'traslado' en subtipo o resumen:")
sub_traslados = df[df['subtipo_servicio'].str.contains('traslado', case=False, na=False)]
print("Subtipo Traslado Interhospitalario:", len(sub_traslados))

# Revisemos casos donde hubo traslado vs donde se atendió en sitio
# ¿Qué dice el texto del resumen?
print("\nTipos de resumen en df:")
print(df['resumen_servicio'].value_counts().head(20))

conn.close()
