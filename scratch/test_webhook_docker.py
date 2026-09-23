import subprocess

script = """
docker exec evolution_api_local curl -s -X POST http://172.17.0.1:8000/api/whatsapp/webhook/ -H "Content-Type: application/json" -d '{"ping": true}'
"""

res = subprocess.run([
    'ssh', '-n',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    'root@107.170.59.223',
    script.strip()
], capture_output=True, text=True, encoding='utf-8')

print("WEBHOOK TEST FROM DOCKER:\n", res.stdout)
