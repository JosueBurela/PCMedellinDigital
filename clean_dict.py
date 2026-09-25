# -*- coding: utf-8 -*-
import re

with open('portal/utils/whatsapp_salidas_tracker.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = re.sub(r'DICCIONARIO_PESOS = \{.*?\]\n\}', '', code, flags=re.DOTALL)

with open('portal/utils/whatsapp_salidas_tracker.py', 'w', encoding='utf-8') as f:
    f.write(code)
