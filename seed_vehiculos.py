import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from portal.models import VehiculoUnidad

unidades = [
    {"numero_unidad": "208", "nombre_identificador": "Ambulancia 208", "tipo_vehiculo": "Ambulancia", "placas": "AMB-208-VER", "odometro_actual": 261446, "nivel_gasolina_actual": "3/4"},
    {"numero_unidad": "072", "nombre_identificador": "Pipa de Agua 072", "tipo_vehiculo": "Pipa", "placas": "PIP-072-VER", "odometro_actual": 185200, "nivel_gasolina_actual": "Lleno"},
    {"numero_unidad": "096", "nombre_identificador": "Pick Up Operativa 096", "tipo_vehiculo": "PickUp", "placas": "PK-096-VER", "odometro_actual": 142100, "nivel_gasolina_actual": "1/2"},
    {"numero_unidad": "104", "nombre_identificador": "Unidad de Rescate 104", "tipo_vehiculo": "Rescate", "placas": "RES-104-VER", "odometro_actual": 98400, "nivel_gasolina_actual": "Lleno"},
]

for u in unidades:
    VehiculoUnidad.objects.get_or_create(numero_unidad=u["numero_unidad"], defaults=u)

print("Flotilla inicial sembrada con exito en el servidor!")
