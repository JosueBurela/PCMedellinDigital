import subprocess

script = """
cd /var/www/pcivildigital
curl -s -X POST http://localhost:8080/chat/findMessages/PCMedellin \
  -H "Content-Type: application/json" \
  -H "apikey: MedellinPCSecretToken2026" \
  -d '{
    "where": {
      "key": {
        "remoteJid": "120363042493725288@g.us"
      }
    },
    "limit": 100
  }' | head -c 2500
"""

res = subprocess.run([
    'ssh', '-n',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    'root@107.170.59.223',
    script.strip()
], capture_output=True, text=True, encoding='utf-8')

print("MESSAGES HEAD:\n", res.stdout[:2000].encode('ascii', 'replace').decode('ascii'))
