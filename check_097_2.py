import os
import django
import sys

sys.path.insert(0, '/var/www/pcivildigital')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from portal.models import BitacoraSalidaVehiculo
for s in BitacoraSalidaVehiculo.objects.filter(unidad__numero_unidad='097').order_by('-fecha_salida')[:5]:
    print("ID:", s.id, "COMPLETADO:", s.completado)
    print("DESC:", repr(s.descripcion_servicio))
