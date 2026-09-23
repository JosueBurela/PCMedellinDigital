import sqlite3
import re
from datetime import datetime

conn = sqlite3.connect('whatsapp_messages.db')
c = conn.cursor()

# Get all messages mentioning transfer or hospitals
query = """
SELECT id, message_timestamp, push_name, text_content
FROM messages
WHERE text_content LIKE '%traslado%'
   OR text_content LIKE '%traslada%'
   OR text_content LIKE '%hospital%'
   OR text_content LIKE '%imss%'
   OR text_content LIKE '%regional%'
ORDER BY message_timestamp ASC
"""

rows = c.execute(query).fetchall()
print(f"Total mensajes candidatos en SQLite: {len(rows)}")

transports = []
for r in rows:
    msg_id, ts, sender, text = r
    if not text: continue
    t_lower = text.lower()
    
    # Filter out chatter
    if len(text.strip()) < 15: continue
    if 'se cancela' in t_lower or 'no amerita' in t_lower or 'falsa alarma' in t_lower: continue
    
    # Check if mentions hospital or transfer action
    hosp_match = re.search(r'(hospital regional|regional de alta especialidad|imss 61|imss 71|imss de cuauht[eé]moc|cruz roja|hospital de boca|tarimoya|milenio|sanatorio|hospital)', t_lower)
    tras_match = re.search(r'(traslada|trasladad[oa]|se traslada|traslado al|en camino al|arribando al|ingresa al)', t_lower)
    
    if hosp_match or (tras_match and ('paciente' in t_lower or 'lesionad' in t_lower or 'femenin' in t_lower or 'masculin' in t_lower)):
        dt_str = datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M') if ts else 'N/A'
        hospital = hosp_match.group(0).title() if hosp_match else 'Hospital por confirmar'
        
        # Look for patient info
        name_match = re.search(r'(?:nombre|paciente|se trata de|se traslada a)\s*[:\-]?\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,3})', text)
        patient_name = name_match.group(1).strip() if name_match else None
        
        if not patient_name:
            if 'masculino' in t_lower:
                patient_name = "Masculino (Sin datos / En calidad de desconocido)"
            elif 'femenina' in t_lower or 'femenino' in t_lower:
                patient_name = "Femenina (Sin datos / En calidad de desconocida)"
            elif 'menor' in t_lower:
                patient_name = "Menor de edad (Identidad reservada / Sin datos)"
            else:
                patient_name = "Paciente lesionado (Sin datos registrados en radio)"
                
        # Unit
        unit_match = re.search(r'(U-?\s*208|U-?\s*097|U-?\s*098|U-?\s*01|Unidad\s*\d+)', text, re.I)
        unit = unit_match.group(0).upper().replace(" ", "") if unit_match else "U-208"
        
        # Diagnosis / Reason
        diag = "Emergencia médica / traumatismo"
        if 'moto' in t_lower or 'derrape' in t_lower:
            diag = "Accidente en motocicleta / Derrape con policontusiones"
        elif 'atropellad' in t_lower:
            diag = "Atropellamiento en vía pública / Traumatismo"
        elif 'choque' in t_lower or 'vehicular' in t_lower:
            diag = "Accidente vehicular / Colisión"
        elif 'arma blanca' in t_lower or 'machete' in t_lower or 'herida' in t_lower:
            diag = "Herida penetrante / Agresión"
        elif 'parto' in t_lower or 'labor' in t_lower or 'embarazo' in t_lower:
            diag = "Urgencia obstétrica / Labor de parto"
        elif 'ca[ií]da' in t_lower:
            diag = "Traumatismo por caída de propia altura / desnivel"
        elif 'convuls' in t_lower:
            diag = "Crisis convulsiva / Síndrome neurológico"
        elif 'diab' in t_lower or 'gluc' in t_lower:
            diag = "Crisis metabólica / Descompensación diabética"
        elif 'hipertens' in t_lower or 'presi[oó]n' in t_lower:
            diag = "Crisis hipertensiva / Urgencia cardiovascular"
            
        transports.append({
            'datetime': dt_str,
            'unit': unit,
            'patient': patient_name,
            'diag': diag,
            'hospital': hospital,
            'text_snippet': text[:120].replace('\n', ' ')
        })

print(f"Total traslados operativos extraídos con radio: {len(transports)}")
print("\nMuestra de traslados operativos:")
for t in transports[:10]:
    print(f"[{t['datetime']}] {t['unit']} | {t['patient']} | {t['diag']} -> {t['hospital']}")
