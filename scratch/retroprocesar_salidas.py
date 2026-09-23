import os
import sys
import json
import urllib.request
import datetime
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from portal.models import VehiculoUnidad, BitacoraSalidaVehiculo
from portal.utils.whatsapp_salidas_tracker import procesar_mensaje_grupo_salidas, GRUPO_SALIDAS_JID
from portal.utils.whatsapp_utils import EVOLUTION_API_URL, EVOLUTION_API_KEY, INSTANCE_NAME

def retroprocesar():
    print("=== INICIANDO RETRO-PROCESAMIENTO COMPLETO DE AYER Y HOY ===")
    
    # Rango de tiempo: Desde ayer 17-Sep 00:00:01 hasta ahora
    hoy = timezone.localdate()
    ayer = hoy - datetime.timedelta(days=1)
    
    # 17 de Septiembre a las 00:00:01
    dt_inicio_ayer = timezone.make_aware(datetime.datetime.combine(ayer, datetime.time(0, 0, 1)))
    ts_inicio = int(dt_inicio_ayer.timestamp())
    
    print(f"Buscando mensajes desde: {dt_inicio_ayer} (Timestamp: {ts_inicio})...")

    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_API_KEY
    }
    
    todos_mensajes = []
    page = 1
    max_pages = 25
    
    while page <= max_pages:
        url = f"{EVOLUTION_API_URL}/chat/findMessages/{INSTANCE_NAME}?page={page}&limit=50"
        payload = {
            "where": {
              "key": {
                "remoteJid": GRUPO_SALIDAS_JID
              }
            }
        }
        
        req_data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=req_data, headers=headers, method='POST')
        
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                records = data.get("messages", {}).get("records", [])
                if not records:
                    print(f"Página {page}: 0 registros. Fin de paginación.")
                    break
                
                ts_primero = records[0].get("messageTimestamp", 0)
                ts_ultimo = records[-1].get("messageTimestamp", 0)
                dt_p = datetime.datetime.fromtimestamp(ts_primero, tz=datetime.timezone.utc)
                dt_u = datetime.datetime.fromtimestamp(ts_ultimo, tz=datetime.timezone.utc)
                print(f"Página {page}: {len(records)} msgs | De {dt_p.strftime('%d/%m %H:%M')} a {dt_u.strftime('%d/%m %H:%M')}")

                todos_mensajes.extend(records)
                
                # Si el último mensaje de la página ya es más antiguo que el inicio de ayer, ya terminamos
                if ts_ultimo < ts_inicio:
                    print(f"Se alcanzó el límite de fecha en página {page}.")
                    break
                    
                page += 1
        except Exception as e:
            print(f"Error al paginar página {page}: {e}")
            break

    print(f"\nTotal mensajes recuperados: {len(todos_mensajes)}")

    # Filtrar solo los mensajes que caigan dentro de Ayer y Hoy (>= ts_inicio)
    mensajes_ayer_y_hoy = [
        m for m in todos_mensajes 
        if m.get("messageTimestamp", 0) >= ts_inicio
    ]
    
    print(f"Mensajes correspondientes a Ayer y Hoy: {len(mensajes_ayer_y_hoy)}")

    # Ordenar cronológicamente (ASC) para procesar primero las salidas y luego las llegadas
    mensajes_ayer_y_hoy.sort(key=lambda x: x.get("messageTimestamp", 0))

    procesados_salida = 0
    procesados_entrada = 0
    ignorados = 0

    for msg in mensajes_ayer_y_hoy:
        ts = msg.get("messageTimestamp", 0)
        dt_msg = timezone.localtime(datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc))
        
        payload_adaptado = {
            "key": msg.get("key", {}),
            "pushName": msg.get("pushName", "") or "Personal Operativo",
            "messageTimestamp": ts,
            "message": msg.get("message", {}),
            "base64": msg.get("base64")
        }
        
        res = procesar_mensaje_grupo_salidas(payload_adaptado)
        status = res.get("status")
        
        if status in ["salida_creada", "salida_updated"]:
            procesados_salida += 1
            print(f"[{dt_msg.strftime('%d/%m %H:%M')}] SALIDA REGISTRADA: Unidad {res.get('unidad')} | Operador: {res.get('operador')}")
        elif status in ["entrada_registrada", "entrada_sin_salida_registrada"]:
            procesados_entrada += 1
            print(f"[{dt_msg.strftime('%d/%m %H:%M')}] LLEGADA REGISTRADA: Unidad {res.get('unidad')} | Duración: {res.get('duracion_min')} min")
        else:
            ignorados += 1

    print("\n=== RESUMEN DE RETRO-PROCESAMIENTO ===")
    print(f"Salidas creadas/actualizadas: {procesados_salida}")
    print(f"Llegadas a base registradas: {procesados_entrada}")
    print(f"Mensajes de chat común ignorados: {ignorados}")

    # Consultar cómo quedó la base de datos
    salidas_ayer = BitacoraSalidaVehiculo.objects.filter(fecha_salida__date=ayer).count()
    salidas_hoy = BitacoraSalidaVehiculo.objects.filter(fecha_salida__date=hoy).count()
    print(f"\nSalidas registradas en Base de Datos para Ayer ({ayer}): {salidas_ayer}")
    print(f"Salidas registradas en Base de Datos para Hoy ({hoy}): {salidas_hoy}")

if __name__ == '__main__':
    retroprocesar()
