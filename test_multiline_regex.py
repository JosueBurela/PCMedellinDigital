import pandas as pd
import re

df = pd.read_excel('Catalogo_Traslados_Medellin_2026.xlsx')

def extraer_multilinea(patron_nombre, texto):
    # Permite dos puntos opcionales, asteriscos opcionales, salto de línea opcional y espacios
    pat = rf'\*?{patron_nombre}\*?[:\s]*\n?\s*([^\n\r\*]+)'
    m = re.search(pat, texto, re.IGNORECASE)
    if m:
        v = m.group(1).strip()
        v = re.sub(r'^\*+|\*+$', '', v).strip()
        if v and v.lower() not in ['n/a', 'na', 'ninguno']:
            return v
    return ""

print("Probando en filas 31, 32, 35, 36:")
for idx in [31, 32, 35, 36]:
    txt = df.loc[idx, 'Texto_Original']
    pac = extraer_multilinea(r'NOMBRE\s*DEL\s*PACIENTE', txt)
    dx = extraer_multilinea(r'DIAGN[OÓ]STICO', txt)
    hosp = extraer_multilinea(r'HOSPITAL\s*(?:DE\s*TRASLADO)?', txt)
    amb = extraer_multilinea(r'AMBULANCIA', txt)
    op = extraer_multilinea(r'OPERADOR', txt)
    pm = extraer_multilinea(r'PARAM[EÉ]DICO', txt)
    print(f"Fila {idx} -> Amb: {amb} | Px: {pac} | Dx: {dx} | Hosp: {hosp} | Op: {op} | PM: {pm}")
