# -*- coding: utf-8 -*-
import re

def extraer_motivo(descripcion):
    lineas = descripcion.split('\n')
    mensajes_reales = []
    
    for linea in lineas:
        match = re.search(r'\[\d{2}:\d{2}\][^:]+:\s*(.*)', linea)
        if match:
            texto = match.group(1).strip()
            texto = re.sub(r'\[FOTO_URL:[^\]]+\]', '', texto).strip()
            if texto and texto != '[FOTO / IMAGEN]':
                mensajes_reales.append(texto.lower())
                
    if not mensajes_reales:
        return "Sin motivo de salida registrado"
        
    motivo_encontrado = ""
    patron_accion = r'\b(procede|sale|salimos|avanza|dirige|rumbo|traslado|traslada|apoyo|servicio de|atender|reportan|accidente|incendio|fuga)\b(.*)'
    
    for msg in mensajes_reales[:3]:
        match = re.search(patron_accion, msg)
        if match:
            resto = match.group(2).strip()
            palabra_clave = match.group(1).strip()
            
            resto = re.sub(r'\b(unidad|u-?|movil|moto)?\s*\d{2,3}\b', '', resto).strip()
            resto = re.sub(r'^(a|al|hacia|para|por)\s+', '', resto).strip()
            
            if len(resto) > 3:
                if palabra_clave in ['reportan', 'accidente', 'incendio', 'traslado', 'apoyo']:
                    motivo_encontrado = f"{palabra_clave.capitalize()} {resto}".strip()
                else:
                    motivo_encontrado = resto.capitalize()
                break
                
    if motivo_encontrado:
        return motivo_encontrado
    else:
        return "Sin motivo de salida registrado"

textos_prueba = [
    "[13:31] VULCANO: Troya 047 procede al batallon militar [FOTO_URL...]",
    "[14:07] Angel: Sale unidad 041 al palacio por tema administrativo",
    "[11:14] Juan: 047 procede al tejar a asuntos administrativos",
    "[13:10] Pedro: Unidad 208 sale al servicio",
    "[10:17] Maria: Sale unidad 096\n[10:30] Maria: Se procede a orillar un cable de puas",
    "[12:04] Jefe: Reportan accidente de vehiculos carretera paso del toro\n[12:05] Base: Enterado",
    "[08:00] Pedro: Sale 072 a xalapa",
    "[09:00] Pedro: Apoyo vial en el puente"
]

for t in textos_prueba:
    print(extraer_motivo(t))
