# ==============================================================================
#  🛡️ COMANDO OFICIAL PARA CREAR CREDENCIALES DE ADMINISTRADOR
# ==============================================================================

from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from portal.models import PersonalAdministrativo, UsuarioOperadorVehiculo

class Command(BaseCommand):
    help = 'Crea o actualiza las credenciales maestras de Administrador para todo el sistema.'

    def handle(self, *args, **options):
        # 1. Crear / Actualizar Administrador de Control de Vehículos
        for nombre_admin in ['ADMINISTRADOR GENERAL', 'ADMINISTRADOR', 'ADMIN']:
            user_veh, _ = UsuarioOperadorVehiculo.objects.get_or_create(
                nombre_completo=nombre_admin,
                defaults={
                    'rol': 'ADMIN',
                    'estado': 'APROBADO',
                    'password_hash': make_password('Medellin2026!')
                }
            )
            user_veh.rol = 'ADMIN'
            user_veh.estado = 'APROBADO'
            user_veh.password_hash = make_password('Medellin2026!')
            user_veh.save()

        # 2. Crear / Actualizar Administrador del Portal Principal (Django Superuser)
        admin_portal, created_portal = PersonalAdministrativo.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@medellindebravo.gob.mx',
                'is_staff': True,
                'is_superuser': True,
                'rol_nivel': 'SUPER',
                'area': 'PC'
            }
        )
        admin_portal.is_staff = True
        admin_portal.is_superuser = True
        admin_portal.rol_nivel = 'SUPER'
        admin_portal.set_password('Medellin2026!')
        admin_portal.save()

        self.stdout.write(self.style.SUCCESS("Credenciales de Administrador creadas/actualizadas con exito."))
