import os
import django
import sys
import urllib.request
import json

sys.path.insert(0, '/var/www/pcivildigital')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from portal.models import BitacoraSalidaVehiculo
from portal.utils.whatsapp_utils import EVOLUTION_API_URL, EVOLUTION_API_KEY, INSTANCE_NAME
from portal.utils.whatsapp_salidas_tracker import GRUPO_SALIDAS_JID

def fix_lids():
    url = f"{EVOLUTION_API_URL}/group/findGroupInfos/{INSTANCE_NAME}?groupJid={GRUPO_SALIDAS_JID}"
    headers = {"apikey": EVOLUTION_API_KEY}
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            participants = data.get("participants", [])
            lid_to_phone = {}
            for p in participants:
                lid = p.get("id")
                phone = p.get("phoneNumber")
                if lid and phone:
                    lid_to_phone[lid] = phone
                    
            # Fix existing records
            salidas = BitacoraSalidaVehiculo.objects.filter(operador_telefono__icontains='@lid')
            count = 0
            for s in salidas:
                if s.operador_telefono in lid_to_phone:
                    s.operador_telefono = lid_to_phone[s.operador_telefono]
                    s.save()
                    count += 1
            print(f"Fixed {count} records.")
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    fix_lids()
