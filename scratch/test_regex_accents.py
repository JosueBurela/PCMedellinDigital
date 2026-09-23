import json
import re
import sys
from datetime import datetime
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

def extract_text(m_dict):
    msg = m_dict.get('message') or {}
    if not isinstance(msg, dict): return ""
    if 'conversation' in msg and msg['conversation']: return str(msg['conversation'])
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

records = []

with open('messages.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if not line.strip(): continue
        try:
            d = json.loads(line)
        except: continue
        
        raw_text = extract_text(d)
        if not raw_text: continue
        text = raw_text.replace('\\n', '\n')
        
        if 'NOMBRE DEL PACIENTE' in text:
            ts = d.get('messageTimestamp')
            dt_str = datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S') if ts else "Desconocida"
            
            def get_f(pat):
                m = re.search(pat, text, re.IGNORECASE)
                return m.group(1).strip() if m else None

            fecha = clean_val(get_f(r'FECHA\*?[:\s]*([^\n\*]+)'))
            hora = clean_val(get_f(r'HORA(?: DEL REPORTE)?\*?[:\s]*([^\n\*]+)'))
            unidad = clean_val(get_f(r'AMBULANCIA\*?[:\s]*([^\n\*]+)'))
            operador = clean_val(get_f(r'OPERADOR\*?[:\s]*([^\n\*]+)'))
            paramedico = clean_val(get_f(r'PARAMEDICO\*?[:\s]*([^\n\*]+)'))
            nombre = clean_val(get_f(r'NOMBRE DEL PACIENTE\*?[:\s]*([^\n\*]+)'))
            edad = clean_val(get_f(r'EDAD\*?[:\s]*([^\n\*]+)'))
            
            # Regex tolerante a acentos
            desc = clean_val(get_f(r'DESCRIPCI[^\*:\n]+N DE LO OCURRIDO\*?[:\s]*([^\*]+?)(?=\*[A-Z]|\Z)'))
            dx = clean_val(get_f(r'DIAGN[^\*:\n]+STICO\*?[:\s]*([^\n\*]+)'))
            hosp = clean_val(get_f(r'HOSPITAL\s+DE\s+TRASLADO\*?[:\s]*([^\n\*]+)'))
            direccion = clean_val(get_f(r'DIRECCI[^\*:\n]+N DEL SERVICIO\*?[:\s]*([^\n\*]+)'))
            recibe = clean_val(get_f(r'RECIBE\*?[:\s]*([^\n\*]+)'))
            codigo = clean_val(get_f(r'C[^\*:\n]+DIGO\*?[:\s]*([^\n\*]+)'))

            h_low = str(hosp).lower()
            es_negativa = any(w in h_low for w in ['no amerita', 'n/a', 'na', 'niega', 'deslinde', 'no se traslada', 'no aporta', 'particular'])
            trasladado = bool(hosp) and not es_negativa

            records.append({
                'dt': dt_str,
                'fecha': fecha,
                'hora': hora,
                'unidad': unidad,
                'paciente': nombre,
                'edad': edad,
                'dx': dx,
                'desc': desc.replace('\n', ' ') if desc else '',
                'hospital': hosp,
                'direccion': direccion,
                'recibe': recibe,
                'codigo': codigo,
                'trasladado': trasladado
            })

df_test = pd.DataFrame(records)
print(f"Total registros: {len(df_test)}")
print(f"Total trasladados: {df_test['trasladado'].sum()}")
for i, r in df_test[df_test['trasladado']].head(10).iterrows():
    print(f"\n[{r['dt']}] {r['unidad']}")
    print(f"  Paciente: {r['paciente']} ({r['edad']})")
    print(f"  Por qué (Dx): {r['dx']}")
    print(f"  Detalle: {r['desc'][:90]}...")
    print(f"  A dónde: {r['hospital']} (Recibe: {r['recibe']})")
    print(f"  Origen: {r['direccion']}")
