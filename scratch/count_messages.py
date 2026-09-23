import subprocess

script = """
docker exec postgres_local psql -U postgres -d evolution -c "
SELECT count(*) FROM \\"Message\\";
"
"""

res = subprocess.run([
    'ssh', '-n',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    'root@107.170.59.223',
    script.strip()
], capture_output=True, text=True, encoding='utf-8')

print("TOTAL IN MESSAGE TABLE:\n", res.stdout)
