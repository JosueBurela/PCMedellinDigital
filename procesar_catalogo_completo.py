import pandas as pd
import re
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

df_orig = pd.read_excel('Catalogo_Traslados_Medellin_2026.xlsx')
print(f"Cargadas {len(df_orig)} filas del catálogo original.")

# Mapeo de nombres conocidos de operadores y paramédicos por teléfono / remitente de WhatsApp
MAPA_REMITENTES = {
    '128733256110143': 'Oficialía / Guardia PC',
    '28067678416994': 'TUM Paramédico PC',
    '233453719150672': 'Paramédico Jorge Luna / U-208',
    '60314259308792': 'Paramédico Rut Sánchez / U-098',
    '244006101479643': 'Operador PC Medellín',
    '43465723384010': 'Paramédico PC Medellín',
    '170188213383234': 'Operador Unidad 096',
    '198930738487413': 'Personal Operativo PC',
    '72104464666678': 'Operador Carlos Peña / U-208',
    '214482211094536': 'Base / Despacho PC',
    '226585563119766': 'Operador PC',
    '44367045730369': 'Operador PC',
    '194171226824727': 'Operador PC',
    '65915584544854': 'Operador PC',
}

def limpiar_campo(val):
    if pd.isna(val) or val is None:
        return ""
    val_str = str(val).strip()
    val_str = re.sub(r'^\*+|\*+$', '', val_str).strip()
    if val_str.lower() in ['nan', 'none', 'n/a', 'na', 'null', 'negado', 'negada', 'niega']:
        if val_str.lower() in ['negado', 'negada', 'niega']:
            return "Negado"
        return ""
    return val_str

registros_procesados = []

for idx, row in df_orig.iterrows():
    texto = str(row.get('Texto_Original', ''))
    t_lower = texto.lower()
    
    # 1. FECHA Y HORA
    f_msg = str(row.get('Fecha_Mensaje', ''))
    f_rep = limpiar_campo(row.get('Fecha_Reporte'))
    h_rep = limpiar_campo(row.get('Hora'))
    
    # Intentar extraer del texto si no hay
    if not f_rep and f_msg:
        f_rep = f_msg.split(' ')[0]
    if not h_rep and f_msg:
        h_rep = f_msg.split(' ')[1] if ' ' in f_msg else ""
        
    # 2. UNIDAD QUE ATIENDE
    unidad = limpiar_campo(row.get('Unidad'))
    if not unidad:
        m_u = re.search(r'(unidad\s*097|unidad\s*098|unidad\s*208|unidad\s*096|unidad\s*047|unidad\s*072|unidad\s*073|unidad\s*041|u-097|u-098|u-208|u-096|u-047|u-072|u072|o96|096|097|098|208|m[oó]vil\s*096|m[oó]vil\s*097|m[oó]vil\s*098|m[oó]vil\s*208|ambulancia)', t_lower)
        if m_u:
            u_str = m_u.group(1).upper()
            if '097' in u_str: unidad = 'Unidad 097 (Ambulancia)'
            elif '098' in u_str: unidad = 'Unidad 098 (Ambulancia)'
            elif '208' in u_str: unidad = 'Unidad 208 (Ambulancia)'
            elif '096' in u_str or 'O96' in u_str: unidad = 'Unidad 096 (Rescate/Apoyo)'
            elif '047' in u_str: unidad = 'Unidad 047'
            elif '072' in u_str: unidad = 'Unidad 072'
            elif '073' in u_str: unidad = 'Unidad 073'
            elif '041' in u_str: unidad = 'Unidad 041'
            elif 'ambulancia' in u_str: unidad = 'Ambulancia PC'
        else:
            unidad = "Guardia PC Medellín"
    else:
        # Estandarizar nombre de unidad
        u_upper = unidad.upper()
        if '097' in u_upper: unidad = 'Unidad 097 (Ambulancia)'
        elif '098' in u_upper: unidad = 'Unidad 098 (Ambulancia)'
        elif '208' in u_upper: unidad = 'Unidad 208 (Ambulancia)'
        elif '096' in u_upper: unidad = 'Unidad 096 (Rescate/Apoyo)'
        elif '047' in u_upper: unidad = 'Unidad 047'
        elif '072' in u_upper: unidad = 'Unidad 072'
        elif '073' in u_upper: unidad = 'Unidad 073'

    # 3. PERSONAL QUE REALIZÓ EL TRASLADO / ATENCIÓN
    operador = limpiar_campo(row.get('Operador'))
    paramedico = limpiar_campo(row.get('Paramédico'))
    tercero = limpiar_campo(row.get('Tercero_Abordo'))
    
    # Extraer si viene en el texto
    if not operador:
        m_op = re.search(r'operador\s*:\s*([^\n\r\*]+)', texto, re.IGNORECASE)
        if m_op: operador = m_op.group(1).strip()
    if not paramedico:
        m_pm = re.search(r'param[eé]dico\s*:\s*([^\n\r\*]+)', texto, re.IGNORECASE)
        if m_pm: paramedico = m_pm.group(1).strip()

    # Construir campo consolidado de Personal a Cargo
    personal_list = []
    if paramedico: personal_list.append(f"Paramédico: {paramedico}")
    if operador: personal_list.append(f"Operador: {operador}")
    if tercero: personal_list.append(f"3ro: {tercero}")
    
    remitente_wa = str(row.get('Remitente_WhatsApp', ''))
    rem_nombre = MAPA_REMITENTES.get(remitente_wa, f"ID {remitente_wa[:6]}...")
    if not personal_list:
        personal_cargo = f"Reportado por {rem_nombre}"
    else:
        personal_cargo = " / ".join(personal_list)

    # 4. NOMBRE DEL PACIENTE / PERSONA TRASLADADA
    paciente = limpiar_campo(row.get('Nombre_Paciente'))
    if not paciente:
        # Buscar variantes informales
        m_p1 = re.search(r'(?:se atiende al joven\s*:?|se atiende a masculino\s*:?|se atiende a femenina\s*:?|se atiende a paciente\s*:?|px\s*:?|paciente\s*:?)\s*([A-Za-zÁÉÍÓÚáéíóúñÑ\s]+?)(?:\s+\d+\s*a[ñn]os|\s+de\s+\d+|\s+edad|\s+dx|\s+padece|\s+presenta|\s+noruega|\s+circuito|\n|\r|$)', texto, re.IGNORECASE)
        if m_p1:
            p_cand = m_p1.group(1).strip()
            if len(p_cand) > 3 and not p_cand.lower().startswith('femenina') and not p_cand.lower().startswith('masculino'):
                paciente = p_cand
        if not paciente:
            # Buscar formato "Nombre Apellido, XX años"
            m_p2 = re.search(r'^([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,3}),?\s+(\d{1,2})\s*a[ñn]os', texto, re.MULTILINE)
            if m_p2:
                paciente = m_p2.group(1).strip()

    # Si sigue sin nombre pero es un reporte de atención, describirlo
    if not paciente:
        if 'traslado de una persona de la tercera edad' in t_lower:
            paciente = "Persona de la tercera edad (No especificado)"
        elif 'paciente inconveniente' in t_lower:
            paciente = "Persona reportada inconveniente"
        elif 'atender reporte de ciudadanos' in t_lower:
            paciente = "Reporte ciudadano en vía pública"
        elif 'fuga de gas' in t_lower:
            paciente = "Servicio de Bomberos (Fuga de gas)"
        elif 'quema' in t_lower or 'incendio' in t_lower:
            paciente = "Servicio de Bomberos (Control de incendio)"
        elif 'panal' in t_lower:
            paciente = "Servicio de Rescate (Retiro de panal)"
        elif 'gasolina' in t_lower:
            paciente = "Carga de Combustible"
        elif 'apoyo de agua' in t_lower or 'riego' in t_lower:
            paciente = "Apoyo social con pipa de agua"
        else:
            paciente = "Atención médica prehospitalaria"

    # 5. EDAD
    edad = limpiar_campo(row.get('Edad'))
    if not edad:
        m_e = re.search(r'(\d{1,2})\s*a[ñn]os', texto, re.IGNORECASE)
        if m_e:
            edad = f"{m_e.group(1)} años"

    # 6. DIAGNÓSTICO / MOTIVO
    diagnostico = limpiar_campo(row.get('Diagnóstico_Motivo'))
    if not diagnostico:
        m_dx = re.search(r'(?:dx\s*:?|diagn[oó]stico\s*:?|padecimiento\s*:?|motivo\s*:?)\s*([^\n\r\*]+)', texto, re.IGNORECASE)
        if m_dx:
            diagnostico = m_dx.group(1).strip()
        elif 'hipoglucemia' in t_lower: diagnostico = "Cuadro de Hipoglucemia"
        elif 'epilexia' in t_lower or 'epilepsia' in t_lower: diagnostico = "Crisis epiléptica"
        elif 'columna' in t_lower: diagnostico = "Problemas de columna / Dificultad motriz"
        elif 'disnea' in t_lower or 'dificultad respiratoria' in t_lower: diagnostico = "Dificultad respiratoria / Disnea"
        elif 'hipertens' in t_lower: diagnostico = "Crisis hipertensiva"
        elif 'policontundido' in t_lower: diagnostico = "Paciente policontundido"
        elif 'fractura' in t_lower: diagnostico = "Probable fractura"
        elif 'accidente' in t_lower or 'choque' in t_lower: diagnostico = "Accidente vehicular"
        elif 'parto' in t_lower: diagnostico = "Trabajo de parto"
        elif 'traslado programado' in t_lower: diagnostico = "Traslado programado / Cita médica"
        elif 'gasolina' in t_lower: diagnostico = "Abastecimiento de combustible"
        elif 'fuga de gas' in t_lower: diagnostico = "Fuga de gas LP"
        elif 'panal' in t_lower: diagnostico = "Retiro de enjambre de avispas/abejas"
        else:
            diagnostico = "Valoración y primeros auxilios"

    # 7. HOSPITAL DE TRASLADO Y ESTATUS
    hospital = limpiar_campo(row.get('Hospital_Destino'))
    estatus_orig = str(row.get('Estatus_Traslado', ''))
    
    if not hospital:
        m_h = re.search(r'(?:hospital(?:\s+de\s+traslado)?\s*:?|traslado\s+a\s*:?|trasladado\s+a\s*:?|se traslada a\s*:?)\s*([^\n\r\*]+)', texto, re.IGNORECASE)
        if m_h:
            h_cand = m_h.group(1).strip()
            if h_cand.lower() not in ['n/a', 'na', 'ninguno', 'no ameritó', 'no']:
                hospital = h_cand
        elif 'haev' in t_lower or 'regional' in t_lower: hospital = "Hospital Regional de Alta Especialidad (HAEV)"
        elif '20 de noviembre' in t_lower: hospital = "Hospital General 20 de Noviembre"
        elif 'issste' in t_lower: hospital = "Clínica Hospital ISSSTE"
        elif 'imss' in t_lower: hospital = "Hospital General de Zona IMSS"
        elif 'boca del río' in t_lower or 'boca del rio' in t_lower: hospital = "Hospital General de Boca del Río"

    # Estatus del Traslado normalizado
    h_l = (hospital or '').lower()
    if 'se niega' in h_l or 'niega traslado' in t_lower or 'se niega' in t_lower:
        estatus = "Negativa de Traslado (Firma Deslinde)"
        hospital = "No aplica (Se rehúsa)"
    elif 'no ameritó' in h_l or 'no amerito' in h_l or 'no amerita' in t_lower or 'no ameritó traslado' in t_lower:
        estatus = "No Ameritó Traslado (Estabilizado)"
        hospital = "Atención en Sitio"
    elif hospital and hospital not in ["Atención en Sitio", "No aplica (Se rehúsa)"]:
        estatus = "Traslado Efectivo a Hospital"
    elif 'traslado' in t_lower and ('domicilio' in t_lower or 'alta' in t_lower):
        estatus = "Traslado de Alta a Domicilio"
        hospital = "Domicilio del Paciente"
    elif 'traslado programado' in t_lower:
        estatus = "Traslado Programado"
        if not hospital: hospital = "Unidad Médica / Hospital"
    else:
        estatus = "Atención en Sitio"
        if not hospital: hospital = "Atención en Sitio"

    # 8. DIRECCIÓN / UBICACIÓN
    direccion = limpiar_campo(row.get('Dirección'))
    if not direccion:
        m_dir = re.search(r'(?:direcci[oó]n(?:\s+del\s+servicio)?\s*:?|domicilio\s*:?|ubicaci[oó]n\s*:?)\s*([^\n\r\*]+)', texto, re.IGNORECASE)
        if m_dir:
            direccion = m_dir.group(1).strip()
        elif 'puente moreno' in t_lower: direccion = "Fracc. Lagos de Puente Moreno"
        elif 'el tejar' in t_lower: direccion = "Localidad El Tejar"
        elif 'playa de vacas' in t_lower: direccion = "Localidad Playa de Vacas"
        elif 'moralillo' in t_lower: direccion = "Localidad El Moralillo"
        elif 'heron proal' in t_lower or 'herón proal' in t_lower: direccion = "Colonia Herón Proal"
        elif 'arboledas' in t_lower: direccion = "Fracc. Arboledas San Ramón"
        else:
            direccion = "Municipio de Medellín de Bravo"

    # 9. MÉDICO QUE RECIBE Y CÓDIGO
    recibe = limpiar_campo(row.get('Médico_Recibe'))
    codigo = limpiar_campo(row.get('Código_Prioridad'))
    if not codigo:
        if 'código rojo' in t_lower or 'codigo rojo' in t_lower or 'rojo' in t_lower: codigo = "Rojo (Prioridad Alta)"
        elif 'código amarillo' in t_lower or 'codigo amarillo' in t_lower or 'amarillo' in t_lower: codigo = "Amarillo (Moderado)"
        elif 'código verde' in t_lower or 'codigo verde' in t_lower or 'verde' in t_lower: codigo = "Verde (Estable)"
        else: codigo = "Verde (Estable)"

    registros_procesados.append({
        'No_Folio': idx + 1,
        'Fecha': f_rep,
        'Hora': h_rep,
        'Unidad_Atiende': unidad,
        'Estatus_Traslado': estatus,
        'Persona_Trasladada_Paciente': paciente,
        'Edad': edad or "N/D",
        'Diagnostico_Motivo': diagnostico,
        'Hospital_Destino': hospital,
        'Personal_Que_Realizo_Traslado': personal_cargo,
        'Direccion_Ubicacion': direccion,
        'Medico_Recibe': recibe or "Personal de Guardia",
        'Codigo_Triage': codigo,
        'Resumen_Operativo': texto[:250].replace('\n', ' ')
    })

df_final = pd.DataFrame(registros_procesados)
print("\n--- RESULTADO DE PARSEO Y LIMPIEZA DE LAS 258 FILAS ---")
print(f"Total registros: {len(df_final)}")
print("\nConteo por Estatus de Traslado:")
print(df_final['Estatus_Traslado'].value_counts())
print("\nConteo por Unidad que Atiende:")
print(df_final['Unidad_Atiende'].value_counts())
print("\nMuestra de las primeras 5 filas limpias:")
print(df_final[['No_Folio', 'Fecha', 'Unidad_Atiende', 'Estatus_Traslado', 'Persona_Trasladada_Paciente', 'Hospital_Destino']].head(5).to_string())

# Guardar un archivo temporal para crear luego el diseño con openpyxl
df_final.to_csv('datos_limpios_catalogo.csv', index=False, encoding='utf-8-sig')
