import sqlite3
import pandas as pd
import numpy as np

def build_analyzer():
    # Cargar datos
    conn = sqlite3.connect("whatsapp_messages.db")
    df = pd.read_sql_query("SELECT * FROM messages ORDER BY message_timestamp ASC", conn)
    conn.close()

    # 1. Filtro de Basura
    df = df[df['text_content'].notna()]
    df['text_content'] = df['text_content'].str.strip()
    df = df[df['text_content'] != ""]
    
    # Palabras sin valor por sí solas
    stop_words = ['ok', 'gracias', 'enterado', 'saludos', 'hola', 'buenas tardes', 'buenos dias', 'buenas noches', 'si', 'no', 'qap', 'copiado', 'recibido']
    df['text_lower'] = df['text_content'].str.lower()
    df = df[~df['text_lower'].isin(stop_words)]
    
    # 2. Reconstrucción de la Continuidad (Hilos y Casos)
    df['date'] = pd.to_datetime(df['message_timestamp'], unit='s')
    
    # Mapeo de IDs de mensajes para seguimiento de respuestas
    # dictionary de id_mensaje -> id_caso
    msg_to_case = {}
    cases_data = []
    
    current_case_id = 0
    TIME_WINDOW_HOURS = 1.5 # 1.5 horas de inactividad separan casos en el mismo grupo
    
    # Ordenar por tiempo para simular la llegada de mensajes
    df = df.sort_values('message_timestamp')
    
    # Guardar el último timestamp por chat
    last_chat_time = {}
    chat_current_case = {}

    for idx, row in df.iterrows():
        chat_id = row['remote_jid']
        msg_id = row['id']
        reply_id = row['reply_to_id']
        timestamp = row['message_timestamp']
        
        assigned_case = None
        
        # Regla 1: Es una respuesta a un mensaje anterior? (Seguimiento de un reporte que ya pasó)
        if pd.notna(reply_id) and reply_id in msg_to_case:
            assigned_case = msg_to_case[reply_id]
        
        # Regla 2: Continuidad temporal en el mismo chat
        if assigned_case is None:
            if chat_id in last_chat_time:
                time_diff = timestamp - last_chat_time[chat_id]
                if time_diff <= (TIME_WINDOW_HOURS * 3600):
                    assigned_case = chat_current_case[chat_id]
                else:
                    # Nuevo caso por tiempo expirado
                    current_case_id += 1
                    assigned_case = current_case_id
            else:
                # Primer caso en este chat
                current_case_id += 1
                assigned_case = current_case_id
                
        # Guardar asignación
        msg_to_case[msg_id] = assigned_case
        last_chat_time[chat_id] = timestamp
        chat_current_case[chat_id] = assigned_case
        
        df.at[idx, 'case_id'] = assigned_case

    # 3. Guardar resultados para análisis
    df['case_id'] = df['case_id'].astype(int)
    
    # Eliminar casos que tengan solo 1 o 2 mensajes y sean muy cortos
    case_counts = df['case_id'].value_counts()
    valid_cases = case_counts[case_counts > 2].index
    df_filtered = df[df['case_id'].isin(valid_cases)]
    
    # Preparar el dataframe final ordenado por caso y luego por tiempo
    df_final = df_filtered[['case_id', 'date', 'remote_jid', 'push_name', 'text_content', 'reply_to_id']].copy()
    df_final = df_final.sort_values(['case_id', 'date'])
    
    # Exportar a Excel y CSV
    try:
        df_final.to_csv('reporte_casos_continuidad.csv', index=False, encoding='utf-8-sig')
        print("Reporte exportado exitosamente a 'reporte_casos_continuidad.csv'")
    except Exception as e:
        print("Error al exportar:", e)

    # Mostrar métricas al usuario
    print(f"\n--- RESUMEN DEL ANALIZADOR ---")
    print(f"Mensajes totales procesados: {len(df)}")
    print(f"Incidentes (Casos) con seguimiento detectados (>2 mensajes): {len(valid_cases)}")
    print("\nEjemplo de continuidad de un caso:")
    
    # Mostrar el primer caso válido con más de 5 mensajes
    for case in valid_cases:
        case_msgs = df_final[df_final['case_id'] == case]
        if len(case_msgs) > 5:
            print(f"\nCaso #{case} (Chat: {case_msgs['remote_jid'].iloc[0]})")
            for _, msg in case_msgs.head(8).iterrows():
                reply_indicator = " -> [Respuesta a reporte]" if pd.notna(msg['reply_to_id']) else ""
                print(f"  [{msg['date']}] {msg['push_name']}{reply_indicator}: {msg['text_content'][:100]}")
            break

if __name__ == "__main__":
    build_analyzer()
