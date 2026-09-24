import django
import os
import sys

sys.path.insert(0, '/var/www/pcivildigital')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from portal.models import VehiculoUnidad

v = VehiculoUnidad.objects.filter(numero_unidad='041').first()
print("Vehiculo 041:", v)
if v:
    print("ID:", v.id)
