import sqlite3
import pandas as pd
from datetime import datetime
import re

# Localidades conocidas de Medellín de Bravo
LOCALIDADES = [
    'Puente Moreno', 'Lagos de Puente Moreno', 'El Tejar', 'Paso del Toro', 
    'Arboledas San Ramón', 'Arboledas', 'Los Robles', 'Robles', 'La Laguna', 
    'Playa de Vacas', 'San Miguel', 'Rancho del Padre', 'Medellín Centro', 
    'Ixcoalco', 'Pichones', 'La Joya', 'Paso del Cedro', 'El Cedral', 
    'Dos Bocas', 'Guasimal', 'Morro de Carrizal', 'Rincón de Pérez'
]

def detectar_localidad(texto):
    t_lower = texto.lower()
    for loc in LOCALIDADES:
        if loc.lower() in t_lower:
            return loc
    return 'Medellín de Bravo (Sector no especificado)'

def extraer_subtipo_y_resumen(categoria, texto, localidad):
    t = texto.lower()
    
    if categoria == 'Atención Médica / Prehospitalaria':
        if any(w in t for w in ['moto', 'derrap', 'motocicleta']):
            subtipo = 'Accidente de Moto / Derrape'
            resumen = f'Atención prehospitalaria y valoración por accidente/derrape en motocicleta en {localidad}.'
        elif any(w in t for w in ['arma blanca', 'machete', 'navaja', 'machetazo', 'picado']):
            subtipo = 'Herida por Arma Blanca'
            resumen = f'Atención de urgencia a persona lesionada con arma blanca en {localidad}.'
        elif any(w in t for w in ['arma de fuego', 'disparo', 'balazo', 'baleado']):
            subtipo = 'Herida por Arma de Fuego'
            resumen = f'Auxilio prehospitalario a persona herida por impacto de arma de fuego en {localidad}.'
        elif any(w in t for w in ['caída', 'caida', 'golpead', 'trauma', 'escalera']):
            subtipo = 'Persona Caída / Traumatismo'
            resumen = f'Valoración y estabilización de paciente tras sufrir caída/traumatismo en {localidad}.'
        elif any(w in t for w in ['parto', 'embarazada', 'alumbramiento', 'contracciones', 'labor']):
            subtipo = 'Atención Ginecológica / Parto'
            resumen = f'Asistencia médica y traslado de paciente en labor de parto/urgencia obstétrica en {localidad}.'
        elif any(w in t for w in ['choque', 'volcadura', 'atropellad', 'carro', 'vehículo']):
            subtipo = 'Accidente Vehicular / Atropellado'
            resumen = f'Atención médica a lesionado derivado de choque/atropellamiento vehicular en {localidad}.'
        elif any(w in t for w in ['sobredos', 'intoxicad', 'veneno', 'medicamento']):
            subtipo = 'Intoxicación / Sobredosis'
            resumen = f'Manejo prehospitalario de paciente por intoxicación/sobredosis de sustancias en {localidad}.'
        elif any(w in t for w in ['traslado', 'clínica', 'hospital', 'imss', 'issste', 'alta']):
            subtipo = 'Traslado Interhospitalario'
            resumen = f'Traslado médico especializado de paciente en ambulancia hacia centro hospitalario.'
        else:
            subtipo = 'Enfermedad General / Clínico'
            resumen = f'Valoración de signos vitales y atención médica a paciente por enfermedad general en {localidad}.'
            
    elif categoria == 'Accidente Vehicular':
        if any(w in t for w in ['moto', 'motocicleta']):
            subtipo = 'Accidente de Moto'
            resumen = f'Despliegue operativo por derrape o colisión de motocicleta en {localidad}.'
        elif any(w in t for w in ['atropellad']):
            subtipo = 'Persona Atropellada'
            resumen = f'Auxilio vial y atención a transeúnte atropellado en vialidad de {localidad}.'
        elif any(w in t for w in ['volcadura']):
            subtipo = 'Volcadura Vehicular'
            resumen = f'Aseguramiento perimetral y rescate vehicular por volcadura en {localidad}.'
        else:
            subtipo = 'Choque Vehicular'
            resumen = f'Atención y abanderamiento de choque vehicular entre automotores en {localidad}.'

    elif categoria == 'Incendio':
        if any(w in t for w in ['pastizal', 'maleza', 'lote', 'basura', 'terreno']):
            subtipo = 'Incendio de Pastizal / Terreno'
            resumen = f'Combate y sofocación de incendio de pastizal y maleza seca en {localidad}.'
        elif any(w in t for w in ['casa', 'vivienda', 'domicilio', 'habitación', 'edificio']):
            subtipo = 'Incendio en Casa Habitación'
            resumen = f'Control, extinción y remoción de escombros por conato/incendio en casa habitación en {localidad}.'
        elif any(w in t for w in ['gas', 'cilindro', 'tanque', 'fuga', 'olor a gas']):
            subtipo = 'Fuga de Gas L.P. / Cilindro'
            resumen = f'Inspección, mitigación y retiro preventivo de cilindro con fuga de gas L.P. en {localidad}.'
        elif any(w in t for w in ['cable', 'poste', 'corto', 'chispa', 'transformador']):
            subtipo = 'Corto Circuito / Cables de Luz'
            resumen = f'Aislamiento de zona y control de riesgo eléctrico por cables/corto circuito en {localidad}.'
        else:
            subtipo = 'Conato de Incendio / Bomberos'
            resumen = f'Intervención del cuerpo de bomberos por reporte de fuego activo en {localidad}.'

    elif categoria == 'Control de Fauna':
        if any(w in t for w in ['abeja', 'avispa', 'enjambre', 'panal', 'colmena']):
            subtipo = 'Abejas / Avispas (Enjambre)'
            resumen = f'Atención, evaluación y neutralización preventiva de enjambre de abejas/avispas en {localidad}.'
        elif any(w in t for w in ['serpiente', 'vibora', 'vboro', 'reptil', 'culebra']):
            subtipo = 'Serpientes y Reptiles'
            resumen = f'Captura y reubicación segura de ejemplar ofidio/reptil localizado en zona habitada de {localidad}.'
        elif any(w in t for w in ['vaca', 'toro', 'ganado', 'caballo', 'semoviente']):
            subtipo = 'Ganado / Semovientes en Vía Pública'
            resumen = f'Retiro de semovientes sueltos sobre cinta asfáltica para prevención de accidentes en {localidad}.'
        else:
            subtipo = 'Rescate de Fauna Silvestre'
            resumen = f'Captura y liberación de fauna silvestre o doméstica en situación de riesgo en {localidad}.'

    elif categoria == 'Rescate / Desastres Naturales':
        if any(w in t for w in ['árbol', 'arbol', 'rama', 'poda']):
            subtipo = 'Retiro de Árbol / Ramas Caídas'
            resumen = f'Seccionamiento y retiro de árbol/rama caída sobre vialidad o domicilio tras temporal en {localidad}.'
        elif any(w in t for w in ['inundac', 'anegac', 'encharca', 'agua', 'drenaje']):
            subtipo = 'Anegación / Inundación por Lluvia'
            resumen = f'Desazolve y apoyo en extracción de agua en vivienda/calle por precipitación pluvial en {localidad}.'
        elif any(w in t for w in ['río', 'rio', 'arroyo', 'ahogad', 'rescate']):
            subtipo = 'Rescate Acuático / Acompañamiento Río'
            resumen = f'Monitoreo de niveles de río/arroyo y maniobra de auxilio acuático preventivo en {localidad}.'
        elif any(w in t for w in ['lámina', 'lamina', 'techo', 'viento', 'destech']):
            subtipo = 'Afectación por Viento / Desprendimiento'
            resumen = f'Aseguramiento de estructuras y retiro de láminas desprendidas por fuertes vientos en {localidad}.'
        else:
            subtipo = 'Emergencia Climatológica'
            resumen = f'Evaluación de daños y apoyo a la población civil por fenómeno meteorológico en {localidad}.'

    elif categoria == 'Servicios / Mantenimiento':
        if any(w in t for w in ['agua', 'pipa', 'tinaco']):
            subtipo = 'Suministro de Agua Potable'
            resumen = f'Apoyo de abastecimiento de agua en pipa para servicio de la comunidad en {localidad}.'
        else:
            subtipo = 'Apoyo Comunitario / Infraestructura'
            resumen = f'Servicio de mantenimiento preventivo y apoyo a infraestructura urbana en {localidad}.'

    else:
        subtipo = 'Falsa Alarma / Sin Efecto'
        resumen = f'Verificación de reporte sin novedad o cancelado por la ciudadanía en {localidad}.'

    return subtipo, resumen

def categorizar_texto(texto):
    t = texto.lower()
    if any(w in t for w in ['paciente', 'paramdico', 'paramedico', 'hospital', 'respirar', 'presin', 'presion', 'ambulancia', 'signos vitales', 'mareada', 'sangre', 'traslado', 'inconsciente', 'lesionad', 'golpes', 'clnica', 'imss', 'issste', 'enferm', 'camilla', 'oxgeno', 'cataterismo', 'salud', 'medico', 'mdico', 'muerto', 'fallecido', 'occiso', 'suicidio', 'cuerpo', 'cadver', 'infarto', 'desmay', 'convulsi', 'parto']):
        return 'Atención Médica / Prehospitalaria'
    elif any(w in t for w in ['choque', 'accidente', 'derrap', 'moto', 'vehculo', 'carro', 'atropellad', 'volcadura', 'carambola', 'impacto', 'conductor', 'prensad', 'carretera', 'triler']):
        return 'Accidente Vehicular'
    elif any(w in t for w in ['fuego', 'incendio', 'quema', 'humo', 'pastizal', 'bomberos', 'conato', 'llamitas', 'apagar', 'tanque de gas', 'fuga de gas', 'corto circuito', 'cilindro', 'flama', 'derrame', 'combustible', 'gasolina', 'olor a gas']):
        return 'Incendio'
    elif any(w in t for w in ['vaca', 'perro', 'serpiente', 'enjambre', 'abejas', 'animal', 'avispa', 'panal', 'reptil', 'canino', 'felino', 'gato', 'toro', 'ganado', 'caballo', 'vboro', 'vibora', 'cocodrilo', 'lagarto', 'fauna', 'mono', 'tlacuache', 'zarigeya', 'mapache']):
        return 'Control de Fauna'
    elif any(w in t for w in ['inundacin', 'inundacion', 'deslave', 'derrumbe', 'rescate', 'atrapado', 'ahogado', 'ro', 'rio', 'arroyo', 'lluvia', 'huracn', 'huracan', 'viento', 'techo', 'lmina', 'lamina', 'socavn', 'terremoto', 'sismo']):
        return 'Rescate / Desastres Naturales'
    elif any(w in t for w in ['pintura', 'tope', 'agua', 'tinaco', 'limpieza', 'poda', 'rbol', 'arbol', 'alumbrado', 'alcantarilla', 'bache', 'obra', 'cable', 'poste', 'cables', 'cfs', 'luz', 'cfe', 'drenaje', 'fuga de agua']):
        return 'Servicios / Mantenimiento'
    elif any(w in t for w in ['falsa alarma', 'negativo', 'no hay nada', 'sin novedad', 'cancelado']):
        return 'Falsa Alarma'
    return 'Descartado'

def procesar_mensajes():
    conn = sqlite3.connect('whatsapp_messages.db')
    
    # Rango Agosto 4 a Septiembre 10
    start_ts = int(datetime(2026, 8, 4, 0, 0, 0).timestamp())
    end_ts = int(datetime(2026, 9, 10, 23, 59, 59).timestamp())
    
    df = pd.read_sql_query(
        'SELECT * FROM messages WHERE message_timestamp BETWEEN ? AND ? ORDER BY message_timestamp ASC',
        conn, params=(start_ts, end_ts)
    )
    
    # Filtro básico
    df = df[df['text_content'].notna()]
    df['text_content'] = df['text_content'].str.strip()
    df = df[df['text_content'] != '']
    
    stop_words = ['ok', 'gracias', 'enterado', 'saludos', 'hola', 'buenas tardes', 'buenos dias', 'buenas noches', 
                  'si', 'no', 'qap', 'copiado', 'recibido', 'entendido', 'voy para alla', 'sale', 'bien', 'va', 'okey']
    df = df[~df['text_content'].str.lower().isin(stop_words)]
    
    df['date'] = pd.to_datetime(df['message_timestamp'], unit='s')
    
    # Agrupación calibrada: 50 minutos (0.83 horas)
    # Evita fragmentar traslados largos a Veracruz/Boca pero separa emergencias distintas
    TIME_WINDOW_HOURS = 0.83
    msg_to_case = {}
    current_case_id = 0
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

    # Consolidar
    casos = []
    for case_id, group in df.groupby('case_id'):
        if len(group) < 2 and len(group.iloc[0]['text_content'].split()) < 4:
            continue
            
        full_text = " | ".join(group['text_content'].tolist())
        categoria = categorizar_texto(full_text)
        if categoria == 'Descartado':
            continue
            
        fecha_inicio = group['date'].min()
        mes_num = fecha_inicio.month
        mes_nombre = 'Agosto' if mes_num == 8 else ('Septiembre' if mes_num == 9 else 'Otro')
        
        localidad = detectar_localidad(full_text)
        subtipo, resumen = extraer_subtipo_y_resumen(categoria, full_text, localidad)
        
        efectividad = 'No Efectivo / Falsa Alarma' if categoria == 'Falsa Alarma' or 'cancelado' in full_text.lower() else 'Efectivo'
        
        casos.append({
            'mes': mes_nombre,
            'mes_num': mes_num,
            'fecha': fecha_inicio.strftime('%Y-%m-%d'),
            'hora': fecha_inicio.strftime('%H:%M:%S'),
            'categoria_macro': categoria,
            'subtipo_servicio': subtipo,
            'localidad': localidad,
            'efectividad': efectividad,
            'fuente_datos': 'WhatsApp Operativo',
            'resumen_servicio': resumen
        })

    df_casos = pd.DataFrame(casos)
    
    # Crear la tabla maestra en SQLite
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS servicios_anuales_2026')
    cursor.execute('''
        CREATE TABLE servicios_anuales_2026 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mes TEXT,
            mes_num INTEGER,
            fecha TEXT,
            hora TEXT,
            categoria_macro TEXT,
            subtipo_servicio TEXT,
            localidad TEXT,
            efectividad TEXT,
            fuente_datos TEXT,
            resumen_servicio TEXT
        )
    ''')
    
    for _, row in df_casos.iterrows():
        cursor.execute('''
            INSERT INTO servicios_anuales_2026 
            (mes, mes_num, fecha, hora, categoria_macro, subtipo_servicio, localidad, efectividad, fuente_datos, resumen_servicio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['mes'], row['mes_num'], row['fecha'], row['hora'],
            row['categoria_macro'], row['subtipo_servicio'], row['localidad'],
            row['efectividad'], row['fuente_datos'], row['resumen_servicio']
        ))
        
    conn.commit()
    conn.close()
    
    print("=== PROCESAMIENTO COMPLETADO ===")
    print(f"Total casos insertados: {len(df_casos)}")
    print("\nDesglose por Mes:")
    print(df_casos['mes'].value_counts())
    print("\nDesglose por Categoría Macro:")
    print(df_casos['categoria_macro'].value_counts())
    print("\nTop Subtipos:")
    print(df_casos['subtipo_servicio'].value_counts().head(8))

if __name__ == '__main__':
    procesar_mensajes()
