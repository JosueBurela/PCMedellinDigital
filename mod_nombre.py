# -*- coding: utf-8 -*-
# Actualizar Quintero por Quintal en el generador
with open("generar_acta_motosierras.py", "r", encoding="utf-8") as f:
    code = f.read()

code_mod = code.replace("Mariano Molina Quintero", "Mariano Molina Quintal")
code_mod = code_mod.replace("Quintero", "Quintal")

with open("generar_acta_motosierras.py", "w", encoding="utf-8") as f:
    f.write(code_mod)

print("Script actualizado con Mariano Molina Quintal.")
