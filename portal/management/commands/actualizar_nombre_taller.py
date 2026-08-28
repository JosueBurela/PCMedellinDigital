from django.core.management.base import BaseCommand
from portal.models import CursoCapacitacion

class Command(BaseCommand):
    help = "Actualiza el titulo del curso a Primeros Auxilios"

    def handle(self, *args, **options):
        cursos = CursoCapacitacion.objects.filter(titulo__icontains="Primeros Auxilios")
        for c in cursos:
            c.titulo = "Primeros Auxilios"
            c.save(update_fields=['titulo'])
            self.stdout.write(f"Actualizado ID {c.id}: {c.titulo}")
        self.stdout.write(self.style.SUCCESS("Titulo actualizado a Primeros Auxilios exitosamente."))
