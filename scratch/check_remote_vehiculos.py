import subprocess

script = """
cd /var/www/pcivildigital
./venv/bin/python -c "import django, os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup(); from portal.models import VehiculoUnidad; print([(v.numero_unidad, v.nombre_identificador, v.tipo_vehiculo) for v in VehiculoUnidad.objects.all()])"
"""

res = subprocess.run([
    'ssh', '-n',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    'root@107.170.59.223',
    script.strip()
], capture_output=True, text=True, encoding='utf-8')

print("REMOTE VEHICULOS:\n", res.stdout)
