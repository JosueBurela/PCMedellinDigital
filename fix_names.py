import os
import django
import sys
import re

sys.path.insert(0, '/var/www/pcivildigital')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from portal.models import BitacoraSalidaVehiculo

salidas = BitacoraSalidaVehiculo.objects.all()
count = 0
for s in salidas:
    # If the name is just a giant number, replace it with their phone number or 'Operador'
    if s.operador_nombre and re.fullmatch(r'\d{12,16}', s.operador_nombre):
        # Format the phone number from operador_telefono
        phone = s.operador_telefono.split('@')[0] if s.operador_telefono else "Desconocido"
        if phone.startswith('521'):
            phone = f"+52 {phone[3:5]} {phone[5:9]} {phone[9:]}"
        else:
            phone = f"+{phone}"
            
        # We don't have their name, so we just set it to their formatted phone number!
        s.operador_nombre = f"Operador ({phone})"
        s.save()
        count += 1

print(f"Fixed {count} names.")
