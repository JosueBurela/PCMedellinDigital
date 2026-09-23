import os
import django
import sys

sys.path.insert(0, '/var/www/pcivildigital')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from portal.models import BitacoraSalidaVehiculo
print("LIDs remaining:", BitacoraSalidaVehiculo.objects.filter(operador_telefono__icontains='@lid').count())
