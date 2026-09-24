import django
import os
import sys

sys.path.insert(0, '/var/www/pcivildigital')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from portal.models import BitacoraSalidaVehiculo

print("Bitacoras for 047:")
for b in BitacoraSalidaVehiculo.objects.filter(unidad__numero_unidad='047').order_by('-fecha_salida')[:5]:
    print("ID:", b.id)
    print("Operador:", b.operador_nombre, b.operador_telefono)
    print(b.descripcion_servicio)
    print("---")
