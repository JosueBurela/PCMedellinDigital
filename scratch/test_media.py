import subprocess

script = """
curl -s -X POST http://localhost:8080/chat/getBase64FromMediaMessage/PCMedellin \
  -H "Content-Type: application/json" \
  -H "apikey: MedellinPCSecretToken2026" \
  -d '{
    "message": {
      "key": {
        "id": "AC4F9C1ECCF3B2139E43A052FEC067C2",
        "remoteJid": "120363042493725288@g.us",
        "fromMe": false
      }
    },
    "convertToMp4": false
  }' | head -c 200
"""

res = subprocess.run([
    'ssh', '-n',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    'root@107.170.59.223',
    script.strip()
], capture_output=True, text=True, encoding='utf-8')

print("MEDIA BASE64:\n", res.stdout)
