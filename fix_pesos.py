# -*- coding: utf-8 -*-
import re

with open('portal/utils/whatsapp_salidas_tracker.py', 'r', encoding='utf-8') as f:
    code = f.read()

new_dict = """DICCIONARIO_PESOS = {
    'SALIDA': [
        (r'\\b(sale|salida|saliendo|salimos)\\b', 60),
        (r'\\b(procede|procediendo|dirige|dirigiendo|avanza|avanzando|avanzo|aproxima|aproximando)\\b', 50),
        (r'\\b(rumbo|en camino|despacho)\\b', 40),
        (r'\\b(traslada|trasladamos|trasladando|traslado)\\b', 50),
        (r'\\b(atender|apoyo|servicio|punto|emergencia|encomienda)\\b', 30),
    ],
    'RETORNANDO': [
        (r'\\b(retorna|retorno|retornando|regresa|regresando|regresamos)\\b', 80),
        (r'\\b(rumbo a base|procede a base|dirige a base)\\b', 80),
    ],
    'ENTRADA': [
        (r'\\b(llega|llegada|llegando|llegamos|arribando|arribo)\\b', 50),
        (r'\\b(entra|entrada|entrando)\\b', 40),
        (r'\\b(en base|ya en base|estacionada|estacionado)\\b', 60),
        (r'\\b(base|central|estacion)\\b', 35),
        (r'\\b(10[-\\s]?8)\\b', 80),
        (r'\\b(concluy(?:e|endo|o)|concluida|concluido|finaliza|finalizado)\\b', 50),
        (r'\\b(sin novedad)\\b', 30),
    ],
    'CONFIRMACION': [
        (r'\\b(enterado|enterada|ent|nt)\\b', 100),
        (r'\\b(recibido|recibida|rcb)\\b', 100),
        (r'\\b(copiado|copia)\\b', 100),
        (r'\\b(qsl)\\b', 100),
        (r'\\b(pendiente)\\b', 100),
        (r'\\b(ok|okey)\\b', 40),
        (r'\\b(10[-\\s]?4)\\b', 100),
    ]
}"""

match = re.search(r'DICCIONARIO_PESOS = \{.*?\]\n\}', code, flags=re.DOTALL)
if match:
    old_dict = match.group(0)
    code = code.replace(old_dict, new_dict)
    with open('portal/utils/whatsapp_salidas_tracker.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Success")
else:
    print("Match not found")
