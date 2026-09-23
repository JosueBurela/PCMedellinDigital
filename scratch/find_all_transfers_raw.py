import sqlite3
import pandas as pd
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('whatsapp_messages.db')

# 1. Mensajes que contienen el formato estructurado FRAP (*NOMBRE DEL PACIENTE*, etc.)
query_frap = """
SELECT id, remote_jid, push_name, text_content, 
       datetime(message_timestamp, 'unixepoch', 'localtime') as dt_local,
       message_timestamp
FROM messages
WHERE text_content LIKE '%NOMBRE DEL PACIENTE%' 
   OR text_content LIKE '%HOSPITAL DE TRASLADO%'
   OR text_content LIKE '%traslado%'
   OR text_content LIKE '%traslada%'
ORDER BY message_timestamp ASC
"""
df_raw = pd.read_sql_query(query_frap, conn)
print(f"Total mensajes candidatos: {len(df_raw)}")

# Analizar cuántos tienen formato FRAP
frap_msgs = df_raw[df_raw['text_content'].str.contains(r'NOMBRE DEL PACIENTE|HOSPITAL DE TRASLADO', case=False, na=False)]
print(f"Total mensajes con formato FRAP estructurado: {len(frap_msgs)}")

# Analizar mensajes de novedades diarias (que resumen los servicios y traslados de la guardia)
nov_msgs = df_raw[df_raw['text_content'].str.contains(r'novedades del d[ií]a|guardia \(', case=False, na=False)]
print(f"Total mensajes de novedades de guardia: {len(nov_msgs)}")

# Ver qué otros mensajes mencionan traslado con nombre o persona
conn.close()
