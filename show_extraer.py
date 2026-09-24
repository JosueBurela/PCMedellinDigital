import re

def extraer_unidad(texto):
    patron = r'\b(?:unidad|u-?|movil|pipa|moto)?\s*(041|047|072|073|096|097|098|208)\b'
    match = re.search(patron, texto, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

print(extraer_unidad("Sale unidad 041 al palacio por tema administrativo"))
