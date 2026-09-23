import sqlite3
import pandas as pd
import numpy as np

def analyze_messages():
    # Load data from SQLite
    conn = sqlite3.connect("whatsapp_messages.db")
    df = pd.read_sql_query("SELECT * FROM messages ORDER BY message_timestamp ASC", conn)
    conn.close()

    print(f"Total de mensajes cargados: {len(df)}")

    # 1. Limpieza de datos básica
    # Eliminar mensajes sin texto útil
    df = df[df['text_content'].notna()]
    df['text_content'] = df['text_content'].str.strip()
    
    # Filtrar mensajes vacíos o muy cortos que suelen ser 'basura'
    basura_words = ['ok', 'gracias', 'enterado', 'saludos', 'hola', 'buenas tardes', 'buenos dias', 'buenas noches', 'si', 'no']
    df_clean = df[~df['text_content'].str.lower().isin(basura_words)]
    
    print(f"Mensajes después de filtrar basura simple: {len(df_clean)}")

    # 2. Reconstrucción de hilos (Continuidad del caso)
    # Convertir timestamp a fecha legible
    df_clean.loc[:, 'date'] = pd.to_datetime(df_clean['message_timestamp'], unit='s')
    
    # Agrupar por 'remote_jid' (número o grupo)
    cases = []
    
    # Vamos a usar una ventana de tiempo de 2 horas para considerar que es el mismo incidente
    TIME_WINDOW_HOURS = 2
    
    for jid, group in df_clean.groupby('remote_jid'):
        group = group.sort_values('message_timestamp')
        
        # Calcular diferencia de tiempo con el mensaje anterior en el mismo chat
        group['time_diff'] = group['message_timestamp'].diff()
        
        # Un nuevo caso empieza si es el primer mensaje o si han pasado más de TIME_WINDOW_HOURS horas
        # o si es explícitamente una respuesta a un caso anterior (reply_to_id)
        
        case_id = 0
        case_ids = []
        
        for index, row in group.iterrows():
            if pd.isna(row['time_diff']) or row['time_diff'] > (TIME_WINDOW_HOURS * 3600):
                # Nuevo caso a menos que sea un reply
                if pd.notna(row['reply_to_id']):
                    # Buscar a qué caso pertenece el mensaje al que responde
                    # Si no lo encontramos rápido, lo agregamos al último
                    pass # Simplificación: si es reply, idealmente busca el case_id del reply_to_id
                else:
                    case_id += 1
            case_ids.append(f"{jid}_{case_id}")
            
        group['case_id'] = case_ids
        cases.append(group)
        
    if cases:
        df_cases = pd.concat(cases)
        
        print("\nEjemplo de casos identificados:")
        # Mostrar los primeros casos agrupados
        case_counts = df_cases['case_id'].value_counts()
        print(f"Total de casos (incidentes) distintos detectados: {len(case_counts)}")
        
        # Mostrar el caso con más mensajes
        top_case = case_counts.index[0]
        print(f"\nCaso con más mensajes ({top_case}):")
        top_case_msgs = df_cases[df_cases['case_id'] == top_case][['date', 'push_name', 'text_content', 'reply_to_id']]
        for _, msg in top_case_msgs.head(10).iterrows():
            reply_mark = " (Respuesta)" if pd.notna(msg['reply_to_id']) else ""
            print(f"[{msg['date']}] {msg['push_name']}{reply_mark}: {msg['text_content'][:100]}...")
            
    else:
        print("No se encontraron casos.")
        
if __name__ == "__main__":
    analyze_messages()
