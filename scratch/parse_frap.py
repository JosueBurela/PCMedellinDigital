import sqlite3
import pandas as pd
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('whatsapp_messages.db')

query = """
SELECT id, remote_jid, push_name, text_content, 
       datetime(message_timestamp, 'unixepoch', 'localtime') as dt_local,
       message_timestamp
FROM messages
WHERE text_content LIKE '%NOMBRE DEL PACIENTE%' 
   OR text_content LIKE '%HOSPITAL DE TRASLADO%'
ORDER BY message_timestamp ASC
"""
df_frap = pd.read_sql_query(query, conn)
print(f"Total mensajes FRAP: {len(df_frap)}")

frap_records = []

def extract_field(text, patterns):
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            # Limpiar asteriscos y espacios
            val = re.sub(r'^\*+|\*+$', '', val).strip()
            if val:
                return val
    return None

for idx, row in df_frap.iterrows():
    text = row['text_content']
    
    # Extraer campos clave
    fecha = extract_field(text, [r'\*FECHA\*[:\s]*([^\n\*]+)', r'FECHA[:\s]*([^\n\*]+)'])
    ambulancia = extract_field(text, [r'\*AMBULANCIA\*[:\s]*([^\n\*]+)', r'AMBULANCIA[:\s]*([^\n\*]+)'])
    tipo_servicio = extract_field(text, [r'\*TIPO DE SERVICIO\*[:\s]*([^\n\*]+)', r'TIPO DE SERVICIO[:\s]*([^\n\*]+)'])
    nombre = extract_field(text, [r'\*NOMBRE DEL PACIENTE\*[:\s]*([^\n\*]+)', r'NOMBRE DEL PACIENTE[:\s]*([^\n\*]+)'])
    edad = extract_field(text, [r'\*EDAD\*[:\s]*([^\n\*]+)', r'EDAD[:\s]*([^\n\*]+)'])
    motivo = extract_field(text, [r'\*DESCRIPCI[ÓO]N DE LO OCURRIDO\*[:\s]*([^\*]+?)(?=\*[A-Z]|\Z)', r'DESCRIPCI[ÓO]N DE LO OCURRIDO[:\s]*([^\*]+?)(?=\*[A-Z]|\Z)'])
    diagnostico = extract_field(text, [r'\*DIAGN[ÓO]STICO\*[:\s]*([^\n\*]+)', r'DIAGN[ÓO]STICO[:\s]*([^\n\*]+)'])
    hospital = extract_field(text, [r'\*HOSPITAL DE TRASLADO\*[:\s]*([^\n\*]+)', r'HOSPITAL DE TRASLADO[:\s]*([^\n\*]+)'])
    direccion = extract_field(text, [r'\*DIRECCI[ÓO]N DEL SERVICIO\*[:\s]*([^\n\*]+)', r'DIRECCI[ÓO]N DEL SERVICIO[:\s]*([^\n\*]+)'])
    observaciones = extract_field(text, [r'\*OBSERVACIONES\*[:\s]*([^\*]+?)(?=\*[A-Z]|\Z)', r'OBSERVACIONES[:\s]*([^\*]+?)(?=\*[A-Z]|\Z)'])

    # Si en hospital dice 'n/a', 'no amerita traslado', 'niega traslado', etc.
    traslado_efectivo = True
    if hospital:
        h_low = hospital.lower()
        if any(w in h_low for w in ['n/a', 'na', 'no amerita', 'niega', 'sin traslado', 'deslinde', 'no se traslada', 'no aporta']):
            traslado_efectivo = False
    elif not hospital:
        traslado_efectivo = False
        
    frap_records.append({
        'msg_id': row['id'],
        'dt_msg': row['dt_local'],
        'fecha_frap': fecha,
        'unidad': ambulancia,
        'tipo': tipo_servicio,
        'nombre_paciente': nombre,
        'edad': edad,
        'direccion': direccion,
        'motivo': motivo.strip().replace('\n', ' ') if motivo else None,
        'diagnostico': diagnostico,
        'hospital_destino': hospital,
        'traslado_efectivo': traslado_efectivo,
        'raw_text': text[:200].replace('\n', ' ')
    })

df_f = pd.DataFrame(frap_records)
print(f"Total registros FRAP procesados: {len(df_f)}")
print("\nDesglose de hospital_destino en FRAP:")
print(df_f['hospital_destino'].value_counts(dropna=False))

print("\n--- CASOS FRAP CON TRASLADO EFECTIVO (Hospital confirmado) ---")
df_frap_efectivo = df_f[df_f['traslado_efectivo'] == True]
print(f"Total traslados efectivos confirmados en FRAP: {len(df_frap_efectivo)}")
for i, r in df_frap_efectivo.head(20).iterrows():
    print(f"\n[{r['dt_msg']}] Unidad: {r['unidad']}")
    print(f"  Paciente: {r['nombre_paciente']} ({r['edad']})")
    print(f"  Motivo / Dx: {r['diagnostico']} | {r['motivo'][:80] if r['motivo'] else ''}")
    print(f"  Destino: {r['hospital_destino']}")

conn.close()
