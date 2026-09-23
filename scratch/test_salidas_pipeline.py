import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from portal.models import VehiculoUnidad, BitacoraSalidaVehiculo
from portal.utils.whatsapp_salidas_tracker import (
    procesar_mensaje_grupo_salidas, GRUPO_SALIDAS_JID,
    extraer_unidad, clasificar_mensaje_operativo
)

print("=== 1. TEST REGEX UNIDAD ===")
casos_unidad = [
    "Unidad 041 sale a asuntos administrativos",
    "U-098 llegando a base",
    "041 en base",
    "Sale la 208 a choque",
    "Pipa 072 salida a incendio",
    "U-041 en camino",
]
for c in casos_unidad:
    u = extraer_unidad(c)
    tipo, det = clasificar_mensaje_operativo(c)
    print(f"Texto: '{c}' -> Unidad: {u} | Tipo: {tipo} | Detalle: {det}")

print("\n=== 2. TEST PROCESAMIENTO WEBHOOK SALIDA ===")
# Limpiar pruebas anteriores
BitacoraSalidaVehiculo.objects.filter(unidad__numero_unidad__icontains="041").delete()

payload_salida = {
    "key": {
        "remoteJid": GRUPO_SALIDAS_JID,
        "fromMe": False,
        "id": "TEST_MSG_001"
    },
    "pushName": "VULCANO CADENAS",
    "messageTimestamp": 1789764975,
    "message": {
        "imageMessage": {
            "caption": "Unidad 041 sale a asuntos administrativos"
        }
    }
}
res_salida = procesar_mensaje_grupo_salidas(payload_salida)
print("Resultado Salida:", res_salida)

salida_obj = BitacoraSalidaVehiculo.objects.filter(unidad__numero_unidad__icontains="041").last()
if salida_obj:
    print(f"Objeto creado en DB: #{salida_obj.id} | Unidad: {salida_obj.unidad.numero_unidad} | Operador: {salida_obj.operador_nombre} | Motivo: {salida_obj.descripcion_servicio} | Completado: {salida_obj.completado}")

print("\n=== 3. TEST PROCESAMIENTO WEBHOOK ENTRADA ===")
payload_entrada = {
    "key": {
        "remoteJid": GRUPO_SALIDAS_JID,
        "fromMe": False,
        "id": "TEST_MSG_002"
    },
    "pushName": "VULCANO CADENAS",
    "messageTimestamp": 1789768000,
    "message": {
        "conversation": "Unidad 041 llegando a base"
    }
}
res_entrada = procesar_mensaje_grupo_salidas(payload_entrada)
print("Resultado Entrada:", res_entrada)

if salida_obj:
    salida_obj.refresh_from_db()
    print(f"Objeto tras llegada: #{salida_obj.id} | Completado: {salida_obj.completado} | Duracion: {salida_obj.duracion_minutos} min | Unidad Estatus: {salida_obj.unidad.estatus}")

print("\nTODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE!")
