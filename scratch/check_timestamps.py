import subprocess
import json
import datetime

script = """
curl -s -X POST http://localhost:8080/chat/findMessages/PCMedellin \
  -H "Content-Type: application/json" \
  -H "apikey: MedellinPCSecretToken2026" \
  -d '{
    "where": {
      "key": {
        "remoteJid": "120363042493725288@g.us"
      }
    },
    "limit": 50
  }'
"""

res = subprocess.run([
    'ssh', '-n',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    'root@107.170.59.223',
    script.strip()
], capture_output=True, text=True, encoding='utf-8')

data = json.loads(res.stdout)
records = data.get("messages", {}).get("records", [])
print("TOTAL RECORDS:", len(records))
if records:
    timestamps = [r.get("messageTimestamp", 0) for r in records]
    min_ts = min(timestamps)
    max_ts = max(timestamps)
    print("MIN MSG (UTC):", datetime.datetime.fromtimestamp(min_ts, tz=datetime.timezone.utc))
    print("MAX MSG (UTC):", datetime.datetime.fromtimestamp(max_ts, tz=datetime.timezone.utc))
    for r in records[:5]:
        ts = r.get("messageTimestamp", 0)
        dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
        txt = r.get("message", {}).get("conversation") or r.get("message", {}).get("imageMessage", {}).get("caption") or "[MEDIA]"
        print(f"[{dt.strftime('%d/%m %H:%M')}] {r.get('pushName')}: {txt[:40]}")
