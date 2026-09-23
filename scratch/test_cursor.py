import subprocess

script = """
curl -s -X POST http://localhost:8080/chat/findMessages/PCMedellin \
  -H "Content-Type: application/json" \
  -H "apikey: MedellinPCSecretToken2026" \
  -d '{
    "where": {
      "key": {
        "remoteJid": "120363042493725288@g.us"
      },
      "messageTimestamp": {
        "lt": 1789760000
      }
    }
  }' | head -c 500
"""

res = subprocess.run([
    'ssh', '-n',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    'root@107.170.59.223',
    script.strip()
], capture_output=True, text=True, encoding='utf-8')

print("CURSOR TEST RESULT:\n", res.stdout[:300].encode('ascii', 'replace').decode('ascii'))
