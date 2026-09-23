import os
import django
import sys

sys.path.insert(0, '/var/www/pcivildigital')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from portal.models import BitacoraSalidaVehiculo

nombres = BitacoraSalidaVehiculo.objects.values_list('operador_nombre', flat=True).distinct()
for n in nombres:
    print(n)
