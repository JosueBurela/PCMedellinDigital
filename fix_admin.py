import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from portal.models import Trabajador
from django.contrib.auth.hashers import make_password

user, created = Trabajador.objects.get_or_create(nombre='ADMIN')
user.password = make_password('1234')
user.rol_vehicular = 'ADMIN'
user.is_active = True
user.save()
print("Usuario ADMIN creado/actualizado exitosamente.")
