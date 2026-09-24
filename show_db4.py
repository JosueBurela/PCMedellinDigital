import django
import os
import sys

sys.path.insert(0, '/var/www/pcivildigital')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from portal.utils.whatsapp_salidas_tracker import clasificar_mensaje_operativo, extraer_unidad, normalizar_texto
from portal.models import BitacoraSalidaVehiculo

texto = "Sale unidad 041 al palacio por tema administrativo"
print("Clasificacion:", clasificar_mensaje_operativo(texto))
print("Extraer unidad:", extraer_unidad(texto))
print("Normalizado:", re.sub(r'[^\w\s-]', '', texto).lower() if 're' in sys.modules else texto)

# Fetch from DB and check what the text actually is
b = BitacoraSalidaVehiculo.objects.get(id=2288)
print("DB text matches:", "041" in b.descripcion_servicio)
