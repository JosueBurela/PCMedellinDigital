import sqlite3
import pandas as pd
from datetime import datetime
import re

def categorizar_caso(texto):
    texto_original = texto
    texto = texto.lower()
    
    # 1. Atencin Mdica / Prehospitalaria
    if any(word in texto for word in ['paciente', 'paramdico', 'paramedico', 'hospital', 'respirar', 'presin', 'presion', 'ambulancia', 'signos vitales', 'mareada', 'sangre', 'traslado', 'inconsciente', 'lesionad', 'golpes', 'clnica', 'imss', 'issste', 'enferm', 'camilla', 'oxgeno', 'cataterismo', 'salud', 'medico', 'mdico', 'muerto', 'fallecido', 'occiso', 'suicidio', 'cuerpo', 'cadver', 'infarto', 'desmay', 'convulsi']):
        return 'Atencin Mdica / Prehospitalaria'
        
    # 2. Accidente Vehicular
    elif any(word in texto for word in ['choque', 'accidente', 'derrap', 'moto', 'vehculo', 'carro', 'atropellad', 'volcadura', 'carambola', 'impacto', 'conductor', 'prensad', 'carretera', 'triler']):
        return 'Accidente Vehicular'
        
    # 3. Incendio / Materiales Peligrosos
    elif any(word in texto for word in ['fuego', 'incendio', 'quema', 'humo', 'pastizal', 'bomberos', 'conato', 'llamitas', 'apagar', 'tanque de gas', 'fuga de gas', 'corto circuito', 'cilindro', 'flama', 'derrame', 'combustible', 'gasolina', 'olor a gas']):
        return 'Incendio'
        
    # 4. Control de Fauna
    elif any(word in texto for word in ['vaca', 'perro', 'serpiente', 'enjambre', 'abejas', 'animal', 'avispa', 'panal', 'reptil', 'canino', 'felino', 'gato', 'toro', 'ganado', 'caballo', 'vboro', 'vibora', 'cocodrilo', 'lagarto', 'fauna', 'mono', 'tlacuache', 'zarigeya', 'mapache']):
        return 'Control de Fauna'
        
    # 5. Rescate / Desastres Naturales
    elif any(word in texto for word in ['inundacin', 'deslave', 'derrumbe', 'rescate', 'atrapado', 'ahogado', 'ro', 'arroyo', 'lluvia', 'huracn', 'viento', 'techo', 'lmina', 'socavn', 'terremoto', 'sismo']):
        return 'Rescate / Desastres Naturales'
        
    # 6. Servicios / Mantenimiento (Infraestructura)
    elif any(word in texto for word in ['pintura', 'tope', 'agua', 'tinaco', 'limpieza', 'poda', 'rbol', 'alumbrado', 'alcantarilla', 'bache', 'obra', 'cable', 'poste', 'cables', 'cfs', 'luz', 'cfe', 'drenaje', 'fuga de agua']):
        return 'Servicios / Mantenimiento'
        
    # 7. Administrativo / Interno (PC)
    elif any(word in texto for word in ['uniforme', 'guardia', 'homenaje', 'novedad', 'bitcora', 'fatiga', 'ley', 'reglamento', 'obligaciones', 'relevo', 'bandera', 'oficio', 'reunin']):
        return 'Administrativo / Interno'
        
    # 8. Falsa Alarma
    elif any(word in texto for word in ['falsa alarma', 'negativo', 'no hay nada', 'sin novedad', 'cancelado']):
        return 'Falsa Alarma'
        
    # 8. Filtro Final de texto corto/basura
    palabras = texto.split()
    if len(palabras) < 6:
        return 'Basura / Descartado'
        
    return 'General / Otros'

def limpiar_texto(texto):
    # Eliminar dobles espacios y caracteres extraos
    texto = re.sub(r'\s+', ' ', str(texto))
    return texto.strip()

def generar_reporte_agosto():
    print("Iniciando limpieza y agrupacin de casos para AGOSTO...")
    
    # Fechas de Agosto (Timestamp)
    start_dt = datetime(2026, 8, 4, 0, 0, 0)
    end_dt = datetime(2026, 8, 31, 23, 59, 59)
    start_ts = int(start_dt.timestamp())
    end_ts = int(end_dt.timestamp())
    
    conn = sqlite3.connect("whatsapp_messages.db")
    df = pd.read_sql_query(
        "SELECT * FROM messages WHERE message_timestamp BETWEEN ? AND ? ORDER BY message_timestamp ASC",
        conn, params=(start_ts, end_ts)
    )
    conn.close()

    # 1. Filtro estricto de Basura
    df = df[df['text_content'].notna()]
    df['text_content'] = df['text_content'].apply(limpiar_texto)
    df = df[df['text_content'] != ""]
    
    # Lista ampliada de palabras basura que no aportan a un reporte si van solas
    stop_words = ['ok', 'gracias', 'enterado', 'saludos', 'hola', 'buenas tardes', 'buenos dias', 'buenas noches', 
                  'si', 'no', 'qap', 'copiado', 'recibido', 'entendido', 'voy para alla', 'sale', 'bien', 'va', 'okey']
    
    df['text_lower'] = df['text_content'].str.lower()
    df = df[~df['text_lower'].isin(stop_words)]
    
    # 2. Agrupacin por Hilos / Continuidad
    df['date'] = pd.to_datetime(df['message_timestamp'], unit='s')
    
    msg_to_case = {}
    current_case_id = 0
    TIME_WINDOW_HOURS = 0.33  # Reducido a 20 mins para no mezclar serpientes con ambulancias
    
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

    # 3. Consolidar la informacin: 1 Fila = 1 Caso (Incidente Completo)
    casos_consolidados = []
    
    agrupado = df.groupby('case_id')
    for case_id, group in agrupado:
        # Filtrar casos que solo tienen 1 mensaje corto (posible basura residual)
        if len(group) < 2:
            texto_unico = group.iloc[0]['text_content']
            if len(texto_unico.split()) < 4:
                continue # Omitir casos de una sola palabra/frase corta
                
        # Unir toda la conversacin del caso
        conversacion_completa = " | ".join(group['text_content'].tolist())
        
        # Categorizar basado en el texto completo
        categoria = categorizar_caso(conversacion_completa)
        
        fecha_inicio = group['date'].min()
        fecha_fin = group['date'].max()
        duracion_minutos = round((fecha_fin - fecha_inicio).total_seconds() / 60, 1)
        
        casos_consolidados.append({
            'ID_Caso': int(case_id),
            'Fecha_Reporte': fecha_inicio.strftime('%Y-%m-%d'),
            'Hora_Inicio': fecha_inicio.strftime('%H:%M:%S'),
            'Hora_Fin': fecha_fin.strftime('%H:%M:%S'),
            'Duracion_Minutos': duracion_minutos,
            'Total_Mensajes': len(group),
            'Categoria': categoria,
            'Grupo_Origen': group.iloc[0]['remote_jid'],
            'Transcripcion_Incidente': conversacion_completa
        })
        
    df_casos = pd.DataFrame(casos_consolidados)
    
    # Filtrar descartados y platicas generales
    df_casos = df_casos[~df_casos['Categoria'].isin(['Basura / Descartado', 'General / Otros'])]
    
    # Guardar en CSV limpio
    archivo_salida = 'reporte_mensual_agosto_limpio.csv'
    df_casos.to_csv(archivo_salida, index=False, encoding='utf-8-sig')
    
    print("\n==================================================")
    print("      REPORTE DE AGOSTO GENERADO CON XITO")
    print("==================================================")
    print(f"Total de mensajes brutos en el mes: {len(df)}")
    print(f"Total de incidentes/salidas reales identificadas: {len(df_casos)}")
    print("\nDesglose por categoras:")
    print(df_casos['Categoria'].value_counts().to_string())
    print(f"\nArchivo guardado como: {archivo_salida}")
    print("==================================================")

if __name__ == "__main__":
    generar_reporte_agosto()
