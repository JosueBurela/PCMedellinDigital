import sqlite3
import pandas as pd
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('whatsapp_messages.db')
c = conn.cursor()

# Ver todos los mensajes que indican una salida, traslado o arribo a hospital
query = """
SELECT id, datetime(message_timestamp, 'unixepoch', 'localtime') as dt, push_name, text_content
FROM messages
WHERE (text_content LIKE '%traslad%' 
   OR text_content LIKE '%hospital%' 
   OR text_content LIKE '%clinica%' 
   OR text_content LIKE '%clínica%' 
   OR text_content LIKE '%imss%' 
   OR text_content LIKE '%issste%'
   OR text_content LIKE '%boca del r%')
ORDER BY message_timestamp ASC
"""
df_all_tr = pd.read_sql_query(query, conn)
print(f"Total mensajes recuperados: {len(df_all_tr)}")

# Analizar eventos distintos
# Agrupar mensajes cercanos en el tiempo por chat para identificar incidentes de traslado completos
eventos_traslado = []

# Filtrar mensajes que son meramente informativos o repetidos
ignorar = ['no amerita traslado', 'no ameritó traslado', 'sin traslado', 'se niega al traslado', 'niega traslado', 'desistimiento']

for idx, r in df_all_tr.iterrows():
    t = str(r['text_content'])
    t_low = t.lower()
    
    # Si contiene negativa, ignorar a menos que diga que luego sí se trasladó
    if any(w in t_low for w in ignorar) and not any(w in t_low for w in ['inicia traslado', 'se traslada a', 'fue trasladado']):
        continue
        
    # Checar si es una acción de traslado
    es_accion = False
    if any(w in t_low for w in ['sale u', 'sale unidad', 'inicia traslado', 'comienza traslado', 'se traslada', 'fue trasladado', 'traslada a', 'traslado de', 'traslado al', 'traslado a', 'en general de boca', 'en clínica 71', 'en clínica 61', 'en imss', 'en espera de equipo', 'entregando paciente', 'retorna de traslado']):
        es_accion = True
    elif 'nombre del paciente' in t_low or 'hospital de traslado' in t_low:
        es_accion = True
        
    if es_accion:
        eventos_traslado.append({
            'id': r['id'],
            'dt': r['dt'],
            'remitente': r['push_name'],
            'texto': t.replace('\n', ' ')[:140]
        })

df_ev = pd.DataFrame(eventos_traslado)
print(f"Total mensajes de acción de traslado / hospital: {len(df_ev)}")

print("\nMuestra de 25 mensajes de acción de traslado:")
for i, r in df_ev.head(25).iterrows():
    print(f"[{r['dt']}] ({r['remitente']}): {r['texto']}")

conn.close()
