import subprocess

res = subprocess.run([
    'ssh', '-n',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    'root@107.170.59.223',
    'docker exec postgres_local psql -U postgres -d evolution -t -c "SELECT count(*) FROM \\"Message\\";"'
], capture_output=True, text=True, encoding='utf-8')

print("COUNT:", res.stdout.strip())
