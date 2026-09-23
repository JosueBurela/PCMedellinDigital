import pandas as pd
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

df_agosto = pd.read_csv('reporte_mensual_agosto_limpio.csv')
print(f"Total casos en reporte_mensual_agosto_limpio: {len(df_agosto)}")

# Funciones de extracción
def extract_field_from_text(text, patterns):
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            val = re.sub(r'^\*+|\*+$', '', val).strip()
            if val:
                return val
    return None

traslados_extraidos = []

for idx, row in df_agosto.iterrows():
    caso_id = row['ID_Caso']
    fecha = row['Fecha_Reporte']
    hora_ini = row['Hora_Inicio']
    hora_fin = row['Hora_Fin']
    categoria = row['Categoria']
    text = str(row['Transcripcion_Incidente'])
    text_low = text.lower()
    
    # Evaluar si el caso involucra un traslado
    # 1. ¿Tiene formato FRAP clínico?
    es_frap = ('NOMBRE DEL PACIENTE' in text) or ('DIAGNÓSTICO' in text and 'HOSPITAL' in text)
    
    # 2. ¿Menciona traslado en el texto?
    menciona_traslado = any(w in text_low for w in ['traslado', 'traslada', 'trasladando', 'trasladaron', 'se traslada'])
    
    # 3. Excluir si hubo negativa explícita y no hubo otro traslado
    negativa = bool(re.search(r'(no requiere traslado|no amerita traslado|no ameritó traslado|sin traslado|se niega al traslado|niega traslado|firma deslinde|firma negativa|trasladaron.*por sus medios)', text_low))
    
    # Si no es FRAP y no menciona traslado, continuar
    if not es_frap and not menciona_traslado and not ('hospital' in text_low and 'unidad' in text_low):
        continue

    # Extraer campos si tiene formato FRAP
    nombre = extract_field_from_text(text, [r'\*NOMBRE DEL PACIENTE\*[:\s]*([^\n\*]+)', r'NOMBRE DEL PACIENTE[:\s]*([^\n\*]+)'])
    edad = extract_field_from_text(text, [r'\*EDAD\*[:\s]*([^\n\*]+)', r'EDAD[:\s]*([^\n\*]+)'])
    diagnostico = extract_field_from_text(text, [r'\*DIAGN[ÓO]STICO\*[:\s]*([^\n\*]+)', r'DIAGN[ÓO]STICO[:\s]*([^\n\*]+)'])
    motivo = extract_field_from_text(text, [r'\*DESCRIPCI[ÓO]N DE LO OCURRIDO\*[:\s]*([^\*]+?)(?=\*[A-Z]|\Z)', r'DESCRIPCI[ÓO]N DE LO OCURRIDO[:\s]*([^\*]+?)(?=\*[A-Z]|\Z)'])
    hospital = extract_field_from_text(text, [r'\*HOSPITAL DE TRASLADO\*[:\s]*([^\n\*]+)', r'HOSPITAL DE TRASLADO[:\s]*([^\n\*]+)'])
    ambulancia = extract_field_from_text(text, [r'\*AMBULANCIA\*[:\s]*([^\n\*]+)', r'AMBULANCIA[:\s]*([^\n\*]+)'])
    direccion = extract_field_from_text(text, [r'\*DIRECCI[ÓO]N DEL SERVICIO\*[:\s]*([^\n\*]+)', r'DIRECCI[ÓO]N DEL SERVICIO[:\s]*([^\n\*]+)'])
    
    # Si no tiene FRAP pero menciona traslado en texto informal
    # Ejemplos: "se traslada a femenina al hospital 20 de noviembre", "traslado de la clinica 71 al hospital de María",
    # "se traslada a la cruz roja", "traslado autorizado Edna Delfinada Montiel"
    
    # Intentar extraer nombre si no vino en FRAP
    if not nombre:
        # Buscar patrones como "paciente: [Nombre]", "ciudadano: [Nombre]", "traslado autorizado [Nombre]"
        m_nom = re.search(r'(?:paciente|px|ciudadano|ciudadana|femenina|masculino|traslado autorizado)[:\s]+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,3})', text)
        if m_nom:
            nombre = m_nom.group(1).strip()
        elif 'masculino' in text_low:
            nombre = "Paciente Masculino (No especificado en cabina)"
        elif 'femenina' in text_low:
            nombre = "Paciente Femenina (No especificado en cabina)"
            
    # Intentar extraer unidad si no vino en FRAP
    if not ambulancia:
        u_match = re.findall(r'(?:unidad|u)[ _-]?([0-9]{3})', text_low)
        if u_match:
            ambulancia = "U-" + u_match[0]
        else:
            ambulancia = "Ambulancia de Guardia"
            
    # Intentar extraer destino si no vino en FRAP
    if not hospital:
        # Buscar hospitales
        if any(w in text_low for w in ['general de boca', 'hg boca', 'hgbv', 'hospital de boca']):
            hospital = "Hospital General de Boca del Río"
        elif any(w in text_low for w in ['clínica 71', 'clinica 71', 'imss 71', '71 de días mirón', '71 de dias miron']):
            hospital = "IMSS Clínica 71 (Díaz Mirón)"
        elif any(w in text_low for w in ['clínica 61', 'clinica 61', 'imss 61', 'cuauhtémoc', 'cuauhtemoc']):
            hospital = "IMSS Clínica 61 / Cuauhtémoc"
        elif any(w in text_low for w in ['regional', 'alta especialidad']):
            hospital = "Hospital Regional de Alta Especialidad de Veracruz"
        elif any(w in text_low for w in ['torre pediátrica', 'torre pediatrica']):
            hospital = "Torre Pediátrica de Veracruz"
        elif any(w in text_low for w in ['hosnaver', 'hospital naval']):
            hospital = "Hospital Naval (HOSNAVER)"
        elif any(w in text_low for w in ['cruz roja']):
            hospital = "Cruz Roja Díaz Mirón"
        elif any(w in text_low for w in ['d\'maría', 'hospital de maría', 'd maria', 'd\'maria']):
            hospital = "Hospital D'María"
        elif any(w in text_low for w in ['domicilio', 'casa', 'a su domicilio']):
            hospital = "Traslado Asistido a Domicilio (Alta Hospitalaria)"
            
    # Intentar extraer diagnóstico o motivo si no vino en FRAP
    if not motivo and not diagnostico:
        # Buscar qué ocurrió
        m_dx = re.search(r'(?:dx|diagnóstico)[:\s]*([^\.\n\|]+)', text, re.IGNORECASE)
        if m_dx:
            diagnostico = m_dx.group(1).strip()
        else:
            # Detectar causa general
            if any(w in text_low for w in ['derrape', 'moto', 'motocicleta']):
                diagnostico = "Accidente / Derrape de Motocicleta"
            elif any(w in text_low for w in ['caída', 'caida', 'andamio', 'escalera']):
                diagnostico = "Traumatismo por caída de altura / nivel"
            elif any(w in text_low for w in ['choque', 'atropellad', 'volcadura']):
                diagnostico = "Accidente Vehicular / Atropellamiento"
            elif any(w in text_low for w in ['convulsión', 'convulsion', 'desmay', 'inconsciente']):
                diagnostico = "Crisis Convulsiva / Pérdida de Conocimiento"
            elif any(w in text_low for w in ['hipertens', 'presión', 'presion', 'ansiedad', 'infarto', 'iam']):
                diagnostico = "Urgencia Médica Clínica / Crisis Hipertensiva"
            elif any(w in text_low for w in ['parto', 'embaraz']):
                diagnostico = "Urgencia Obstétrica / Labor de Parto"
            else:
                diagnostico = "Enfermedad General / Traslado Clínico Programado"
                
    # Determinar si realmente se trasladó o si fue negativa
    # Si el hospital es 'no amerita', 'n/a' y hay negativa explícita:
    fue_trasladado = True
    if hospital and any(w in hospital.lower() for w in ['no amerita', 'n/a', 'na', 'niega', 'deslinde']):
        fue_trasladado = False
    elif negativa and not any(w in text_low for w in ['inicia traslado', 'comienza traslado', 'se traslada', 'fue trasladado', 'sale u.*a traslado']):
        fue_trasladado = False
        
    if fue_trasladado and (hospital or 'traslad' in text_low):
        traslados_extraidos.append({
            'caso_id': caso_id,
            'fecha': fecha,
            'hora': hora_ini,
            'unidad': ambulancia,
            'paciente': nombre if nombre else "Paciente no registrado nominalmente",
            'edad': edad if edad else "No especificada",
            'motivo_diagnostico': diagnostico if diagnostico else (motivo[:100] if motivo else "Atención prehospitalaria"),
            'descripcion_detallada': motivo.strip().replace('\n', ' ') if motivo else "",
            'destino': hospital if hospital else "Centro Hospitalario (Conurbación)",
            'direccion_origen': direccion if direccion else "Municipio de Medellín de Bravo",
            'fuente': 'FRAP' if es_frap else 'Bitácora Operativa'
        })

df_res = pd.DataFrame(traslados_extraidos)
print(f"Total traslados exactos identificados: {len(df_res)}")
print("\nPrimeros 20 registros con nombre, motivo, destino y hora:")
for i, r in df_res.head(20).iterrows():
    print(f"[{r['caso_id']}] {r['fecha']} {r['hora']} | {r['unidad']}")
    print(f"  Paciente: {r['paciente']} (Edad: {r['edad']})")
    print(f"  Motivo/Dx: {r['motivo_diagnostico']}")
    print(f"  Destino: {r['destino']}")
    print(f"  Origen: {r['direccion_origen']}")
    print("-" * 60)
