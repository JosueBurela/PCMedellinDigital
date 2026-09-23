import psycopg2
import re
import os
import sqlite3
import json
from datetime import datetime, timedelta

# Conexión a Postgres de Evolution API
pg_conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
pg_cur = pg_conn.cursor()

GROUP_JID = '120363042493725288@g.us'

# Crear base de datos SQLite estructurada para Casos Documentados
DB_FILE = 'bitacora_casos_pc.db'
if os.path.exists(DB_FILE):
    try:
        os.remove(DB_FILE)
    except:
        pass

sql_conn = sqlite3.connect(DB_FILE)
sql_cur = sql_conn.cursor()

sql_cur.execute('''
CREATE TABLE IF NOT EXISTS casos (
    id_caso TEXT PRIMARY KEY,
    unidad TEXT,
    tipo_caso TEXT,
    fecha_inicio TIMESTAMP,
    fecha_fin TIMESTAMP,
    duracion_minutos INTEGER,
    paciente_nombre TEXT,
    paciente_edad TEXT,
    direccion TEXT,
    diagnostico TEXT,
    hospital_destino TEXT,
    medico_recibe TEXT,
    codigo_triage TEXT,
    operador TEXT,
    paramedico TEXT,
    tercero_abordo TEXT,
    foto_salida_id TEXT,
    foto_retorno_id TEXT,
    total_fotos INTEGER DEFAULT 0,
    total_mensajes INTEGER DEFAULT 0
)
''')

sql_cur.execute('''
CREATE TABLE IF NOT EXISTS caso_mensajes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_caso TEXT,
    wa_id TEXT,
    fecha_hora TIMESTAMP,
    remitente TEXT,
    tipo_mensaje TEXT,
    texto TEXT,
    es_foto INTEGER,
    foto_local_path TEXT,
    rol_mensaje TEXT,
    FOREIGN KEY(id_caso) REFERENCES casos(id_caso)
)
''')
sql_conn.commit()

# Cargar todos los mensajes del grupo
print("Cargando mensajes desde PostgreSQL...")
pg_cur.execute('''
    SELECT 
        "id",
        to_timestamp("messageTimestamp") as fecha_msg,
        "pushName",
        "messageType",
        COALESCE(
            "message"->>'conversation',
            "message"->'extendedTextMessage'->>'text',
            "message"->'imageMessage'->>'caption',
            "message"->'videoMessage'->>'caption',
            ''
        ) as texto,
        "message"->'imageMessage' IS NOT NULL as tiene_imagen,
        "key"->>'id' as wa_id,
        "key",
        "message"
    FROM "Message"
    WHERE "key"->>'remoteJid' = %s
    ORDER BY "messageTimestamp" ASC
''', (GROUP_JID,))

mensajes = pg_cur.fetchall()
print(f"Total mensajes cargados: {len(mensajes)}")

# Identificar partes médicos
def parsear_parte_medico(texto):
    t_lower = texto.lower()
    if not (('nombre del paciente' in t_lower or 'paciente' in t_lower) and ('diagnostico' in t_lower or 'diagnóstico' in t_lower or 'hospital' in t_lower or 'edad' in t_lower)):
        if not ('*ambulancia*' in t_lower and '*fecha*' in t_lower):
            return None
            
    def extraer(patrones):
        for p in patrones:
            m = re.search(p, texto, re.IGNORECASE | re.MULTILINE)
            if m:
                v = re.sub(r'^\*+|\*+$', '', m.group(1)).strip()
                if v: return v
        return ""

    paciente = extraer([r'\*?NOMBRE\s*DEL\s*PACIENTE\*?\s*:\s*([^\n\r\*]+)'])
    edad = extraer([r'\*?EDAD\*?\s*:\s*([^\n\r\*]+)'])
    ambulancia = extraer([r'\*?AMBULANCIA\*?\s*:\s*([^\n\r\*]+)', r'\*?UNIDAD\*?\s*:\s*([^\n\r\*]+)'])
    operador = extraer([r'\*?OPERADOR\*?\s*:\s*([^\n\r\*]+)'])
    paramedico = extraer([r'\*?PARAMEDICO\*?\s*:\s*([^\n\r\*]+)', r'\*?PARAMÉDICO\*?\s*:\s*([^\n\r\*]+)'])
    tercero = extraer([r'\*?TERCERO\s*ABORDO\*?\s*:\s*([^\n\r\*]+)'])
    direccion = extraer([r'\*?DIRECCI[OÓ]N\s*DEL\s*SERVICIO\*?\s*:\s*([^\n\r\*]+)', r'DIRECCI[OÓ]N\s*:\s*([^\n\r]+)'])
    diagnostico = extraer([r'\*?DIAGN[OÓ]STICO\*?\s*:\s*([^\n\r\*]+)'])
    hospital = extraer([r'\*?HOSPITAL\s*DE\s*TRASLADO\*?\s*:\s*([^\n\r\*]+)', r'HOSPITAL\s*:\s*([^\n\r]+)'])
    recibe = extraer([r'\*?RECIBE\*?\s*:\s*([^\n\r\*]+)'])
    codigo = extraer([r'\*?C[OÓ]DIGO\*?\s*:\s*([^\n\r\*]+)'])
    
    h_lower = hospital.lower()
    t_full = texto.lower()
    if 'se niega' in h_lower or 'niega traslado' in t_full or 'se niega' in t_full:
        tipo = "NEGATIVA_DE_TRASLADO"
    elif 'no ameritó' in h_lower or 'no amerito' in h_lower or 'no ameritó traslado' in t_full:
        tipo = "ATENCION_NO_AMERITA_TRASLADO"
    elif any(k in h_lower for k in ['hospital', 'imss', 'issste', 'regional', 'faustino', 'tarimoya', '20 de noviembre', 'criver', 'materno', 'boca del río']) or (hospital and hospital.lower() not in ['n/a', 'na', 'ninguno', 'no']):
        tipo = "TRASLADO_EFECTIVO_HOSPITAL"
    else:
        tipo = "ATENCION_EN_SITIO"

    return {
        'paciente': paciente,
        'edad': edad,
        'ambulancia': ambulancia,
        'operador': operador,
        'paramedico': paramedico,
        'tercero': tercero,
        'direccion': direccion,
        'diagnostico': diagnostico,
        'hospital': hospital,
        'recibe': recibe,
        'codigo': codigo,
        'tipo': tipo
    }

# Normalizar unidad
def normalizar_unidad(txt):
    if not txt: return "SIN_UNIDAD"
    m = re.search(r'(097|098|208|096|047|072|073|041)', txt)
    if m:
        return f"U-{m.group(1)}"
    return txt.strip().upper()[:15]

# Detectar eventos clave
partes = []
for idx, m in enumerate(mensajes):
    mid, f, push, mtype, txt, tiene_img, wa_id, k, msg = m
    parte_info = parsear_parte_medico(txt)
    if parte_info:
        partes.append((idx, m, parte_info))

print(f"Total partes médicos detectados: {len(partes)}")

# Para cada parte médico, armar el caso correlacionando mensajes anteriores y posteriores
casos_creados = 0
for idx_p, m_p, p_info in partes:
    f_p = m_p[1] # fecha_msg
    unidad_norm = normalizar_unidad(p_info['ambulancia'])
    
    # Buscar salida hasta 2 horas antes
    ventana_inicio = f_p - timedelta(hours=2)
    ventana_fin = f_p + timedelta(hours=1, minutes=30)
    
    # Recorrer mensajes en la ventana
    mensajes_caso = []
    foto_salida_id = None
    foto_retorno_id = None
    
    # Buscar salida previa
    for i in range(max(0, idx_p - 100), idx_p):
        m_ant = mensajes[i]
        f_ant = m_ant[1]
        if f_ant < ventana_inicio:
            continue
        txt_ant = (m_ant[4] or '').lower()
        tiene_img_ant = m_ant[5]
        
        # Coincidencia de unidad si es posible
        u_m = normalizar_unidad(txt_ant)
        if ('sale' in txt_ant or 'salida' in txt_ant):
            if u_m == unidad_norm or unidad_norm == "SIN_UNIDAD" or any(u in txt_ant for u in ['097','098','208','ambulancia']):
                rol = "SALIDA"
                if tiene_img_ant and not foto_salida_id:
                    foto_salida_id = m_ant[6]
                    rol = "FOTO_ODOMETRO_SALIDA"
                mensajes_caso.append((m_ant, rol))
        elif 'en el lugar' in txt_ant or 'en el punto' in txt_ant or '10-97' in txt_ant:
            mensajes_caso.append((m_ant, "ARRIBO_ESCENA"))
        elif tiene_img_ant and f_ant > ventana_inicio + timedelta(minutes=15):
            mensajes_caso.append((m_ant, "FOTO_ESCENA_ATENCION"))
            
    # El parte médico es el centro
    mensajes_caso.append((m_p, "PARTE_MEDICO_FRAP"))
    
    # Buscar retorno a base después del parte
    for i in range(idx_p + 1, min(len(mensajes), idx_p + 80)):
        m_pos = mensajes[i]
        f_pos = m_pos[1]
        if f_pos > ventana_fin:
            break
        txt_pos = (m_pos[4] or '').lower()
        tiene_img_pos = m_pos[5]
        
        if 'base' in txt_pos or 'retorna' in txt_pos or '10 a base' in txt_pos:
            rol = "RETORNO_BASE"
            if tiene_img_pos and not foto_retorno_id:
                foto_retorno_id = m_pos[6]
                rol = "FOTO_ODOMETRO_RETORNO"
            mensajes_caso.append((m_pos, rol))
        elif tiene_img_pos:
            mensajes_caso.append((m_pos, "FOTO_SEGUIMIENTO"))

    # Armar ID del caso
    casos_creados += 1
    id_caso = f"CASO-{f_p.strftime('%Y%m%d')}-{unidad_norm}-{casos_creados:03d}"
    
    # Calcular fechas de inicio y fin del caso
    f_ini = mensajes_caso[0][0][1] if mensajes_caso else f_p
    f_fin = mensajes_caso[-1][0][1] if mensajes_caso else f_p
    duracion = int((f_fin - f_ini).total_seconds() / 60)
    
    total_fotos = sum(1 for m_c in mensajes_caso if m_c[0][5])
    
    # Insertar en tabla casos
    sql_cur.execute('''
    INSERT INTO casos (
        id_caso, unidad, tipo_caso, fecha_inicio, fecha_fin, duracion_minutos,
        paciente_nombre, paciente_edad, direccion, diagnostico, hospital_destino,
        medico_recibe, codigo_triage, operador, paramedico, tercero_abordo,
        foto_salida_id, foto_retorno_id, total_fotos, total_mensajes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        id_caso, unidad_norm, p_info['tipo'], f_ini.strftime('%Y-%m-%d %H:%M:%S'), f_fin.strftime('%Y-%m-%d %H:%M:%S'), duracion,
        p_info['paciente'], p_info['edad'], p_info['direccion'], p_info['diagnostico'], p_info['hospital'],
        p_info['recibe'], p_info['codigo'], p_info['operador'], p_info['paramedico'], p_info['tercero'],
        foto_salida_id, foto_retorno_id, total_fotos, len(mensajes_caso)
    ))
    
    # Insertar mensajes del caso
    for m_c, rol in mensajes_caso:
        mid_c, f_c, push_c, mtype_c, txt_c, tiene_img_c, wa_id_c, _, _ = m_c
        sql_cur.execute('''
        INSERT INTO caso_mensajes (
            id_caso, wa_id, fecha_hora, remitente, tipo_mensaje, texto, es_foto, rol_mensaje
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            id_caso, wa_id_c, f_c.strftime('%Y-%m-%d %H:%M:%S'), push_c, mtype_c, txt_c, 1 if tiene_img_c else 0, rol
        ))

sql_conn.commit()
print(f"Total casos estructurados e insertados en SQLite: {casos_creados}")

# Mostrar resumen estadístico de SQLite
sql_cur.execute('''
    SELECT tipo_caso, count(*), sum(total_fotos), sum(total_mensajes)
    FROM casos
    GROUP BY tipo_caso
''')
print("\n--- RESUMEN EN BASE DE DATOS DE CASOS DOCUMENTADOS (bitacora_casos_pc.db) ---")
for row in sql_cur.fetchall():
    print(f"Tipo: {row[0]:30} | Casos: {row[1]:3} | Total Fotos: {row[2]:3} | Total Mensajes: {row[3]:4}")

sql_conn.close()
pg_conn.close()
