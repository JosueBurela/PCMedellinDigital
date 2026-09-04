import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from portal.models import CursoCapacitacion
# Buscar el curso que tiene 'Primeros Auxilios 4 Septiembre' o similar
cursos = CursoCapacitacion.objects.filter(titulo__icontains='Primeros Auxilios 4 Septiembre')
for c in cursos:
    c.titulo = 'Primeros Auxilios'
    c.save()
    print('Renombrado el curso ID:', c.id)
