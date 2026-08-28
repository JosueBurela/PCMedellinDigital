from django.core.management.base import BaseCommand
from portal.models import CursoCapacitacion

class Command(BaseCommand):
    help = "Actualiza el nombre del taller a Taller de Primeros Auxilios"

    def handle(self, *args, **options):
        cursos = CursoCapacitacion.objects.filter(titulo__icontains="Primeros Auxilios")
        for c in cursos:
            c.titulo = "Taller de Primeros Auxilios"
            c.save(update_fields=['titulo'])
            self.stdout.write(f"Actualizado ID {c.id}: {c.titulo}")
        self.stdout.write(self.style.SUCCESS("Nombre del taller actualizado exitosamente."))
