# -*- coding: utf-8 -*-
with open("generar_acta_motosierras.py", "r", encoding="utf-8") as f:
    code = f.read()

code_mod = code.replace("C. MARIANO MOLINA QUINTERO", "C. MARIANO MOLINA QUINTAL")
code_mod = code_mod.replace("MARIANO MOLINA QUINTERO", "MARIANO MOLINA QUINTAL")

with open("generar_acta_motosierras.py", "w", encoding="utf-8") as f:
    f.write(code_mod)

print("Actualizado en mayúsculas también.")
