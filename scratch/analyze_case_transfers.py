import sqlite3
import pandas as pd
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('whatsapp_messages.db')

# 1. Analizar los casos de Agosto-Septiembre reconstruidos desde messages
# Emulando la lógica de agrupación de procesar_anual_db.py para ver el texto completo de cada caso
start_ts = int(pd.Timestamp('2026-08-04 00:00:00').timestamp())
end_ts = int(pd.Timestamp('2026-09-10 23:59:59').timestamp())

df_msg = pd.read_sql_query(
    'SELECT * FROM messages WHERE message_timestamp BETWEEN ? AND ? ORDER BY message_timestamp ASC',
    conn, params=(start_ts, end_ts)
)

# Filtro básico
df_msg = df_msg[df_msg['text_content'].notna()]
df_msg['text_content'] = df_msg['text_content'].str.strip()
df_msg = df_msg[df_msg['text_content'] != '']
stop_words = ['ok', 'gracias', 'enterado', 'saludos', 'hola', 'buenas tardes', 'buenos dias', 'buenas noches', 
              'si', 'no', 'qap', 'copiado', 'recibido', 'entendido', 'voy para alla', 'sale', 'bien', 'va', 'okey']
df_msg = df_msg[~df_msg['text_content'].str.lower().isin(stop_words)]

TIME_WINDOW_HOURS = 0.83
msg_to_case = {}
current_case_id = 0
last_chat_time = {}
chat_current_case = {}

for idx, row in df_msg.iterrows():
    chat_id = row['remote_jid']
    msg_id = row['id']
    reply_id = row['reply_to_id']
    timestamp = row['message_timestamp']
    
    assigned_case = None
    if pd.notna(reply_id) and reply_id in msg_to_case:
        assigned_case = msg_to_case[reply_id]
    
    if assigned_case is None:
        if chat_id in last_chat_time:
            time_diff = timestamp - last_chat_time[chat_id]
            if time_diff <= (TIME_WINDOW_HOURS * 3600):
                assigned_case = chat_current_case[chat_id]
            else:
                current_case_id += 1
                assigned_case = current_case_id
        else:
            current_case_id += 1
            assigned_case = current_case_id
            
    msg_to_case[msg_id] = assigned_case
    last_chat_time[chat_id] = timestamp
    chat_current_case[chat_id] = assigned_case
    df_msg.at[idx, 'case_id'] = assigned_case

casos_analisis = []
for case_id, group in df_msg.groupby('case_id'):
    if len(group) < 2 and len(group.iloc[0]['text_content'].split()) < 4:
        continue
    full_text = " | ".join(group['text_content'].tolist())
    t_low = full_text.lower()
    
    # Evaluar si hubo traslado
    # Indicadores positivos de traslado:
    tiene_traslado_positivo = bool(re.search(r'(traslad[aoó]|se traslada|fue trasladado|trasladando|traslado a|traslado al|arriba a|ingresa a|se canaliza a)\s*(al?|la|el)?\s*(hospital|cl[ií]nica|imss|issste|regional|milan|torre|cruz roja|hgbv)?', t_low))
    # Indicadores negativos explícitos:
    no_traslado = bool(re.search(r'(no requiere traslado|sin traslado|no amerita traslado|no fue necesario traslado|se niega al traslado|firma desistimiento|firma de desistimiento|no quiso traslado)', t_low))
    
    # Clasificación de traslado en el caso:
    status_traslado = "Sin mención"
    if no_traslado:
        status_traslado = "No requirió / Rechazó traslado"
    elif tiene_traslado_positivo or 'traslado' in t_low or 'hospital' in t_low or 'imss' in t_low:
        status_traslado = "Traslado Efectuado / Vinculado a Hospital"
        
    casos_analisis.append({
        'case_id': case_id,
        'fecha': group['message_timestamp'].min(),
        'mensajes': len(group),
        'status_traslado': status_traslado,
        'full_text': full_text[:200]
    })

df_ca = pd.DataFrame(casos_analisis)
print(f"Total casos reconstruidos Agosto-Septiembre: {len(df_ca)}")
print("\nDistribución de estado de traslado en los casos de WhatsApp:")
print(df_ca['status_traslado'].value_counts())

conn.close()
