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

def clean_val(v):
    if not v: return None
    v = v.strip()
    v = re.sub(r'^\*+|\*+$', '', v).strip()
    return v if v else None

all_raw_frap = []

with open('messages.jsonl', 'r', encoding='utf-8') as f:
    for line_num, line in enumerate(f):
        if not line.strip(): continue
        try:
            d = json.loads(line)
        except:
            continue
        
        text = extract_text(d)
        if not text:
            continue
            
        text_clean = text.replace('\\n', '\n')
        text_low = text_clean.lower()
        
        # ¿Tiene formato FRAP o mención de paciente con traslado?
        if 'NOMBRE DEL PACIENTE' in text_clean or 'HOSPITAL DE TRASLADO' in text_clean:
            ts = d.get('messageTimestamp')
            dt_str = datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S') if ts else "Desconocida"
            
            # Helper regex
            def get_frap_field(pattern):
                m = re.search(pattern, text_clean, re.IGNORECASE)
                return m.group(1).strip() if m else None

            fecha = clean_val(get_frap_field(r'FECHA\*?[:\s]*([^\n\*]+)'))
            hora = clean_val(get_frap_field(r'HORA(?: DEL REPORTE)?\*?[:\s]*([^\n\*]+)'))
            unidad = clean_val(get_frap_field(r'AMBULANCIA\*?[:\s]*([^\n\*]+)'))
            operador = clean_val(get_frap_field(r'OPERADOR\*?[:\s]*([^\n\*]+)'))
            paramedico = clean_val(get_frap_field(r'PARAMEDICO\*?[:\s]*([^\n\*]+)'))
            tipo_serv = clean_val(get_frap_field(r'TIPO DE SERVICIO\*?[:\s]*([^\n\*]+)'))
            nombre = clean_val(get_frap_field(r'NOMBRE DEL PACIENTE\*?[:\s]*([^\n\*]+)'))
            edad = clean_val(get_frap_field(r'EDAD\*?[:\s]*([^\n\*]+)'))
            motivo = clean_val(get_frap_field(r'DESCRIPCI[ÓO]N DE LO OCURRIDO\*?[:\s]*([^\*]+?)(?=\*[A-Z]|\Z)'))
            diagnostico = clean_val(get_frap_field(r'DIAGN[ÓO]STICO\*?[:\s]*([^\n\*]+)'))
            hospital = clean_val(get_frap_field(r'HOSPITAL DE TRASLADO\*?[:\s]*([^\n\*]+)'))
            direccion = clean_val(get_frap_field(r'DIRECCI[ÓO]N DEL SERVICIO\*?[:\s]*([^\n\*]+)'))
            observaciones = clean_val(get_frap_field(r'OBSERVACIONES\*?[:\s]*([^\*]+?)(?=\*[A-Z]|\Z)'))

            # Determinar si fue traslado efectivo o no ameritó / se negó
            hosp_low = str(hospital).lower()
            es_negativa = any(w in hosp_low for w in ['no amerita', 'n/a', 'na', 'niega', 'deslinde', 'no se traslada', 'no aporta'])
            
            all_raw_frap.append({
                'id_msg': d.get('id'),
                'fecha_hora_msg': dt_str,
                'fecha_frap': fecha,
                'hora_frap': hora,
                'unidad': unidad,
                'operador': operador,
                'paramedico': paramedico,
                'tipo_servicio': tipo_serv,
                'nombre_paciente': nombre,
                'edad': edad,
                'motivo': motivo.replace('\n', ' ') if motivo else '',
                'diagnostico': diagnostico,
                'hospital_destino': hospital,
                'direccion': direccion,
                'es_traslado_efectivo': not es_negativa and bool(hospital),
                'texto_completo': text_clean
            })

print(f"Total reportes FRAP encontrados en messages.jsonl: {len(all_raw_frap)}")
df_frap_parsed = pd.DataFrame(all_raw_frap)
print("\nDesglose de es_traslado_efectivo en FRAP:")
print(df_frap_parsed['es_traslado_efectivo'].value_counts())

print("\nDesglose de hospital_destino (los que sí se trasladaron):")
print(df_frap_parsed[df_frap_parsed['es_traslado_efectivo']]['hospital_destino'].value_counts())

print("\n--- DETALLE DE LOS TRASLADOS EFECTIVOS EN FRAP ---")
for i, r in df_frap_parsed[df_frap_parsed['es_traslado_efectivo']].iterrows():
    print(f"\n[{r['fecha_hora_msg']}] Unidad: {r['unidad']}")
    print(f"  Paciente: {r['nombre_paciente']} (Edad: {r['edad']})")
    print(f"  Motivo / Dx: {r['diagnostico']} | {r['motivo'][:90]}...")
    print(f"  Destino: {r['hospital_destino']}")
    print(f"  Lugar: {r['direccion']}")
