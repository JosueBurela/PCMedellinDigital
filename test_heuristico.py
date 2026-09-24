import re

DICCIONARIO_PESOS = {
    'SALIDA': [
        (r'\b(sale|salida|saliendo|salimos)\b', 60),
        (r'\b(procede|dirige|dirigiendo|avanza|avanzando|aproxima)\b', 50),
        (r'\b(rumbo|encomienda|despacho)\b', 40),
        (r'\b(traslada|trasladamos|traslado)\b', 50),
        (r'\b(atender|apoyo|servicio|punto)\b', 30),
    ],
    'ENTRADA': [
        (r'\b(llega|llegada|llegando|llegamos|arribando)\b', 50),
        (r'\b(entra|entrada|entrando)\b', 40),
        (r'\b(retorna|retorno|retornando)\b', 50),
        (r'\b(base|central|estacion)\b', 35),
        (r'\b(10[-\s]?8)\b', 80),
        (r'\b(concluy(?:e|endo|o)|concluida)\b', 50),
        (r'\b(sin novedad)\b', 30),
    ],
    'CONFIRMACION': [
        (r'\b(enterado|ent|nt)\b', 70),
        (r'\b(recibido)\b', 70),
        (r'\b(copiado|copia)\b', 70),
        (r'\b(qsl)\b', 80),
        (r'\b(pendiente)\b', 50),
        (r'\b(ok)\b', 40),
        (r'\b(10[-\s]?4)\b', 80),
    ]
}

def normalizar(texto):
    return re.sub(r'[^\w\s-]', '', texto).lower()

def modelo_predictivo(texto_original):
    texto = normalizar(texto_original)
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
            
    if max_puntaje < 35:
        ganador = 'NOVEDAD'
        
    return ganador, puntajes

mensajes_prueba = [
    "Troya 047 procede al batallon militar",
    "Enterado en base",
    "En base 047",
    "10-8",
    "QSL pendiente en central",
    "Unidad 072 avanza al servicio",
    "Llegando a la estacion sin novedad"
]

for m in mensajes_prueba:
    clas, pts = modelo_predictivo(m)
    print(f"'{m}' -> {clas} {pts}")
