import sqlite3
import pandas as pd
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('whatsapp_messages.db')

# Buscar mensajes que contienen partes clínicos o reportes de traslado
query = """
SELECT id, remote_jid, push_name, text_content, 
       datetime(message_timestamp, 'unixepoch', 'localtime') as dt_local,
       message_timestamp
FROM messages
WHERE text_content LIKE '%NOMBRE DEL PACIENTE%'
   OR text_content LIKE '%Paciente:%'
   OR text_content LIKE '%Px:%'
   OR text_content LIKE '%traslad%'
   OR text_content LIKE '%HOSPITAL DE TRASLADO%'
ORDER BY message_timestamp ASC
"""

df_msgs = pd.read_sql_query(query, conn)
print(f"Total mensajes encontrados: {len(df_msgs)}")

# Analicemos mensaje por mensaje
registros_traslados_directos = []

for idx, r in df_msgs.iterrows():
    text = str(r['text_content'])
    dt = r['dt_local']
    text_low = text.lower()
    
    # 1. ¿Es formato FRAP completo?
    if 'NOMBRE DEL PACIENTE' in text:
        # Extraer campos con regex precisa
        def get_val(pattern):
            m = re.search(pattern, text, re.IGNORECASE)
            return m.group(1).strip() if m else None

        nom = get_val(r'NOMBRE DEL PACIENTE\*?[:\s]*([^\n\*]+)')
        edad = get_val(r'EDAD\*?[:\s]*([^\n\*]+)')
        dx = get_val(r'DIAGN[ÓO]STICO\*?[:\s]*([^\n\*]+)')
        hosp = get_val(r'HOSPITAL DE TRASLADO\*?[:\s]*([^\n\*]+)')
        unidad = get_val(r'AMBULANCIA\*?[:\s]*([^\n\*]+)')
        desc = get_val(r'DESCRIPCI[ÓO]N DE LO OCURRIDO\*?[:\s]*([^\*]+?)(?=\*[A-Z]|\Z)')
        dir_serv = get_val(r'DIRECCI[ÓO]N DEL SERVICIO\*?[:\s]*([^\n\*]+)')
        tipo = get_val(r'TIPO DE SERVICIO\*?[:\s]*([^\n\*]+)')

        # Limpiar valores
        if nom: nom = re.sub(r'^\*+|\*+$', '', nom).strip()
        if hosp: hosp = re.sub(r'^\*+|\*+$', '', hosp).strip()
        if dx: dx = re.sub(r'^\*+|\*+$', '', dx).strip()
        if unidad: unidad = re.sub(r'^\*+|\*+$', '', unidad).strip()

        # Verificar si fue traslado efectivo o no
        hosp_low = str(hosp).lower()
        es_negativa = any(w in hosp_low for w in ['no amerita', 'n/a', 'na', 'niega', 'deslinde', 'no se'])
        
        # Si no hubo negativa en hospital, o si se especifica un hospital real
        if hosp and not es_negativa:
            registros_traslados_directos.append({
                'tipo_registro': 'Formato FRAP Oficial',
                'msg_id': r['id'],
                'fecha_hora': dt,
                'unidad': unidad if unidad else 'Ambulancia Operativa',
                'paciente': nom if nom else 'No aportó nombre',
                'edad': edad if edad else 'No especificada',
                'motivo_diagnostico': dx if dx else 'Atención prehospitalaria',
                'descripcion': desc.strip().replace('\n', ' ') if desc else '',
                'destino': hosp,
                'lugar_origen': dir_serv if dir_serv else 'Medellín de Bravo'
            })
        elif es_negativa:
            # Caso valorado en sitio sin traslado
            pass

    # 2. Formato breve tipo parte médico (Paciente: ... Dx: ... Hospital / Traslado)
    elif ('paciente:' in text_low or 'px:' in text_low) and any(w in text_low for w in ['traslad', 'hospital', 'clínica', 'imss', 'boca del río']):
        # Verificar si no dice "no amerita traslado"
        if not any(w in text_low for w in ['no amerita traslado', 'no ameritó traslado', 'se niega al traslado', 'niega traslado']):
            m_nom = re.search(r'(?:paciente|px)[:\s]+([^\.\n,]+)', text, re.IGNORECASE)
            m_dx = re.search(r'(?:dx|diagnóstico)[:\s]+([^\.\n]+)', text, re.IGNORECASE)
            
            # Buscar hospital
            hosp = "Centro Hospitalario"
            if 'boca del río' in text_low or 'boca del rio' in text_low or 'hgbv' in text_low:
                hosp = "Hospital General de Boca del Río"
            elif '71' in text_low:
                hosp = "IMSS Clínica 71 (Díaz Mirón)"
            elif '61' in text_low or 'cuauhtémoc' in text_low:
                hosp = "IMSS Clínica 61 / Cuauhtémoc"
            elif 'regional' in text_low:
                hosp = "Hospital Regional de Alta Especialidad"
            elif 'cruz roja' in text_low:
                hosp = "Cruz Roja Díaz Mirón"
            elif 'hosnaver' in text_low or 'naval' in text_low:
                hosp = "Hospital Naval (HOSNAVER)"
            elif 'pediátrica' in text_low or 'pediatrica' in text_low:
                hosp = "Torre Pediátrica de Veracruz"
                
            m_u = re.search(r'(?:unidad|u)[ _-]?([0-9]{3})', text_low)
            unidad = f"U-{m_u.group(1)}" if m_u else "Ambulancia de Guardia"
            
            registros_traslados_directos.append({
                'tipo_registro': 'Parte Médico Breve',
                'msg_id': r['id'],
                'fecha_hora': dt,
                'unidad': unidad,
                'paciente': m_nom.group(1).strip() if m_nom else "Paciente registrado en guardia",
                'edad': "No especificada",
                'motivo_diagnostico': m_dx.group(1).strip() if m_dx else "Auxilio prehospitalario",
                'descripcion': text[:120].replace('\n', ' '),
                'destino': hosp,
                'lugar_origen': 'Medellín de Bravo'
            })

    # 3. Reportes de despacho operativo de traslado (ej. "Unidad 208 comienza traslado de la clínica 71 al hospital de María")
    elif any(w in text_low for w in ['inicia traslado', 'comienza traslado', 'traslada a', 'traslado programado', 'traslado autorizado']):
        if not any(w in text_low for w in ['no amerita', 'sin traslado', 'no requiere']):
            # Extraer unidad
            m_u = re.search(r'(?:unidad|u)[ _-]?([0-9]{3})', text_low)
            unidad = f"U-{m_u.group(1)}" if m_u else "Ambulancia de Guardia"
            
            # Extraer paciente si viene
            m_nom = re.search(r'(?:traslado autorizado|traslada a|paciente)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,3})', text)
            paciente = m_nom.group(1).strip() if m_nom else ("Masculino" if 'masculino' in text_low else ("Femenina" if 'femenina' in text_low else "Paciente no especificado nominalmente"))
            
            # Extraer destino
            hosp = "Centro Hospitalario"
            if 'hospital de maría' in text_low or 'd\'maría' in text_low or 'd maria' in text_low:
                hosp = "Hospital D'María"
            elif 'boca del río' in text_low or 'boca del rio' in text_low or 'hgbv' in text_low:
                hosp = "Hospital General de Boca del Río"
            elif '71' in text_low:
                hosp = "IMSS Clínica 71 (Díaz Mirón)"
            elif '61' in text_low:
                hosp = "IMSS Clínica 61"
            elif 'cuauhtémoc' in text_low:
                hosp = "IMSS Cuauhtémoc"
            elif 'domicilio' in text_low or 'casa' in text_low:
                hosp = "Traslado a Domicilio (Alta Hospitalaria)"
            elif 'regional' in text_low:
                hosp = "Hospital Regional de Alta Especialidad"
                
            registros_traslados_directos.append({
                'tipo_registro': 'Despacho Operativo / Cabina',
                'msg_id': r['id'],
                'fecha_hora': dt,
                'unidad': unidad,
                'paciente': paciente,
                'edad': "No especificada",
                'motivo_diagnostico': "Traslado interhospitalario / urgencia médica",
                'descripcion': text[:120].replace('\n', ' '),
                'destino': hosp,
                'lugar_origen': 'Medellín de Bravo'
            })

conn.close()

df_exact = pd.DataFrame(registros_traslados_directos)
print(f"\nTotal registros de traslados exactos identificados: {len(df_exact)}")
print("\nDesglose por tipo de registro:")
print(df_exact['tipo_registro'].value_counts())

print("\nDesglose por Hospital Destino:")
print(df_exact['destino'].value_counts())

print("\n--- PRIMEROS 25 REGISTROS EXACTOS ---")
for i, r in df_exact.head(25).iterrows():
    print(f"[{i+1}] {r['fecha_hora']} | Unidad: {r['unidad']} | Tipo: {r['tipo_registro']}")
    print(f"    Paciente: {r['paciente']} (Edad: {r['edad']})")
    print(f"    Motivo/Dx: {r['motivo_diagnostico']}")
    print(f"    Destino: {r['destino']}")
    print(f"    Origen: {r['lugar_origen']}")
    print(f"    Texto: {r['descripcion'][:80]}...")
    print("-" * 70)
