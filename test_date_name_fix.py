import re
from datetime import datetime

def normalizar_fecha(f_rep, f_msg):
    if not f_rep and f_msg:
        f_rep = str(f_msg).split(' ')[0]
    f_rep = str(f_rep).strip()
    
    # Si ya viene como YYYY-MM-DD
    m_iso = re.match(r'^(20\d{2})[-/](\d{1,2})[-/](\d{1,2})', f_rep)
    if m_iso:
        y, m, d = m_iso.groups()
        return f"{y}-{int(m):02d}-{int(d):02d}"
        
    # Si viene como DD/MM/YYYY o DD/MM/YY
    m_lat = re.match(r'^(\d{1,2})[-/](\d{1,2})[-/](20\d{2}|\d{2})', f_rep)
    if m_lat:
        d, m, y = m_lat.groups()
        if len(y) == 2: y = f"20{y}"
        return f"{y}-{int(m):02d}-{int(d):02d}"
        
    if f_msg:
        return str(f_msg).split(' ')[0]
    return f_rep

def limpiar_nombre_paciente(nombre):
    if not nombre: return ""
    n = nombre.strip()
    n_l = n.lower()
    
    # Palabras que indican que no es un nombre propio
    palabras_invalidas = [
        'inconveniente', 'a base', 'que ', 'se traslada', 'en el ', 'para ', 'por ',
        'apoyo', 'tercera edad', 'recomienda', 'estable', 'consciente', 'orientado',
        'femenina', 'masculino', 'px', 'paciente', 'solicita', 'reporte'
    ]
    for p in palabras_invalidas:
        if n_l.startswith(p):
            return ""
            
    # Si tiene menos de 4 caracteres o no tiene espacios
    partes = n.split()
    if len(partes) < 2 and len(n) < 6:
        return ""
        
    # Debe contener al menos dos palabras con mayúscula o longitud razonable
    return n.title()

print("Pruebas de fecha:")
print("2026-06-11 ->", normalizar_fecha("2026-06-11", "2026-06-11 14:19"))
print("20/09/2026 ->", normalizar_fecha("20/09/2026", "2026-09-20 23:49"))
print("20/09/26 ->", normalizar_fecha("20/09/26", "2026-09-20 23:49"))

print("\nPruebas de nombres:")
print("inconveniente en ->", repr(limpiar_nombre_paciente("inconveniente en")))
print("a base a pedir el apoyo ->", repr(limpiar_nombre_paciente("a base a pedir el apoyo")))
print("francisco gutierrez villanueva ->", repr(limpiar_nombre_paciente("francisco gutierrez villanueva")))
print("Jose Antonio Acosta Murillo ->", repr(limpiar_nombre_paciente("Jose Antonio Acosta Murillo")))
