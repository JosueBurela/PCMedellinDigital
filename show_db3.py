import django
import os
import sys

sys.path.insert(0, '/var/www/pcivildigital')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from portal.utils.whatsapp_salidas_tracker import clasificar_mensaje_operativo

texto = "Sale unidad 041 al palacio por tema administrativo"
res = clasificar_mensaje_operativo(texto)
print("Classification:", res)
