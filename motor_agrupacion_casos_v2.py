import psycopg2
import re
import os
import sqlite3
import pandas as pd
import requests
import base64
from datetime import datetime, timedelta

print("Iniciando motor v2 de agrupamiento y catalogacion de casos...")

pg_conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
pg_cur = pg_conn.cursor()

GROUP_JID = '120363042493725288@g.us'
DB_FILE = 'bitacora_casos_pc.db'

# Conectar SQLite
sql_conn = sqlite3.connect(DB_FILE)
sql_cur = sql_conn.cursor()

sql_cur.execute('DROP TABLE IF EXISTS caso_mensajes;')
sql_cur.execute('DROP TABLE IF EXISTS casos;')

sql_cur.execute('''
CREATE TABLE casos (
    id_caso TEXT PRIMARY KEY,
    unidad TEXT,
    tipo_caso TEXT,
    fecha_reporte TEXT,
    hora_reporte TEXT,
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
    total_mensajes INTEGER DEFAULT 0,
    resumen_caso TEXT
)
''')

sql_cur.execute('''
CREATE TABLE caso_mensajes (
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
print(f"Total mensajes analizados: {len(mensajes)}")

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

    fecha = extraer([r'\*?FECHA\*?\s*:\s*([^\n\r\*]+)', r'FECHA\s*:\s*([^\n\r]+)'])
    hora = extraer([r'\*?HORA\*?\s*:\s*([^\n\r\*]+)', r'HORA\s*:\s*([^\n\r]+)'])
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
        'fecha': fecha,
        'hora': hora,
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

def extraer_unidad_clave(txt):
    if not txt: return ""
    m = re.search(r'(097|098|208|096|047|072|073|041)', txt)
    return m.group(1) if m else ""

# Detectar y desduplicar partes médicos
partes_unicos = []
vistos = set()

for idx, m in enumerate(mensajes):
    mid, f, push, mtype, txt, tiene_img, wa_id, k, msg = m
    parte_info = parsear_parte_medico(txt)
    if parte_info:
        # Clave de deduplicación: paciente + fecha en redondeo de horas
        pac_key = (parte_info['paciente'] or '').strip().lower()
        if not pac_key and len(txt) > 20:
            pac_key = txt[:30].strip().lower()
        clave = (pac_key, f.strftime('%Y-%m-%d-%H'))
        if clave not in vistos:
            vistos.add(clave)
            partes_unicos.append((idx, m, parte_info))

print(f"Total casos médicos únicos identificados tras deduplicación: {len(partes_unicos)}")

casos_insertados = 0
registros_excel_casos = []
registros_excel_mensajes = []

for idx_p, m_p, p_info in partes_unicos:
    f_p = m_p[1]
    u_clave = extraer_unidad_clave(p_info['ambulancia'])
    u_label = f"U-{u_clave}" if u_clave else "AMB"
    
    casos_insertados += 1
    id_caso = f"CASO-{f_p.strftime('%Y%m%d')}-{u_label}-{casos_insertados:03d}"
    
    ventana_inicio = f_p - timedelta(hours=2)
    ventana_fin = f_p + timedelta(hours=1, minutes=30)
    
    mensajes_caso = []
    foto_salida_id = None
    foto_retorno_id = None
    
    # 1. Buscar mensajes anteriores (salida, rumbo al punto, arribo)
    for i in range(max(0, idx_p - 80), idx_p):
        m_ant = mensajes[i]
        f_ant = m_ant[1]
        if f_ant < ventana_inicio:
            continue
            
        txt_ant = (m_ant[4] or '').lower()
        tiene_img_ant = m_ant[5]
        u_ant = extraer_unidad_clave(txt_ant)
        
        # Si menciona otra unidad diferente explícitamente (ej. U-096 vs U-098), omitir
        if u_clave and u_ant and u_ant != u_clave:
            continue
            
        if 'sale' in txt_ant or 'salida' in txt_ant:
            rol = "FOTO_ODOMETRO_SALIDA" if tiene_img_ant else "SALIDA_UNIDAD"
            if tiene_img_ant and not foto_salida_id:
                foto_salida_id = m_ant[6]
            mensajes_caso.append((m_ant, rol))
        elif 'en el lugar' in txt_ant or 'en el punto' in txt_ant or '10-97' in txt_ant:
            mensajes_caso.append((m_ant, "ARRIBO_ESCENA"))
        elif tiene_img_ant:
            # Foto relevante de la tripulación en el servicio
            mensajes_caso.append((m_ant, "FOTO_ESCENA_ATENCION"))
            
    # 2. El parte médico
    mensajes_caso.append((m_p, "PARTE_MEDICO_FRAP"))
    
    # 3. Buscar mensajes posteriores (retorno, en base)
    for i in range(idx_p + 1, min(len(mensajes), idx_p + 60)):
        m_pos = mensajes[i]
        f_pos = m_pos[1]
        if f_pos > ventana_fin:
            break
            
        txt_pos = (m_pos[4] or '').lower()
        tiene_img_pos = m_pos[5]
        u_pos = extraer_unidad_clave(txt_pos)
        
        if u_clave and u_pos and u_pos != u_clave:
            continue
            
        if 'base' in txt_pos or 'retorna' in txt_pos or '10 a base' in txt_pos:
            rol = "FOTO_ODOMETRO_RETORNO" if tiene_img_pos else "RETORNO_BASE"
            if tiene_img_pos and not foto_retorno_id:
                foto_retorno_id = m_pos[6]
            mensajes_caso.append((m_pos, rol))
        elif tiene_img_pos:
            mensajes_caso.append((m_pos, "FOTO_SEGUIMIENTO"))

    f_ini = mensajes_caso[0][0][1] if mensajes_caso else f_p
    f_fin = mensajes_caso[-1][0][1] if mensajes_caso else f_p
    duracion = max(0, int((f_fin - f_ini).total_seconds() / 60))
    total_fotos = sum(1 for mc in mensajes_caso if mc[0][5])
    
    resumen = f"Atención a {p_info['paciente'] or 'Px sin nombre'} ({p_info['edad'] or 'Edad N/D'}) por {p_info['diagnostico'] or 'diagnóstico no especificado'}."
    if p_info['tipo'] == 'TRASLADO_EFECTIVO_HOSPITAL':
        resumen += f" Trasladado al {p_info['hospital']}."
    elif p_info['tipo'] == 'NEGATIVA_DE_TRASLADO':
        resumen += " Paciente firma negativa de traslado."
    else:
        resumen += " Atendido y estabilizado en sitio."

    # Guardar en SQLite
    sql_cur.execute('''
    INSERT INTO casos (
        id_caso, unidad, tipo_caso, fecha_reporte, hora_reporte, fecha_inicio, fecha_fin,
        duracion_minutos, paciente_nombre, paciente_edad, direccion, diagnostico,
        hospital_destino, medico_recibe, codigo_triage, operador, paramedico, tercero_abordo,
        foto_salida_id, foto_retorno_id, total_fotos, total_mensajes, resumen_caso
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        id_caso, u_label, p_info['tipo'], p_info['fecha'] or f_p.strftime('%Y-%m-%d'), p_info['hora'] or f_p.strftime('%H:%M'),
        f_ini.strftime('%Y-%m-%d %H:%M:%S'), f_fin.strftime('%Y-%m-%d %H:%M:%S'), duracion,
        p_info['paciente'], p_info['edad'], p_info['direccion'], p_info['diagnostico'],
        p_info['hospital'], p_info['recibe'], p_info['codigo'], p_info['operador'],
        p_info['paramedico'], p_info['tercero'], foto_salida_id, foto_retorno_id,
        total_fotos, len(mensajes_caso), resumen
    ))
    
    registros_excel_casos.append({
        'ID_Caso': id_caso,
        'Unidad': u_label,
        'Tipo_Caso': p_info['tipo'],
        'Fecha_Reporte': p_info['fecha'] or f_p.strftime('%Y-%m-%d'),
        'Hora_Reporte': p_info['hora'] or f_p.strftime('%H:%M'),
        'Inicio_Servicio': f_ini.strftime('%Y-%m-%d %H:%M'),
        'Fin_Servicio': f_fin.strftime('%Y-%m-%d %H:%M'),
        'Duración_Min': duracion,
        'Paciente': p_info['paciente'],
        'Edad': p_info['edad'],
        'Diagnóstico_Motivo': p_info['diagnostico'],
        'Hospital_Destino': p_info['hospital'],
        'Dirección': p_info['direccion'],
        'Paramédico': p_info['paramedico'],
        'Operador': p_info['operador'],
        'Tercero_Abordo': p_info['tercero'],
        'Médico_Recibe': p_info['recibe'],
        'Código_Triage': p_info['codigo'],
        'Total_Fotos': total_fotos,
        'Total_Mensajes': len(mensajes_caso),
        'Resumen': resumen
    })

    for mc, rol in mensajes_caso:
        mid_c, f_c, push_c, mtype_c, txt_c, tiene_img_c, wa_id_c, _, _ = mc
        sql_cur.execute('''
        INSERT INTO caso_mensajes (
            id_caso, wa_id, fecha_hora, remitente, tipo_mensaje, texto, es_foto, rol_mensaje
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            id_caso, wa_id_c, f_c.strftime('%Y-%m-%d %H:%M:%S'), push_c, mtype_c, txt_c, 1 if tiene_img_c else 0, rol
        ))
        
        registros_excel_mensajes.append({
            'ID_Caso': id_caso,
            'Fecha_Hora': f_c.strftime('%Y-%m-%d %H:%M:%S'),
            'Remitente': push_c,
            'Rol_Operativo': rol,
            'Es_Foto': 'SÍ' if tiene_img_c else 'NO',
            'Tipo_Mensaje': mtype_c,
            'Mensaje_Texto': txt_c,
            'WA_Msg_ID': wa_id_c
        })

sql_conn.commit()
sql_conn.close()
pg_conn.close()

print(f"Base de datos SQLite actualizada: {DB_FILE}")

# Generar Excel con dos pestañas estructuradas
excel_path = "c:/Users/burel/OneDrive/Documentos/PCivil Digital/Expedientes_Casos_PC_Medellin.xlsx"
with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    df_casos = pd.DataFrame(registros_excel_casos)
    df_mensajes = pd.DataFrame(registros_excel_mensajes)
    
    # Separar casos por traslado vs atención en sitio
    df_traslados = df_casos[df_casos['Tipo_Caso'] == 'TRASLADO_EFECTIVO_HOSPITAL']
    df_atenciones = df_casos[df_casos['Tipo_Caso'] != 'TRASLADO_EFECTIVO_HOSPITAL']
    
    df_traslados.to_excel(writer, sheet_name='1. Traslados a Hospitales', index=False)
    df_atenciones.to_excel(writer, sheet_name='2. Atenciones y Negativas', index=False)
    df_mensajes.to_excel(writer, sheet_name='3. Cronología Mensajes y Fotos', index=False)

print(f"Excel generado exitosamente con 3 pestañas en: {excel_path}")
print(f"  - Traslados a Hospitales: {len(df_traslados)}")
print(f"  - Atenciones / Negativas en Sitio: {len(df_atenciones)}")
print(f"  - Mensajes y Fotos Cronológicos Vinculados: {len(df_mensajes)}")
