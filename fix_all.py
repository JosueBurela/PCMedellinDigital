import os
import django
import sys
import urllib.request
import json
import re

sys.path.insert(0, '/var/www/pcivildigital')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from portal.models import BitacoraSalidaVehiculo
from portal.utils.whatsapp_utils import EVOLUTION_API_URL, EVOLUTION_API_KEY, INSTANCE_NAME
from portal.utils.whatsapp_salidas_tracker import GRUPO_SALIDAS_JID

def fix_all():
    url = f"{EVOLUTION_API_URL}/group/findGroupInfos/{INSTANCE_NAME}?groupJid={GRUPO_SALIDAS_JID}"
    headers = {"apikey": EVOLUTION_API_KEY}
    
    req = urllib.request.Request(url, headers=headers)
    lid_to_phone = {}
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            for p in data.get("participants", []):
                lid = p.get("id")
                phone = p.get("phoneNumber")
                if lid and phone:
                    # Map both with and without @lid
                    lid_to_phone[lid] = phone
                    lid_to_phone[lid.split('@')[0]] = phone
    except Exception as e:
        print("Error fetching group:", e)
        return

    salidas = BitacoraSalidaVehiculo.objects.all()
    fixed_phones = 0
    fixed_names = 0
    
    for s in salidas:
        changed = False
        
        # Clean up operador_telefono
        old_tel = s.operador_telefono
        if old_tel:
            # If it's a raw LID number or a full LID string, convert to actual phone number
            if old_tel in lid_to_phone:
                s.operador_telefono = lid_to_phone[old_tel]
                changed = True
            elif old_tel.replace('@lid', '') in lid_to_phone:
                s.operador_telefono = lid_to_phone[old_tel.replace('@lid', '')]
                changed = True
                
        # Clean up operador_nombre
        if s.operador_nombre and ('Operador' in s.operador_nombre or re.fullmatch(r'\d+', s.operador_nombre) or 'lid' in s.operador_nombre):
            # Try to format the current phone
            phone = s.operador_telefono.split('@')[0] if s.operador_telefono else "Desconocido"
            if phone.startswith('521'):
                phone = f"+52 {phone[3:5]} {phone[5:9]} {phone[9:]}"
            else:
                phone = f"+{phone}"
            
            s.operador_nombre = f"Personal ({phone})"
            changed = True
            fixed_names += 1

        if changed:
            s.save()
            fixed_phones += 1

    print(f"Fixed {fixed_phones} records.")

if __name__ == '__main__':
    fix_all()
