import sqlite3
import pandas as pd
from datetime import datetime

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%d-%m-%Y")
    except ValueError:
        return None

def analyze_by_date():
    print("========================================")
    print("  ANALIZADOR DE CONTINUIDAD - PCIVIL")
    print("========================================")
    
    start_str = input("\nIngresa la FECHA DE INICIO (Formato DD-MM-YYYY, ej. 01-08-2026): ")
    start_date = parse_date(start_str)
    
    end_str = input("Ingresa la FECHA FINAL (Formato DD-MM-YYYY, ej. 08-09-2026): ")
    end_date = parse_date(end_str)
    
    if not start_date or not end_date:
        print("Error: Formato de fecha incorrecto. Debe ser DD-MM-YYYY.")
        return
    
    # Ajustar para que tome hasta el final del día final
    end_date = end_date.replace(hour=23, minute=59, second=59)
    
    start_ts = int(start_date.timestamp())
    end_ts = int(end_date.timestamp())
    
    print(f"\nExtrayendo datos desde {start_date.strftime('%d-%m-%Y')} hasta {end_date.strftime('%d-%m-%Y')}...")
    
    conn = sqlite3.connect("whatsapp_messages.db")
    df = pd.read_sql_query(
        "SELECT * FROM messages WHERE message_timestamp BETWEEN ? AND ? ORDER BY message_timestamp ASC",
        conn,
        params=(start_ts, end_ts)
    )
    conn.close()
    
    if len(df) == 0:
        print("No se encontraron mensajes en ese rango de fechas.")
        return
        
    print(f"Se cargaron {len(df)} mensajes. Aplicando algoritmos de limpieza y continuidad...")
    
    # 1. Filtro de Basura
    df = df[df['text_content'].notna()]
    df['text_content'] = df['text_content'].str.strip()
    df = df[df['text_content'] != ""]
    
    stop_words = ['ok', 'gracias', 'enterado', 'saludos', 'hola', 'buenas tardes', 'buenos dias', 'buenas noches', 'si', 'no', 'qap', 'copiado', 'recibido']
    df['text_lower'] = df['text_content'].str.lower()
    df = df[~df['text_lower'].isin(stop_words)]
    
    # 2. Reconstrucción de la Continuidad
    df['date'] = pd.to_datetime(df['message_timestamp'], unit='s')
    
    msg_to_case = {}
    current_case_id = 0
    TIME_WINDOW_HOURS = 1.5 
    
    last_chat_time = {}
    chat_current_case = {}

    for idx, row in df.iterrows():
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
        
        df.at[idx, 'case_id'] = assigned_case

    df['case_id'] = df['case_id'].astype(int)
    
    # Eliminar casos de solo 1 o 2 mensajes
    case_counts = df['case_id'].value_counts()
    valid_cases = case_counts[case_counts > 2].index
    df_filtered = df[df['case_id'].isin(valid_cases)]
    
    df_final = df_filtered[['case_id', 'date', 'remote_jid', 'push_name', 'text_content', 'reply_to_id']].copy()
    df_final = df_final.sort_values(['case_id', 'date'])
    
    filename = f"reporte_casos_{start_date.strftime('%d%m%Y')}_a_{end_date.strftime('%d%m%Y')}.csv"
    try:
        df_final.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n¡ÉXITO! Reporte exportado a '{filename}'")
    except Exception as e:
        print("Error al exportar:", e)

    print(f" -> Incidentes continuos encontrados: {len(valid_cases)}")
    print("========================================")

if __name__ == "__main__":
    analyze_by_date()
