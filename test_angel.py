# -*- coding: utf-8 -*-
import re

DICCIONARIO_PESOS = {
    'SALIDA': [
        (r'\b(sale|salida|saliendo|salimos)\b', 60),
        (r'\b(procede|procediendo|dirige|dirigiendo|avanza|avanzando|avanzo|aproxima|aproximando)\b', 50),
        (r'\b(rumbo|en camino|despacho)\b', 40),
        (r'\b(traslada|trasladamos|trasladando|traslado)\b', 50),
        (r'\b(atender|apoyo|servicio|punto|emergencia|encomienda)\b', 30),
    ],
    'ENTRADA': [
        (r'\b(llega|llegada|llegando|llegamos|arribando|arribo)\b', 50),
        (r'\b(entra|entrada|entrando)\b', 40),
        (r'\b(retorna|retorno|retornando)\b', 50),
        (r'\b(base|central|estacion)\b', 35),
        (r'\b(10[-\s]?8)\b', 80),
        (r'\b(concluy(?:e|endo|o)|concluida|concluido|finaliza|finalizado)\b', 50),
        (r'\b(sin novedad)\b', 30),
    ],
    'CONFIRMACION': [
        (r'\b(enterado|enterada|ent|nt)\b', 70),
        (r'\b(recibido|recibida|rcb)\b', 70),
        (r'\b(copiado|copia)\b', 70),
        (r'\b(qsl)\b', 80),
        (r'\b(pendiente)\b', 50),
        (r'\b(ok|okey)\b', 40),
        (r'\b(10[-\s]?4)\b', 80),
    ]
}

def clasificar(texto_original):
    texto = re.sub(r'[^\w\s-]', '', texto_original).lower()
    puntajes = {'SALIDA': 0, 'ENTRADA': 0, 'CONFIRMACION': 0}
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
            
    if max_puntaje < 35: ganador = 'NOVEDAD'
    if ganador == 'CONFIRMACION': return 'NOVEDAD', puntajes
    return ganador, puntajes

print(clasificar("Sale unidad 041 al palacio por tema administrativo"))
