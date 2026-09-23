import subprocess

script = """
curl -s -X POST http://localhost:8080/webhook/set/PCMedellin \
  -H "Content-Type: application/json" \
  -H "apikey: MedellinPCSecretToken2026" \
  -d '{
    "webhook": {
      "enabled": true,
      "url": "https://107-170-59-223.sslip.io/api/whatsapp/webhook/",
      "byEvents": false,
      "base64": true,
      "events": [
        "MESSAGES_UPSERT",
        "CONNECTION_UPDATE"
      ]
    }
  }'
"""

res = subprocess.run([
    'ssh', '-n',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    'root@107.170.59.223',
    script.strip()
], capture_output=True, text=True, encoding='utf-8')

print("SET WEBHOOK TO SSL:\n", res.stdout)
