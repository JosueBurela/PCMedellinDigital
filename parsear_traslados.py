import psycopg2
import re
import pandas as pd
from datetime import datetime

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()

GROUP_JID = '120363042493725288@g.us'

cur.execute('''
    SELECT 
        "id",
        to_timestamp("messageTimestamp") as fecha_msg,
        "pushName",
        "messageType",
        COALESCE(
            "message"->>'conversation',
            "message"->'extendedTextMessage'->>'text',
            "message"->'imageMessage'->>'caption',
            ''
        ) as texto,
        "key"->>'id' as wa_id
    FROM "Message"
    WHERE "key"->>'remoteJid' = %s
    ORDER BY "messageTimestamp" ASC
''', (GROUP_JID,))

rows = cur.fetchall()

def extraer_campo(texto, patrones):
    for pat in patrones:
        m = re.search(pat, texto, re.IGNORECASE | re.MULTILINE)
        if m:
            val = m.group(1).strip()
            # Limpiar asteriscos y espacios extra
            val = re.sub(r'^\*+|\*+$', '', val).strip()
            if val:
                return val
    return ""

registros_traslados = []

for r in rows:
    db_id, fecha_msg, remitente, mtype, texto, wa_id = r
    if not texto:
        continue
        
    t_lower = texto.lower()
    
    # Criterio: es un parte médico o ficha clínica de atención
    es_ficha = False
    if 'nombre del paciente' in t_lower or 'paciente' in t_lower and ('diagnostico' in t_lower or 'diagnóstico' in t_lower or 'hospital' in t_lower or 'edad' in t_lower):
        es_ficha = True
    elif '*ambulancia*' in t_lower and '*fecha*' in t_lower:
        es_ficha = True

    if not es_ficha:
        continue

    # Extraer campos
    fecha_reporte = extraer_campo(texto, [r'\*?FECHA\*?\s*:\s*([^\n\r\*]+)', r'FECHA\s*:\s*([^\n\r]+)'])
    hora_reporte = extraer_campo(texto, [r'\*?HORA\*?\s*:\s*([^\n\r\*]+)', r'HORA\s*:\s*([^\n\r]+)'])
    ambulancia = extraer_campo(texto, [r'\*?AMBULANCIA\*?\s*:\s*([^\n\r\*]+)', r'AMBULANCIA\s*:\s*([^\n\r]+)', r'\*?UNIDAD\*?\s*:\s*([^\n\r\*]+)'])
    operador = extraer_campo(texto, [r'\*?OPERADOR\*?\s*:\s*([^\n\r\*]+)', r'OPERADOR\s*:\s*([^\n\r]+)'])
    paramedico = extraer_campo(texto, [r'\*?PARAMEDICO\*?\s*:\s*([^\n\r\*]+)', r'\*?PARAMÉDICO\*?\s*:\s*([^\n\r\*]+)', r'PARAMEDICO\s*:\s*([^\n\r]+)'])
    tercero = extraer_campo(texto, [r'\*?TERCERO\s*ABORDO\*?\s*:\s*([^\n\r\*]+)'])
    paciente = extraer_campo(texto, [r'\*?NOMBRE\s*DEL\s*PACIENTE\*?\s*:\s*([^\n\r\*]+)', r'NOMBRE\s*DEL\s*PACIENTE\s*:\s*([^\n\r]+)'])
    edad = extraer_campo(texto, [r'\*?EDAD\*?\s*:\s*([^\n\r\*]+)', r'EDAD\s*:\s*([^\n\r]+)'])
    direccion = extraer_campo(texto, [r'\*?DIRECCI[OÓ]N\s*DEL\s*SERVICIO\*?\s*:\s*([^\n\r\*]+)', r'DIRECCI[OÓ]N\s*:\s*([^\n\r]+)'])
    tipo_servicio = extraer_campo(texto, [r'\*?TIPO\s*DE\s*SERVICIO\*?\s*:\s*([^\n\r\*]+)', r'TIPO\s*DE\s*SERVICIO\s*:\s*([^\n\r]+)'])
    descripcion = extraer_campo(texto, [r'\*?DESCRIPCI[OÓ]N\s*DE\s*LO\s*OCURRIDO\*?\s*:\s*([^\n\r\*]+)'])
    diagnostico = extraer_campo(texto, [r'\*?DIAGN[OÓ]STICO\*?\s*:\s*([^\n\r\*]+)', r'DIAGN[OÓ]STICO\s*:\s*([^\n\r]+)'])
    hospital = extraer_campo(texto, [r'\*?HOSPITAL\s*DE\s*TRASLADO\*?\s*:\s*([^\n\r\*]+)', r'HOSPITAL\s*:\s*([^\n\r]+)', r'TRASLADO\s*A\s*:\s*([^\n\r]+)'])
    recibe = extraer_campo(texto, [r'\*?RECIBE\*?\s*:\s*([^\n\r\*]+)'])
    codigo = extraer_campo(texto, [r'\*?C[OÓ]DIGO\*?\s*:\s*([^\n\r\*]+)'])
    despacha = extraer_campo(texto, [r'\*?DESPACHA\*?\s*:\s*([^\n\r\*]+)'])
    
    # Determinar Estatus de Traslado
    h_lower = (hospital or '').lower()
    t_full = texto.lower()
    if any(k in h_lower or k in t_full for k in ['se niega', 'niega traslado', 'se reusa']):
        estatus = "Negado por Paciente/Familiar"
    elif any(k in h_lower or k in t_full for k in ['no ameritó', 'no amerito', 'no amerita']):
        estatus = "No Ameritó Traslado (Atención en sitio)"
    elif any(k in h_lower for k in ['hospital', 'imss', 'issste', 'regional', 'faustino', 'tarimoya', 'beneficencia', '20 de noviembre', 'criver', 'torre médica', 'materno']) or (hospital and hospital.lower() not in ['n/a', 'na', 'ninguno', 'no']):
        estatus = "Traslado Efectivo a Hospital"
    else:
        estatus = "Atención en Sitio / Sin Traslado"
        
    registros_traslados.append({
        'Fecha_Mensaje': fecha_msg.strftime('%Y-%m-%d %H:%M'),
        'Fecha_Reporte': fecha_reporte or fecha_msg.strftime('%Y-%m-%d'),
        'Hora': hora_reporte or fecha_msg.strftime('%H:%M'),
        'Unidad': ambulancia,
        'Estatus_Traslado': estatus,
        'Hospital_Destino': hospital,
        'Nombre_Paciente': paciente,
        'Edad': edad,
        'Tipo_Servicio': tipo_servicio,
        'Diagnóstico_Motivo': diagnostico,
        'Dirección': direccion,
        'Operador': operador,
        'Paramédico': paramedico,
        'Tercero_Abordo': tercero,
        'Médico_Recibe': recibe,
        'Código_Prioridad': codigo,
        'Despacha': despacha,
        'Remitente_WhatsApp': remitente,
        'Texto_Original': texto
    })

print(f"Total registros catalogados: {len(registros_traslados)}")
df = pd.DataFrame(registros_traslados)
print("\nConteo por Estatus de Traslado:")
print(df['Estatus_Traslado'].value_counts())

excel_path = "c:/Users/burel/OneDrive/Documentos/PCivil Digital/Catalogo_Traslados_Medellin_2026.xlsx"
df.to_excel(excel_path, index=False)
print(f"\nExcel generado con éxito en: {excel_path}")

conn.close()
