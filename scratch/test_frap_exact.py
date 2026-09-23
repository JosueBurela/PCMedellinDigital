import json
import re
import sys
from datetime import datetime
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

def extract_text(m_dict):
    msg = m_dict.get('message') or {}
    if not isinstance(msg, dict):
        return ""
    if 'conversation' in msg and msg['conversation']:
        return str(msg['conversation'])
    if 'extendedTextMessage' in msg and isinstance(msg['extendedTextMessage'], dict):
        return str(msg['extendedTextMessage'].get('text', ''))
    if 'imageMessage' in msg and isinstance(msg['imageMessage'], dict):
        return str(msg['imageMessage'].get('caption', ''))
    return ""

def fix_mojibake(text):
    # Arregla posibles caracteres mal decodificados (ej. utf-8 decodificado como latin1 o cp1252)
    try:
        return text.encode('latin1').decode('utf-8')
    except:
        return text

def clean_field(v):
    if not v: return None
    v = v.strip()
    v = re.sub(r'^\*+|\*+$', '', v).strip()
    return v if v else None

frap_records = []

with open('messages.jsonl', 'r', encoding='utf-8') as f:
    for line_num, line in enumerate(f):
        if not line.strip(): continue
        try:
            d = json.loads(line)
        except:
            continue
        
        raw_text = extract_text(d)
        if not raw_text: continue
        
        # Corregir codificación si viene con mojibake
        text = fix_mojibake(raw_text.replace('\\n', '\n'))
        
        if 'NOMBRE DEL PACIENTE' in text or 'HOSPITAL' in text and 'TRASLADO' in text:
            ts = d.get('messageTimestamp')
            dt_str = datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S') if ts else "Desconocida"
            
            def get_frap(pat):
                m = re.search(pat, text, re.IGNORECASE)
                return m.group(1).strip() if m else None

            fecha = clean_field(get_frap(r'FECHA\*?[:\s]*([^\n\*]+)'))
            hora = clean_field(get_frap(r'HORA(?: DEL REPORTE)?\*?[:\s]*([^\n\*]+)'))
            unidad = clean_field(get_frap(r'AMBULANCIA\*?[:\s]*([^\n\*]+)'))
            operador = clean_field(get_frap(r'OPERADOR\*?[:\s]*([^\n\*]+)'))
            paramedico = clean_field(get_frap(r'PARAMEDICO\*?[:\s]*([^\n\*]+)'))
            tipo_serv = clean_field(get_frap(r'TIPO DE SERVICIO\*?[:\s]*([^\n\*]+)'))
            nombre = clean_field(get_frap(r'NOMBRE DEL PACIENTE\*?[:\s]*([^\n\*]+)'))
            edad = clean_field(get_frap(r'EDAD\*?[:\s]*([^\n\*]+)'))
            desc = clean_field(get_frap(r'DESCRIPCI[ÓO]N DE LO OCURRIDO\*?[:\s]*([^\*]+?)(?=\*[A-Z]|\Z)'))
            dx = clean_field(get_frap(r'DIAGN[ÓO]STICO\*?[:\s]*([^\n\*]+)'))
            hospital = clean_field(get_frap(r'HOSPITAL\s+DE\s+TRASLADO\*?[:\s]*([^\n\*]+)'))
            direccion = clean_field(get_frap(r'DIRECCI[ÓO]N DEL SERVICIO\*?[:\s]*([^\n\*]+)'))
            recibe = clean_field(get_frap(r'RECIBE\*?[:\s]*([^\n\*]+)'))
            codigo = clean_field(get_frap(r'C[ÓO]DIGO\*?[:\s]*([^\n\*]+)'))

            # Traslado efectivo vs no amerita
            h_low = str(hospital).lower()
            es_negativa = any(w in h_low for w in ['no amerita', 'n/a', 'na', 'niega', 'deslinde', 'no se traslada', 'no aporta', 'particular'])
            trasladado = bool(hospital) and not es_negativa

            frap_records.append({
                'msg_id': d.get('id'),
                'fecha_hora_msg': dt_str,
                'fecha_frap': fecha,
                'hora_frap': hora,
                'unidad': unidad if unidad else "U-208 / U-098",
                'operador': operador,
                'paramedico': paramedico,
                'nombre_paciente': nombre,
                'edad': edad,
                'tipo_servicio': tipo_serv,
                'diagnostico': dx,
                'motivo_descripcion': desc.replace('\n', ' ') if desc else '',
                'hospital_destino': hospital,
                'direccion_origen': direccion,
                'medico_recibe': recibe,
                'codigo_triage': codigo,
                'traslado_efectivo': trasladado
            })

df_f = pd.DataFrame(frap_records)
print(f"Total reportes FRAP procesados: {len(df_f)}")
print("\nDesglose de traslado_efectivo:")
print(df_f['traslado_efectivo'].value_counts())

print("\nDesglose por Hospital Destino (Traslados Efectivos):")
print(df_f[df_f['traslado_efectivo']]['hospital_destino'].value_counts())

print("\n--- LISTA COMPLETA DE TRASLADOS EFECTIVOS FRAP ---")
for i, r in df_f[df_f['traslado_efectivo']].iterrows():
    print(f"[{r['fecha_hora_msg']}] Unidad: {r['unidad']} | Código: {r['codigo_triage']}")
    print(f"  Paciente: {r['nombre_paciente']} (Edad: {r['edad']})")
    print(f"  Por qué (Dx/Causa): {r['diagnostico']}")
    print(f"  Descripción: {r['motivo_descripcion'][:100]}...")
    print(f"  A dónde (Destino): {r['hospital_destino']} (Recibe: {r['medico_recibe']})")
    print(f"  Origen: {r['direccion_origen']}")
    print("-" * 75)
