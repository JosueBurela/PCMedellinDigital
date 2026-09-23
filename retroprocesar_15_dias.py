import os
import django
import sys
import time
import psycopg2
import json

sys.path.insert(0, '/var/www/pcivildigital')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from portal.utils.whatsapp_salidas_tracker import procesar_mensaje_grupo_salidas, GRUPO_SALIDAS_JID

def procesar():
    from portal.models import BitacoraSalidaVehiculo
    print("Limpiando bitacora de los ultimos 15 dias para re-ingestar limpio...")
    timestamp_15_dias = int(time.time()) - (86400 * 15)
    
    import datetime
    from django.utils import timezone
    dt_15_dias = timezone.localtime(datetime.datetime.fromtimestamp(timestamp_15_dias, tz=datetime.timezone.utc))
    BitacoraSalidaVehiculo.objects.filter(fecha_salida__gte=dt_15_dias).delete()
    print("Bitacora borrada.")

    conn = psycopg2.connect('postgresql://postgres:postgres@127.0.0.1:5432/evolution')
    cur = conn.cursor()
    
    cur.execute(f'''
        SELECT "messageTimestamp", "pushName", "keyId", "participant", "message"
        FROM "Message"
        WHERE "messageTimestamp" >= {timestamp_15_dias}
        ORDER BY "messageTimestamp" ASC
    ''')
    
    filas = cur.fetchall()
    print(f"Total mensajes en los ultimos 15 dias: {len(filas)}")
    
    procesados = 0
    ignorados = 0
    
    for row in filas:
        timestamp, push_name, key_id, participant, message_json = row
        
        if isinstance(message_json, str):
            try:
                message_dict = json.loads(message_json)
            except Exception:
                continue
        else:
            message_dict = message_json
            
        data = {
            "key": {
                "remoteJid": GRUPO_SALIDAS_JID,
                "id": key_id,
                "participant": participant
            },
            "pushName": push_name,
            "messageTimestamp": timestamp,
            "message": message_dict
        }
        
        res = procesar_mensaje_grupo_salidas(data)
        if res.get("status") in ["salida_creada", "salida_updated", "salida_updated_taken_over", "entrada_registrada", "entrada_sin_salida_registrada", "novedad_anexada"]:
            procesados += 1
        else:
            ignorados += 1
            
    print(f"Mensajes operativos procesados: {procesados}")
    print(f"Mensajes ordinarios ignorados: {ignorados}")

if __name__ == '__main__':
    procesar()
