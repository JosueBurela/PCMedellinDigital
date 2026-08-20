import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth.hashers import make_password
from portal.models import UsuarioOperadorVehiculo

admin_user, created = UsuarioOperadorVehiculo.objects.get_or_create(
    nombre_completo='ADMINISTRADOR GENERAL',
    defaults={
        'password_hash': make_password('admin'),
        'rol': 'ADMIN',
        'estado': 'APROBADO'
    }
)

print('ADMINISTRADOR GENERAL creado en produccion:', created)
