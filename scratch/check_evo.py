import subprocess

res = subprocess.run([
    'ssh', '-n',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    'root@107.170.59.223',
    'docker logs evolution_api_local --tail 30'
], capture_output=True, text=True, encoding='utf-8')

print("STDOUT:\n", res.stdout.encode('ascii', 'replace').decode('ascii'))
