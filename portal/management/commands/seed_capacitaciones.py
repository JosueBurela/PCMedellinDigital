# ==============================================================================
#  🎓 COMANDO PARA POBLAR CURSOS SEMILLA DE CAPACITACIÓN
# ==============================================================================

import datetime
from django.core.management.base import BaseCommand
from portal.models import CursoCapacitacion

class Command(BaseCommand):
    help = 'Crea los cursos de capacitación semilla para Protección Civil.'

    def handle(self, *args, **options):
        if CursoCapacitacion.objects.count() == 0:
            c1 = CursoCapacitacion.objects.create(
                titulo='Primeros Auxilios Básicos y RCP',
                descripcion='Capacitación teórico-práctica en reanimación cardiopulmonar, atragantamiento, vendajes y atención primaria de heridas.',
                duracion_horas=8,
                fecha_inicio=datetime.date.today() + datetime.timedelta(days=7),
                horario='09:00 a 13:00 hrs',
                sede_ubicacion='Estación Central de Bomberos El Tejar',
                cupo_maximo=50,
                activo=True
            )
            c2 = CursoCapacitacion.objects.create(
                titulo='Uso y Manejo Seguro de Extintores',
                descripcion='Identificación de clases de fuego (A, B, C), uso correcto de extintores de PQS y CO2 y protocolos de seguridad contra incendios.',
                duracion_horas=6,
                fecha_inicio=datetime.date.today() + datetime.timedelta(days=14),
                horario='10:00 a 14:00 hrs',
                sede_ubicacion='Auditorio Municipal de Medellín de Bravo',
                cupo_maximo=40,
                activo=True
            )
            c3 = CursoCapacitacion.objects.create(
                titulo='Evacuación e Incendios en Inmuebles y Comercios',
                descripcion='Formación de brigadas comunitarias y comerciales de evacuación, señalética, rutas de evacuación y zonas de seguridad.',
                duracion_horas=10,
                fecha_inicio=datetime.date.today() + datetime.timedelta(days=21),
                horario='09:00 a 14:00 hrs',
                sede_ubicacion='Estación Central de Bomberos El Tejar',
                cupo_maximo=60,
                activo=True
            )
            self.stdout.write(self.style.SUCCESS("Cursos de capacitacion creados con exito."))
        else:
            self.stdout.write("Cursos ya existentes.")
