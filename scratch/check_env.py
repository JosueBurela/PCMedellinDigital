import subprocess

res = subprocess.run([
    'ssh', '-n',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    'root@107.170.59.223',
    'cat /var/www/pcivildigital/.env | grep -E "EVOLUTION|INSTANCE|WHATSAPP|GRUPO"'
], capture_output=True, text=True, encoding='utf-8')

print("ENV:\n", res.stdout)
