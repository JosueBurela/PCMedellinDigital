# -*- coding: utf-8 -*-
import re

with open('portal/utils/whatsapp_salidas_tracker.py', 'r', encoding='utf-8') as f:
    code = f.read()

new_function = """DICCIONARIO_PESOS = {
    'SALIDA': [
        (r'\\b(sale|salida|saliendo|salimos)\\b', 60),
        (r'\\b(procede|procediendo|dirige|dirigiendo|avanza|avanzando|avanzo|aproxima|aproximando)\\b', 50),
        (r'\\b(rumbo|en camino|despacho)\\b', 40),
        (r'\\b(traslada|trasladamos|trasladando|traslado)\\b', 50),
        (r'\\b(atender|apoyo|servicio|punto|emergencia|encomienda)\\b', 30),
    ],
    'ENTRADA': [
        (r'\\b(llega|llegada|llegando|llegamos|arribando|arribo)\\b', 50),
        (r'\\b(entra|entrada|entrando)\\b', 40),
        (r'\\b(retorna|retorno|retornando)\\b', 50),
        (r'\\b(base|central|estacion)\\b', 35),
        (r'\\b(10[-\\s]?8)\\b', 80),
        (r'\\b(concluy(?:e|endo|o)|concluida|concluido|finaliza|finalizado)\\b', 50),
        (r'\\b(sin novedad)\\b', 30),
    ],
    'CONFIRMACION': [
        (r'\\b(enterado|enterada|ent|nt)\\b', 70),
        (r'\\b(recibido|recibida|rcb)\\b', 70),
        (r'\\b(copiado|copia)\\b', 70),
        (r'\\b(qsl)\\b', 80),
        (r'\\b(pendiente)\\b', 50),
        (r'\\b(ok|okey)\\b', 40),
        (r'\\b(10[-\\s]?4)\\b', 80),
    ]
}

def clasificar_mensaje_operativo(texto_original):
    # normalizacion
    texto = re.sub(r'[^\\w\\s-]', '', texto_original).lower()
    
    puntajes = {'SALIDA': 0, 'ENTRADA': 0, 'CONFIRMACION': 0}
    
    # Evaluar el modelo predictivo heuristico basado en pesos
    for categoria, reglas in DICCIONARIO_PESOS.items():
        for patron, peso in reglas:
            if re.search(patron, texto):
                puntajes[categoria] += peso
                
    max_puntaje = 0
    ganador = 'NOVEDAD'
    
    for cat, pts in puntajes.items():
        if pts > max_puntaje:
            max_puntaje = pts
            ganador = cat
            
    # Umbral de confianza
    if max_puntaje < 35:
        ganador = 'NOVEDAD'
        
    if ganador == 'CONFIRMACION':
        return 'NOVEDAD'
        
    return ganador"""

import sys
match = re.search(r'def clasificar_mensaje_operativo\(texto_original\):.*?return \'NOVEDAD\'', code, flags=re.DOTALL)
if match:
    old_func = match.group(0)
    code = code.replace(old_func, new_function)
    with open('portal/utils/whatsapp_salidas_tracker.py', 'w', encoding='utf-8') as f:
        f.write(code)
else:
    print("Function not found!")
    sys.exit(1)
