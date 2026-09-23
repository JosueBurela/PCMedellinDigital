import sqlite3
import pandas as pd

conn = sqlite3.connect('whatsapp_messages.db')

print("=== MENSAJES DE WHATSAPP CON 'TRASLADO' ===")
query = """
SELECT id, push_name, text_content, datetime(message_timestamp, 'unixepoch', 'localtime') as dt
FROM messages 
WHERE text_content LIKE '%traslado%' OR text_content LIKE '%traslad%'
ORDER BY message_timestamp ASC
"""
df_tr = pd.read_sql_query(query, conn)
print(f"Total mensajes que mencionan traslado/traslad: {len(df_tr)}")
print("\nPrimeros 25 mensajes:")
for idx, r in df_tr.head(25).iterrows():
    print(f"[{r['dt']}] {r['push_name']}: {r['text_content'][:100]}")

print("\n=== SERVICIOS ANUALES CON SUBTIPO 'Traslado Interhospitalario' ===")
df_sub_tr = pd.read_sql_query("SELECT * FROM servicios_anuales_2026 WHERE subtipo_servicio = 'Traslado Interhospitalario'", conn)
print(f"Total: {len(df_sub_tr)}")
print(df_sub_tr[['mes', 'fecha', 'hora', 'localidad', 'resumen_servicio']].head(15))

print("\n=== REPORTE DE CASOS CONTINUIDAD CSV ===")
try:
    df_cont = pd.read_csv('reporte_casos_continuidad.csv')
    print("Columnas continuidad:", df_cont.columns.tolist())
    print("Total filas:", len(df_cont))
    if 'subtipo' in df_cont.columns:
        print(df_cont['subtipo'].value_counts())
    # buscar traslados
    mask = df_cont.apply(lambda row: row.astype(str).str.contains('traslad', case=False).any(), axis=1)
    print("Filas con 'traslad':", mask.sum())
except Exception as e:
    print("Error continuidad:", e)

conn.close()
