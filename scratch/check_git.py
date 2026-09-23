import subprocess

script = """
cd /var/www/pcivildigital
git fetch origin main
git log -n 3 --oneline
"""

res = subprocess.run([
    'ssh', '-n',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    'root@107.170.59.223',
    script.strip()
], capture_output=True, text=True, encoding='utf-8')

print("GIT LOG:\n", res.stdout.encode('ascii', 'replace').decode('ascii'))
