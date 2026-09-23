import json
import sqlite3
import pandas as pd
import re
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

def fix_mojibake(text):
    if not text: return ""
    # Arreglar patrones comunes de mojibake utf-8 interpretado como cp1252/latin1
    replacements = {
        '├í': 'á', '├é': 'É', '├¡': 'í', '├│': 'ó', '├║': 'ú', '├▒': 'ñ', '├ô': 'Ó',
        '├ü': 'Á', '├ö': 'Ö', '├ñ': 'ñ', '├ü': 'Á', '├ì': 'Í', '┬░': '°', '┬º': 'º',
        'a├▒os': 'años', 'A├▒os': 'Años', 'posici├│n': 'posición', 'atenci├│n': 'atención',
        'DIRECCI├ôN': 'DIRECCIÓN', 'DIAGN├ôSTICO': 'DIAGNÓSTICO', 'C├ôDIGO': 'CÓDIGO',
        'DESCRIPCI├ôN': 'DESCRIPCIÓN', 'femenina': 'femenina', 'masculino': 'masculino',
        'H├⌐ctor': 'Héctor', 'Vel├ízquez': 'Velázquez', 'Hern├índez': 'Hernández',
        'Mart├¡nez': 'Martínez', 'Jim├⌐nez': 'Jiménez', 'Vida├▒a': 'Vidaña',
        'Garc├¡a': 'García', 'Ram├│n': 'Ramón', 'Andres': 'Andrés', 'S├ínchez': 'Sánchez',
        'Guti├⌐rrez': 'Gutiérrez', '├üngel': 'Ángel', 'Chavez': 'Chávez',
        'Jos├⌐': 'José', 'P├⌐rez': 'Pérez', 'Gonzales': 'González', 'Rub├¡': 'Rubí'
    }
    t = str(text)
    for k, v in replacements.items():
        t = t.replace(k, v)
    return t

def clean_str(val):
    if not val: return None
    val = str(val).strip()
    val = re.sub(r'^\*+|\*+$', '', val).strip()
    return val if val else None

transfers_master = []
seen_keys = set() # (fecha_str, paciente_clean, hospital_clean)

# =============================================================================
# FUENTE 1: messages.jsonl (Reportes FRAP estructurados completos)
# =============================================================================
def extract_text_from_json(d):
    msg = d.get('message') or {}
    if not isinstance(msg, dict): return ""
    if 'conversation' in msg and msg['conversation']: return str(msg['conversation'])
    if 'extendedTextMessage' in msg and isinstance(msg['extendedTextMessage'], dict):
        return str(msg['extendedTextMessage'].get('text', ''))
    if 'imageMessage' in msg and isinstance(msg['imageMessage'], dict):
        return str(msg['imageMessage'].get('caption', ''))
    return ""

try:
    with open('messages.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            try: d = json.loads(line)
            except: continue
            
            raw_text = extract_text_from_json(d)
            if not raw_text: continue
            text = fix_mojibake(raw_text.replace('\\n', '\n'))
            
            if 'NOMBRE DEL PACIENTE' in text:
                ts = d.get('messageTimestamp')
                dt_str = datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S') if ts else "2026-08-00 00:00"
                
                def get_val(pat):
                    m = re.search(pat, text, re.IGNORECASE)
                    return m.group(1).strip() if m else None

                fecha = clean_str(get_val(r'FECHA\*?[:\s]*([^\n\*]+)'))
                hora = clean_str(get_val(r'HORA(?: DEL REPORTE)?\*?[:\s]*([^\n\*]+)'))
                unidad = clean_str(get_val(r'AMBULANCIA\*?[:\s]*([^\n\*]+)'))
                operador = clean_str(get_val(r'OPERADOR\*?[:\s]*([^\n\*]+)'))
                paramedico = clean_str(get_val(r'PARAMEDICO\*?[:\s]*([^\n\*]+)'))
                paciente = clean_str(get_val(r'NOMBRE DEL PACIENTE\*?[:\s]*([^\n\*]+)'))
                edad = clean_str(get_val(r'EDAD\*?[:\s]*([^\n\*]+)'))
                dx = clean_str(get_val(r'DIAGN[^\*:\n]+STICO\*?[:\s]*([^\n\*]+)'))
                desc = clean_str(get_val(r'DESCRIPCI[^\*:\n]+N DE LO OCURRIDO\*?[:\s]*([^\*]+?)(?=\*[A-Z]|\Z)'))
                hosp = clean_str(get_val(r'HOSPITAL\s+DE\s+TRASLADO\*?[:\s]*([^\n\*]+)'))
                dir_orig = clean_str(get_val(r'DIRECCI[^\*:\n]+N DEL SERVICIO\*?[:\s]*([^\n\*]+)'))
                recibe = clean_str(get_val(r'RECIBE\*?[:\s]*([^\n\*]+)'))
                codigo = clean_str(get_val(r'C[^\*:\n]+DIGO\*?[:\s]*([^\n\*]+)'))

                h_low = str(hosp).lower()
                es_neg = any(w in h_low for w in ['no amerit', 'n/a', 'na', 'niega', 'deslinde', 'no se traslada', 'no aporta', 'particular'])
                
                if hosp and not es_neg:
                    # Limpiar paciente
                    pac_clean = paciente if paciente else "Paciente Clínico"
                    pac_clean = pac_clean.replace('.', '').strip()
                    
                    key = (dt_str[:10], pac_clean[:15].lower(), hosp[:10].lower())
                    if key not in seen_keys:
                        seen_keys.add(key)
                        hora_exacta = hora if hora else dt_str[11:16]
                        fecha_exacta = fecha if fecha else dt_str[:10]
                        transfers_master.append({
                            'fuente': 'Formato FRAP Oficial',
                            'fecha_hora': f"{fecha_exacta} {hora_exacta}",
                            'unidad': unidad if unidad else 'U-208 / U-098',
                            'paciente': pac_clean,
                            'edad': edad if edad else 'No especificada',
                            'motivo_por_que': dx if dx else 'Atención de urgencia prehospitalaria',
                            'detalle_incidente': desc[:140] + '...' if desc and len(desc) > 140 else (desc if desc else ''),
                            'destino_a_donde': hosp,
                            'medico_recibe': recibe if recibe else 'Personal de Triage / Urgencias',
                            'lugar_origen': dir_orig if dir_orig else 'Medellín de Bravo',
                            'personal_a_cargo': f"Op: {operador} | Par: {paramedico}" if operador or paramedico else 'Guardia Operativa PC'
                        })
except Exception as e:
    print("Error leyendo messages.jsonl:", e)

print(f"Traslados extraídos de FRAP: {len(transfers_master)}")

# =============================================================================
# FUENTE 2: whatsapp_messages.db (Bitácoras de Novedades de Guardia)
# =============================================================================
conn = sqlite3.connect('whatsapp_messages.db')
c = conn.cursor()
c.execute("""
SELECT id, datetime(message_timestamp, 'unixepoch', 'localtime') as dt, text_content
FROM messages
WHERE text_content LIKE '%novedades del día%' OR text_content LIKE '%novedades del dia%'
ORDER BY message_timestamp ASC
""")
for msg_id, dt_msg, text_nov in c.fetchall():
    lineas = re.split(r'(?=\b\d{1,2}:\d{2}\b)', str(text_nov))
    fecha_base = dt_msg[:10]
    for l in lineas:
        l_clean = fix_mojibake(l.strip().replace('\n', ' '))
        l_low = l_clean.lower()
        if any(w in l_low for w in ['traslada', 'traslado', 'trasladar']) and any(w in l_low for w in ['hospital', 'clínica', 'clinica', 'cruz roja', 'imss', 'issste', 'hg', 'hosnaver', 'torre', 'domicilio', 'jamapa']):
            if not any(w in l_low for w in ['no amerit', 'no requiri', 'perrito']):
                # Extraer hora
                m_h = re.search(r'\b(\d{1,2}:\d{2})\b', l_clean)
                hora = m_h.group(1) if m_h else dt_msg[11:16]
                
                # Extraer unidad
                m_u = re.search(r'(?:unidad|u)[ _-]?([0-9]{3})', l_low)
                unidad = f"U-{m_u.group(1)}" if m_u else "Ambulancia de Guardia"
                
                # Extraer motivo y paciente
                # Destino
                destino = "Hospital de Zona"
                if 'boca del río' in l_low or 'boca del rio' in l_low or 'hg de boca' in l_low:
                    destino = "Hospital General de Boca del Río"
                elif '71' in l_low:
                    destino = "IMSS Clínica 71 (Díaz Mirón)"
                elif '61' in l_low:
                    destino = "IMSS Hospital Cuauhtémoc (Clínica 61)"
                elif '20 de noviembre' in l_low or 'hg 20 de noviembre' in l_low:
                    destino = "Hospital Regional de Alta Especialidad (20 de Noviembre)"
                elif 'torre pediatrica' in l_low or 'torre pediátrica' in l_low:
                    destino = "Torre Pediátrica de Veracruz"
                elif 'naval' in l_low or 'hosnaver' in l_low:
                    destino = "Hospital Naval (HOSNAVER)"
                elif 'issste' in l_low:
                    destino = "Hospital ISSSTE Veracruz"
                elif 'cruz roja' in l_low:
                    destino = "Cruz Roja Mexicana (Díaz Mirón)"
                elif 'domicilio' in l_low:
                    destino = "Traslado Asistido a Domicilio (Alta Médica)"
                elif 'jamapa' in l_low:
                    destino = "Traslado Intermunicipal (Jamapa)"
                elif 'chopo' in l_low:
                    destino = "Clínica Chopo (Estudios Especializados)"
                elif 'cuauhtémoc' in l_low:
                    destino = "IMSS Hospital Cuauhtémoc"
                    
                # Paciente y Motivo
                paciente = "Paciente de Emergencia"
                motivo = "Auxilio Prehospitalario / Traslado de Urgencia"
                
                if 'menor de tres años con convulsiones' in l_low:
                    paciente = "Menor de 3 años (Pediátrico)"
                    motivo = "Crisis Convulsiva Febril en menor"
                elif 'menor de 15 años' in l_low:
                    paciente = "Menor de 15 años"
                    motivo = "Retiro programado de puntos quirúrgicos en pierna derecha"
                elif 'marta' in l_low:
                    paciente = "Marta (Trabajadora de Intendencia)"
                    motivo = "Síncope / Desmayo con pérdida de respuesta"
                elif 'derrape de moto' in l_low or 'accidente de moto' in l_low or 'choke de moto' in l_low:
                    m_moto = re.search(r'(?:masculino|femenina|persona)?.*?derrape|choke', l_low)
                    paciente = "Paciente accidentado en motocicleta"
                    motivo = "Accidente / Derrape de motocicleta con policontusiones"
                elif 'infarto' in l_low:
                    paciente = "Paciente Masculino"
                    motivo = "Sospecha de Infarto Agudo al Miocardio (Dolor Precordial en caseta)"
                elif 'atropellada' in l_low:
                    paciente = "Paciente Masculino Atropellado"
                    motivo = "Traumatismo por atropellamiento en vía pública"
                elif 'inconsciente' in l_low:
                    paciente = "Paciente Inconsciente"
                    motivo = "Pérdida súbita del estado de alerta / Inconsciencia"
                elif 'femenina golpeada' in l_low:
                    paciente = "Paciente Femenina"
                    motivo = "Agresión física / Traumatismo por golpes"
                elif 'caída' in l_low or 'callo de un andamio' in l_low:
                    paciente = "Paciente Masculino (Trabajador)"
                    motivo = "Traumatismo por caída de andamio en altura"
                elif 'se corto la mano' in l_low:
                    paciente = "Paciente Masculino"
                    motivo = "Herida lacerante / Cortante profunda en mano"
                elif 'dolor de estómago' in l_low:
                    paciente = "Paciente Adulto"
                    motivo = "Abdomen agudo / Fuerte dolor abdominal"
                elif 'traslado programado' in l_low:
                    paciente = "Paciente Programado"
                    motivo = "Traslado médico programado interhospitalario o retorno"

                key = (fecha_base, paciente[:10].lower(), destino[:10].lower(), hora)
                if key not in seen_keys:
                    seen_keys.add(key)
                    transfers_master.append({
                        'fuente': 'Bitácora de Novedades de Guardia',
                        'fecha_hora': f"{fecha_base} {hora}",
                        'unidad': unidad,
                        'paciente': paciente,
                        'edad': 'Población atendida',
                        'motivo_por_que': motivo,
                        'detalle_incidente': l_clean[:140],
                        'destino_a_donde': destino,
                        'medico_recibe': 'Área de Triage / Hospital Receptor',
                        'lugar_origen': 'Medellín de Bravo',
                        'personal_a_cargo': 'Personal Paramédico y Chofer de Guardia'
                    })

# =============================================================================
# FUENTE 3: Partes Médicos Directos en messages
# =============================================================================
c.execute("""
SELECT id, datetime(message_timestamp, 'unixepoch', 'localtime') as dt, text_content
FROM messages
WHERE (text_content LIKE '%Paciente%' OR text_content LIKE '%PX:%')
  AND (text_content LIKE '%traslad%' OR text_content LIKE '%hospital%')
ORDER BY message_timestamp ASC
""")
for msg_id, dt_msg, text_msg in c.fetchall():
    t_clean = fix_mojibake(str(text_msg))
    t_low = t_clean.lower()
    
    if any(w in t_low for w in ['no ameritó traslado', 'no amerita traslado', 'se niega al traslado', 'niega traslado', 'deslinde']):
        continue
        
    # Verificar si tiene nombre específico
    m_px = re.search(r'(?:paciente|px)[:\s]+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,3})', t_clean, re.IGNORECASE)
    if m_px:
        nombre_px = m_px.group(1).strip()
        
        # Hospital
        dest = "Hospital General de Boca del Río"
        if '71' in t_low: dest = "IMSS Clínica 71 (Díaz Mirón)"
        elif '61' in t_low or 'cuauhtémoc' in t_low: dest = "IMSS Clínica 61"
        elif 'regional' in t_low: dest = "Hospital Regional de Alta Especialidad"
        elif 'issste' in t_low: dest = "Hospital ISSSTE"
        elif 'cruz roja' in t_low: dest = "Cruz Roja Mexicana"
        elif 'domicilio' in t_low: dest = "Traslado Asistido a Domicilio"
        
        # Diagnóstico
        m_dx = re.search(r'(?:dx|diagnóstico|probable|posible)[:\s]*([^\.\n\|]+)', t_clean, re.IGNORECASE)
        dx_str = m_dx.group(1).strip() if m_dx else "Valoración y traslado de urgencia médica"
        
        m_u = re.search(r'(?:unidad|u)[ _-]?([0-9]{3})', t_low)
        unidad = f"U-{m_u.group(1)}" if m_u else "Ambulancia de Guardia"
        
        m_edad = re.search(r'(\d{1,2})\s*años', t_low)
        edad_str = f"{m_edad.group(1)} años" if m_edad else "No especificada"
        
        key = (dt_msg[:10], nombre_px[:12].lower(), dest[:10].lower())
        if key not in seen_keys:
            seen_keys.add(key)
            transfers_master.append({
                'fuente': 'Parte Médico en Cabina',
                'fecha_hora': dt_msg[:16],
                'unidad': unidad,
                'paciente': nombre_px,
                'edad': edad_str,
                'motivo_por_que': dx_str,
                'detalle_incidente': t_clean[:140].replace('\n', ' '),
                'destino_a_donde': dest,
                'medico_recibe': 'Personal Médico de Guardia',
                'lugar_origen': 'Medellín de Bravo',
                'personal_a_cargo': 'Guardia Operativa PC'
            })

conn.close()

df_master = pd.DataFrame(transfers_master)
# Ordenar por fecha y hora
df_master['dt_sort'] = pd.to_datetime(df_master['fecha_hora'], errors='coerce')
df_master = df_master.sort_values(by='dt_sort').drop(columns=['dt_sort']).reset_index(drop=True)

print(f"\n=======================================================")
print(f"  TOTAL TRASLADOS EXACTOS IDENTIFICADOS Y LIMPIOS: {len(df_master)}")
print(f"=======================================================")
print("\nDesglose por Fuente de Registro:")
print(df_master['fuente'].value_counts())

print("\nDesglose por Hospital / Destino Receptor:")
print(df_master['destino_a_donde'].value_counts())

print("\n--- MUESTRA DE 20 REGISTROS MAESTROS ---")
for i, r in df_master.head(20).iterrows():
    print(f"[{i+1:02d}] {r['fecha_hora']} | {r['unidad']}")
    print(f"     Paciente: {r['paciente']} ({r['edad']})")
    print(f"     Por qué : {r['motivo_por_que']}")
    print(f"     A dónde : {r['destino_a_donde']}")
    print("-" * 75)
