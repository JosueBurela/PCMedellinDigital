import subprocess

res_scp = subprocess.run([
    'scp',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    r'c:\Users\burel\OneDrive\Documentos\PCivil Digital\scratch\retroprocesar_salidas.py',
    'root@107.170.59.223:/var/www/pcivildigital/retroprocesar.py'
], capture_output=True, text=True, encoding='utf-8')

print("SCP RETURNCODE:", res_scp.returncode)
if res_scp.stderr:
    print("SCP STDERR:", res_scp.stderr)

# Ejecutar el script
res_run = subprocess.run([
    'ssh', '-n',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    'root@107.170.59.223',
    'cd /var/www/pcivildigital && ./venv/bin/python retroprocesar.py'
], capture_output=True, text=True, encoding='utf-8')

print("EXEC STDOUT:\n", res_run.stdout.encode('ascii', 'replace').decode('ascii'))
if res_run.stderr:
    print("EXEC STDERR:\n", res_run.stderr.encode('ascii', 'replace').decode('ascii'))
