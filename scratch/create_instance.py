import subprocess

script = """
curl -s -X POST http://localhost:8080/instance/create \
  -H "Content-Type: application/json" \
  -H "apikey: MedellinPCSecretToken2026" \
  -d '{
    "instanceName": "PCMedellin",
    "token": "MedellinPCSecretToken2026",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
  }'
"""

res = subprocess.run([
    'ssh', '-n',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    'root@107.170.59.223',
    script.strip()
], capture_output=True, text=True, encoding='utf-8')

print("CREATE INSTANCE RESULT:\n", res.stdout[:1500])
