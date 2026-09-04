import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from portal.models import Trabajador
from django.contrib.auth.hashers import make_password

# Le damos permisos a todos
Trabajador.objects.update(rol_vehicular='ADMIN')

# Si no hay nadie, creamos uno de prueba
if not Trabajador.objects.exists():
    Trabajador.objects.create(nombre='ADMIN', password=make_password('1234'), rol_vehicular='ADMIN')
