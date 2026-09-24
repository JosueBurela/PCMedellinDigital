import sys
import os
import django

sys.path.insert(0, 'c:/Users/burel/OneDrive/Documentos/PCivil Digital')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from portal.utils.whatsapp_salidas_tracker import clasificar_mensaje_operativo

m1 = "Unidad 097 retorna a base"
m2 = "Unidad 097 en base"

print("m1:", m1, "->", clasificar_mensaje_operativo(m1))
print("m2:", m2, "->", clasificar_mensaje_operativo(m2))
