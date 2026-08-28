from django.core.management.base import BaseCommand
from portal.models import InscripcionCapacitacion

class Command(BaseCommand):
    help = "Corrige el nombre de Bruno Rguez a Rodriguez"

    def handle(self, *args, **options):
        inscripciones = InscripcionCapacitacion.objects.filter(nombre_completo__icontains="BRUNO RGUEZ")
        for i in inscripciones:
            old_name = i.nombre_completo
            i.nombre_completo = "Bruno Rodriguez Parola"
            i.save(update_fields=['nombre_completo'])
            self.stdout.write(f"Actualizado Folio {i.folio_constancia}: de {old_name} a {i.nombre_completo}")
        self.stdout.write(self.style.SUCCESS("Nombres corregidos exitosamente."))
