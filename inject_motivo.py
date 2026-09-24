# -*- coding: utf-8 -*-
import re

with open('portal/models.py', 'r', encoding='utf-8') as f:
    code = f.read()

new_property = """    @property
    def motivo_predictivo(self):
        import re
        if not self.descripcion_servicio: return "Sin motivo registrado"
        
        lineas = self.descripcion_servicio.split('\\n')
        mensajes = []
        for linea in lineas:
            match = re.search(r'\\[\\d{2}:\\d{2}\\][^:]+:\\s*(.*)', linea)
            if match:
                txt = match.group(1).strip()
                txt = re.sub(r'\\[FOTO_URL:.*?\\]', '', txt).strip()
                if txt and txt != '[FOTO / IMAGEN]' and not txt.startswith('[CORTES'):
                    mensajes.append(txt.lower())
        
        if not mensajes: return "Sin motivo registrado"
        
        patron = r'\\b(procede|sale|salimos|avanza|dirige|rumbo|traslado|traslada|apoyo|servicio|atender|reportan|accidente|incendio|fuga|enfermo|lesionado|caido|volcadura|choque)\\b(.*)'
        
        for msg in mensajes[:3]:
            match = re.search(patron, msg)
            if match:
                resto = match.group(2).strip()
                clave = match.group(1).strip()
                
                resto = re.sub(r'\\b(unidad|u-?|movil|moto|pipa)?\\s*\\d{2,3}\\b', '', resto).strip()
                resto = re.sub(r'^(a|al|hacia|para|por)\\s+', '', resto).strip()
                
                if len(resto) > 3:
                    if clave in ['reportan', 'accidente', 'incendio', 'traslado', 'apoyo', 'fuga', 'enfermo', 'lesionado', 'volcadura', 'choque', 'servicio']:
                        return f"{clave.capitalize()} {resto}".strip()
                    else:
                        return resto.capitalize()
                        
        return "Sin motivo especifico registrado"
"""

code = code.replace("    def __str__(self):\n        estado_str = \"FINALIZADO\" if self.completado else \"EN CURSO\"\n        return f\"{self.unidad.nombre_identificador} - {self.operador_nombre} ({estado_str})\"", "    def __str__(self):\n        estado_str = \"FINALIZADO\" if self.completado else \"EN CURSO\"\n        return f\"{self.unidad.nombre_identificador} - {self.operador_nombre} ({estado_str})\"\n\n" + new_property)

with open('portal/models.py', 'w', encoding='utf-8') as f:
    f.write(code)
