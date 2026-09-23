import json
import sqlite3
import pandas as pd
import re
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# Cargar los datos actuales de scratch/generate_exact_transfers_doc.py
# Vamos a crear una función robusta de normalización
MESES_MAP = {
    'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
    'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
    'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
}

def normalizar_fecha_hora(raw_str):
    if not raw_str: return "2026-08-01 00:00", "01/08/2026 00:00"
    s = str(raw_str).strip()
    
    # 1. Extraer hora (HH:MM)
    m_h = re.search(r'\b(\d{1,2}):(\d{2})\b', s)
    if m_h:
        hh = int(m_h.group(1))
        mm = int(m_h.group(2))
        hora_str = f"{hh:02d}:{mm:02d}"
    else:
        hora_str = "12:00"
        
    # 2. Extraer fecha
    # Caso: "15 de Agosto del 2026" o "02 septiembre 2026"
    m_mes = re.search(r'(\d{1,2})\s+(?:de\s+)?([a-zA-Z]+)(?:\s+(?:del?\s+)?(\d{4}))?', s, re.IGNORECASE)
    if m_mes:
        dia = int(m_mes.group(1))
        mes_word = m_mes.group(2).lower()
        ano = int(m_mes.group(3)) if m_mes.group(3) else 2026
        mes_num = MESES_MAP.get(mes_word, '08')
        fecha_iso = f"{ano}-{mes_num}-{dia:02d}"
        fecha_mx = f"{dia:02d}/{mes_num}/{ano}"
        return f"{fecha_iso} {hora_str}", f"{fecha_mx} {hora_str}"
        
    # Caso: "04/ 08/2026" o "27/08/2026"
    m_slash = re.search(r'(\d{1,2})\s*/\s*(\d{1,2})\s*/\s*(\d{4})', s)
    if m_slash:
        dia = int(m_slash.group(1))
        mes = int(m_slash.group(2))
        ano = int(m_slash.group(3))
        fecha_iso = f"{ano}-{mes:02d}-{dia:02d}"
        fecha_mx = f"{dia:02d}/{mes:02d}/{ano}"
        return f"{fecha_iso} {hora_str}", f"{fecha_mx} {hora_str}"
        
    # Caso: "2026-08-04"
    m_dash = re.search(r'(\d{4})-(\d{2})-(\d{2})', s)
    if m_dash:
        ano = int(m_dash.group(1))
        mes = int(m_dash.group(2))
        dia = int(m_dash.group(3))
        fecha_iso = f"{ano}-{mes:02d}-{dia:02d}"
        fecha_mx = f"{dia:02d}/{mes:02d}/{ano}"
        return f"{fecha_iso} {hora_str}", f"{fecha_mx} {hora_str}"
        
    return "2026-08-15 12:00", "15/08/2026 12:00"

def normalizar_unidad(u_str):
    if not u_str: return "U-098"
    s = str(u_str).upper().replace('.', '').strip()
    if '208' in s and '098' in s: return "U-208 / U-098"
    if '208' in s: return "U-208"
    if '098' in s: return "U-098"
    if '097' in s: return "U-097"
    if '096' in s: return "U-096"
    if '072' in s: return "U-072 (Apoyo)"
    if '073' in s: return "U-073 (Apoyo)"
    if '041' in s: return "U-041 (Apoyo)"
    return "U-098"

def normalizar_hospital(h_str):
    if not h_str: return "Hospital General de Boca del Río"
    s = str(h_str).lower().strip()
    if 'boca del río' in s or 'boca del rio' in s or 'hg de boca' in s or 'hr boca' in s or 'hgbv' in s or 'boca' in s:
        return "Hospital General de Boca del Río"
    if '71' in s:
        return "IMSS Hospital General de Zona #71 (Díaz Mirón)"
    if '61' in s or 'cuauhtémoc' in s or 'cuauhtemoc' in s:
        return "IMSS Hospital General de Zona #61 (Cuauhtémoc)"
    if 'pediatrica' in s or 'pediátrica' in s or 'infantil' in s:
        return "Torre de la Niña y el Niño (Torre Pediátrica)"
    if 'regional' in s or '20 de noviembre' in s or 'haev' in s or 'alta especialidad' in s:
        return "Hospital Regional de Alta Especialidad de Veracruz"
    if 'naval' in s or 'hosnaver' in s:
        return "Hospital Naval de Alta Especialidad (HOSNAVER)"
    if 'issste' in s:
        return "Hospital ISSSTE de Alta Especialidad (Veracruz)"
    if 'cruz roja' in s:
        return "Cruz Roja Mexicana (Delegación Veracruz)"
    if 'star' in s:
        return "Hospital StarMédica Veracruz (Privado)"
    if 'chopo' in s:
        return "Laboratorios Chopo Veracruz (Gabinete Especializado)"
    if 'jamapa' in s:
        return "Traslado Intermunicipal a Cabecera de Jamapa"
    if 'domicilio' in s or 'casa' in s:
        return "Traslado Asistido a Domicilio (Alta Hospitalaria)"
    return "Hospital General de Boca del Río"

def normalizar_edad(e_str):
    if not e_str: return "No especificada"
    s = str(e_str).lower().strip()
    m = re.search(r'(\d{1,2})\s*(?:a[ñn]os?)?', s)
    if m:
        return f"{m.group(1)} años"
    if 'mes' in s:
        return s
    return "Adulto"

def normalizar_diagnostico(dx_raw):
    if not dx_raw: return "Atención médica prehospitalaria y traslado de urgencia"
    s = str(dx_raw).strip()
    # Limpiar prefijos
    s = re.sub(r'^(?:dx|diagnóstico|pb\.?|posible|probable)\s*[:\.\-]?\s*', '', s, flags=re.IGNORECASE).strip()
    s = re.sub(r'^\*+|\*+$', '', s).strip()
    
    # Reemplazos amigables y profesionales
    repl = [
        (r'\bTCE\b', 'Traumatismo Craneoencefálico (TCE)'),
        (r'\bIAM\b', 'Infarto Agudo al Miocardio (IAM)'),
        (r'\bEVC\b', 'Evento Vascular Cerebral (EVC)'),
        (r'\bFx\b', 'Fractura'),
        (r'\bHx\b', 'Herida'),
        (r'\bpx\b', 'paciente'),
        (r'\bPb\b', 'Probable'),
        (r'\bHTA\b', 'Hipertensión Arterial'),
    ]
    for p, r in repl:
        s = re.sub(p, r, s, flags=re.IGNORECASE)
    # Capitalizar primera letra
    if len(s) > 1:
        s = s[0].upper() + s[1:]
    # Recortar si es excesivamente largo
    if len(s) > 95:
        s = s[:92] + "..."
    return s

def normalizar_paciente(p_raw):
    if not p_raw: return "Paciente Clínico (No aportó datos)"
    s = str(p_raw).strip()
    s = re.sub(r'^\*+|\*+$', '', s).strip()
    s = s.replace('.', '').strip()
    # Casos genéricos
    if any(w in s.lower() for w in ['no aportó', 'no aporta', 'desconocido', 'sin nombre', 'femenina / masculino']):
        return "Paciente de Emergencia (Sin datos en cabina)"
    # Formatear a Title Case si viene en mayúsculas completas
    if s.isupper():
        s = s.title()
    return s

# Cargar desde el Excel recién generado
df_exactos = pd.read_excel('Documentacion/Registro_Nominal_Traslados_Exactos_2026.xlsx', skiprows=4)
# Renombrar columnas para consistencia
col_map = {
    'Fecha y Hora': 'fecha_hora',
    'Unidad': 'unidad',
    'Nombre del Paciente': 'paciente',
    'Edad': 'edad',
    'Por Qué (Diagnóstico / Motivo)': 'motivo_por_que',
    'A Dónde (Hospital Receptor)': 'destino_a_donde',
    'Recibe / Observaciones': 'recibe',
    'Lugar de Origen': 'lugar_origen'
}
df_exactos = df_exactos.rename(columns=col_map)

print(f"Total registros a normalizar: {len(df_exactos)}")

limpios = []
for idx, r in df_exactos.iterrows():
    f_iso, f_mx = normalizar_fecha_hora(r['fecha_hora'])
    u_clean = normalizar_unidad(r['unidad'])
    p_clean = normalizar_paciente(r['paciente'])
    e_clean = normalizar_edad(r['edad'])
    dx_clean = normalizar_diagnostico(r['motivo_por_que'])
    h_clean = normalizar_hospital(r['destino_a_donde'])
    
    # Observación / recibe corta y limpia
    recibe_raw = str(r['recibe']) if pd.notna(r['recibe']) else ""
    if any(w in recibe_raw.lower() for w in ['llamada de c5', 'reporte de c5', 'reporte por parte', 'nan', ':']):
        recibe_clean = "Área de Triage / Urgencias"
    elif len(recibe_raw) > 35:
        recibe_clean = recibe_raw[:32] + "..."
    else:
        recibe_clean = recibe_raw if recibe_raw.strip() else "Personal de Urgencias"
        
    limpios.append({
        'dt_iso': f_iso,
        'fecha_hora': f_mx,
        'unidad': u_clean,
        'paciente': p_clean,
        'edad': e_clean,
        'diagnostico': dx_clean,
        'hospital_destino': h_clean,
        'observaciones': recibe_clean,
        'origen': str(r['lugar_origen'])[:35] if pd.notna(r['lugar_origen']) else "Medellín de Bravo"
    })

df_clean = pd.DataFrame(limpios)
df_clean = df_clean.sort_values(by='dt_iso').reset_index(drop=True)
df_clean.index += 1

print("\n--- MUESTRA DE 10 REGISTROS NORMALIZADOS ---")
for i in range(1, 11):
    r = df_clean.loc[i]
    print(f"[{i:02d}] {r['fecha_hora']} | {r['unidad']} | {r['paciente']} ({r['edad']})")
    print(f"     Dx: {r['diagnostico']}")
    print(f"     Destino: {r['hospital_destino']} | {r['observaciones']}")
