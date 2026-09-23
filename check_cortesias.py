import os
import django
import sys

sys.path.insert(0, '/var/www/pcivildigital')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from portal.models import BitacoraSalidaVehiculo

cortesias = BitacoraSalidaVehiculo.objects.filter(descripcion_servicio__icontains='sin salida').order_by('-fecha_salida')[:5]

for c in cortesias:
    print(f"[{c.fecha_salida}] Unidad {c.unidad.numero_unidad} por {c.operador_nombre}")
