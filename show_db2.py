import django
import os
import sys

sys.path.insert(0, 'c:/Users/burel/OneDrive/Documentos/PCivil Digital')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from portal.models import BitacoraSalidaVehiculo

print("Bitacoras for 041 today:")
for b in BitacoraSalidaVehiculo.objects.filter(unidad__numero_unidad='041').order_by('-fecha_salida')[:5]:
    print("ID:", b.id)
    print(b.descripcion_servicio)
    print("---")
