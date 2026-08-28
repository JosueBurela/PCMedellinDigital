from django.core.management.base import BaseCommand
from django.utils import timezone
from portal.models import CursoCapacitacion, InscripcionCapacitacion
import unicodedata
import re

def slugify_simple(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '.', text)

class Command(BaseCommand):
    help = "Registra los 31 participantes del taller de Primeros Auxilios"

    def handle(self, *args, **options):
        # 1. Buscar o asegurar el curso de Primeros Auxilios
        curso = CursoCapacitacion.objects.filter(titulo__icontains="Primeros Auxilios").first()
        if not curso:
            curso = CursoCapacitacion.objects.create(
                titulo="Primeros Auxilios Básicos y RCP",
                descripcion="Taller práctico de primeros auxilios, soporte vital básico, control de hemorragias y RCP.",
                duracion_horas=8,
                fecha_inicio=timezone.now().date(),
                horario="09:00 a 14:00 hrs",
                sede_ubicacion="Estación Central de Bomberos El Tejar",
                cupo_maximo=50,
                activo=True
            )
            self.stdout.write(self.style.SUCCESS(f"Curso creado: {curso.titulo}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Curso encontrado: {curso.titulo} (ID: {curso.id})"))

        nombres_raw = [
            "Erika Amaya Castillo.",
            "Abril del Carmen Gtz. Reyes.",
            "Gloria Monserrath Lara Duran.",
            "Adalberto Torres Sosa.",
            "Alfonsa Galindo Sosa.",
            "Concepción Cruz Gómez.",
            "Daniel Alexo Pérez.",
            "Nallely Lara López.",
            "Nely Piedra Andrade.",
            "Daniela Gpe. Hdez Peña.",
            "Silvia Peña Ramírez.",
            "Walda Alejandra Dzib Reyes.",
            "Laura Herrera Martínez.",
            "Andy Bautista Ramírez.",
            "Roberto Carlos Rivera Villela.",
            "Elvira Melchor Lagunes.",
            "Bruno Rguez Parola.",
            "Luis Alfredo Lara Vela.",
            "Beatriz Cecilia Zamora.",
            "Yadira del Carmen Méndez Valencia.",
            "Veronica Pérez Vidaña.",
            "Julieta Irayt Contreras Palacio.",
            "Olga Pérez Vidaña.",
            "Yarani Montes Sánchez.",
            "Edilberto Mora Bravo.",
            "Mercedes Carabarin Morales.",
            "Nancy Arely Elizalde Montoya.",
            "Ma. José Carabarin Morales.",
            "Elvira Melchor Lagunes.",
            "Patricia Hernández Ramos.",
            "Brayan Nahum Nordy Hernández."
        ]

        total_creados = 0
        for idx, raw_nombre in enumerate(nombres_raw, start=1):
            nombre_limpio = raw_nombre.strip().rstrip('.').strip()
            slug_nom = slugify_simple(nombre_limpio)
            correo = f"{slug_nom}_{idx}@gmail.com"
            telefono = f"2299{idx:06d}"

            inscripcion = InscripcionCapacitacion.objects.create(
                curso=curso,
                nombre_completo=nombre_limpio,
                correo=correo,
                telefono=telefono,
                empresa_institucion="PARTICULAR",
                asistio=True,
                aprobado=True,
                fecha_emision=timezone.now()
            )
            total_creados += 1
            self.stdout.write(f"[{total_creados}/31] {inscripcion.nombre_completo} | Folio: {inscripcion.folio_constancia}")

        self.stdout.write(self.style.SUCCESS(f"Se registraron exitosamente los {total_creados} participantes con asistencia y aprobacion habilitada."))
