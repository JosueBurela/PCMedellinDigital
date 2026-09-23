import os
import django
import sys

sys.path.insert(0, '/var/www/pcivildigital')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from portal.models import BitacoraSalidaVehiculo

total = BitacoraSalidaVehiculo.objects.count()
cortesias = BitacoraSalidaVehiculo.objects.filter(descripcion_servicio__icontains='sin salida').count()

print(f"Total salidas: {total}")
print(f"Salidas de cortesia: {cortesias}")
