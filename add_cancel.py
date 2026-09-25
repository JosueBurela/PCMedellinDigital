# -*- coding: utf-8 -*-
import re

with open('portal/utils/whatsapp_salidas_tracker.py', 'r', encoding='utf-8') as f:
    code = f.read()

new_engine = """def clasificar_mensaje_operativo(texto_original):
    texto = re.sub(r'[^\\w\\s-]', '', texto_original).lower()
    
    # 1. ACUSES DE RECIBO (Ignorar cualquier otra palabra)
    if re.search(r'\\b(enterad[oa]|ent|nt|recibid[oa]|rcb|copiad[oa]|copia|qsl|10[-\\s]?4|pendiente)\\b', texto):
        return 'NOVEDAD'
        
    # 2. CANCELACIONES / FALSA ALARMA (Cierra la bitacora de inmediato)
    if re.search(r'\\b(falsa alarma|cancelad[oa]|se cancela|negativo)\\b', texto):
        return 'ENTRADA'
        
    # 3. REPORTES DE ESTATUS EN CAMINO (No son salidas nuevas ni llegadas a base)
    if re.search(r'\\b(retorna|retorno|retornando|regresa|regresando|regresamos)\\b', texto) or \\
       re.search(r'\\b(llegando|arribando|en el|al|llegamos).*?(punto|lugar|hospital|siniestro|servicio|emergencia|imss|issste|regional|cruz roja|clinica)\\b', texto) or \\
       re.search(r'\\b(traslad[oa]|trasladando|trasladamos)\\b', texto):
        return 'NOVEDAD'
        
    # 4. LLEGADA DEFINITIVA A BASE (Cierra la bitacora)
    if re.search(r'\\b(en base|ya en base|estacionad[oa]|10[-\\s]?8)\\b', texto) or \\
       re.search(r'\\b(llega|llegada|llegando|arribando|arribo|entra|entrando).*?(base|central|estacion|cuartel)\\b', texto) or \\
       re.search(r'\\b(base|central).*?(sin novedad)\\b', texto) or \\
       re.search(r'\\b(concluy(?:e|endo|o)|concluida|concluido|finaliza|finalizado)\\b', texto):
        return 'ENTRADA'
        
    # 5. SALIDA / INICIO DE SERVICIO (Abre bitacora)
    if re.search(r'\\b(sale|salida|saliendo|salimos)\\b', texto) or \\
       re.search(r'\\b(procede|procediendo|dirige|dirigiendo|avanza|avanzando|avanzo|aproxima|aproximando)\\b', texto) or \\
       re.search(r'\\b(rumbo|en camino|despacho)\\b', texto):
        return 'SALIDA'
        
    return 'NOVEDAD'"""

match = re.search(r'def clasificar_mensaje_operativo\(texto_original\):.*?return \'NOVEDAD\'', code, flags=re.DOTALL)
if match:
    code = code.replace(match.group(0), new_engine)
    with open('portal/utils/whatsapp_salidas_tracker.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Success")
else:
    print("Failed")
