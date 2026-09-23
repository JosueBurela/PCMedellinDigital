import subprocess

script = """
docker exec postgres_local psql -U postgres -d postgres -c "CREATE DATABASE evolution;"
docker exec postgres_local psql -U postgres -d postgres -c "ALTER USER postgres WITH PASSWORD 'postgres';"
docker restart evolution_api_local
sleep 4
docker ps
"""

res = subprocess.run([
    'ssh', '-n',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    'root@107.170.59.223',
    script.strip()
], capture_output=True, text=True, encoding='utf-8')

print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
