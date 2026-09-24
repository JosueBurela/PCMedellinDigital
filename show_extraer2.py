import re

patron = r'\b(?:unidad|u-?|movil|pipa|moto)?\s*(041|047|072|073|096|097|098|208)\b'
texto = "Sale unidad 041 al palacio por tema administrativo"
match = re.search(patron, texto, re.IGNORECASE)
print("Match:", match.group(1) if match else "None")
