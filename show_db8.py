import django
import os
import sys

sys.path.insert(0, '/var/www/pcivildigital')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from portal.models import VehiculoUnidad
for v in VehiculoUnidad.objects.all():
    print(v.numero_unidad)
