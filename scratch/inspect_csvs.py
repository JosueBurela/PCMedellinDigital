import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

df_agosto = pd.read_csv('reporte_mensual_agosto_limpio.csv')
print("=== reporte_mensual_agosto_limpio.csv ===")
print("Dimensiones:", df_agosto.shape)
print("Columnas:", df_agosto.columns.tolist())

# Buscar en Transcripcion_Incidente los formatos FRAP y menciones de traslado
frap_cases = []
for idx, r in df_agosto.iterrows():
    t = str(r['Transcripcion_Incidente'])
    if 'NOMBRE DEL PACIENTE' in t or 'HOSPITAL DE TRASLADO' in t or 'traslad' in t.lower():
        frap_cases.append(r)

print(f"Total casos con FRAP o traslado en transcripción: {len(frap_cases)}")

df_cont = pd.read_csv('reporte_casos_continuidad.csv')
print("\n=== reporte_casos_continuidad.csv ===")
print("Dimensiones:", df_cont.shape)
print("Columnas:", df_cont.columns.tolist())
