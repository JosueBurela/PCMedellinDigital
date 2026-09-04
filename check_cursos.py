import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from portal.models import CursoCapacitacion
for c in CursoCapacitacion.objects.all():
    print(c.id, c.titulo)
