import subprocess

script = """
cat << 'EOF' > /var/www/pcivildigital/test_pages.py
import json, urllib.request, datetime

url = "http://localhost:8080/chat/findMessages/PCMedellin"
headers = {"Content-Type": "application/json", "apikey": "MedellinPCSecretToken2026"}

for page in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
    payload = {
        "where": {"key": {"remoteJid": "120363042493725288@g.us"}},
        "page": page,
        "limit": 50
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        records = data.get("messages", {}).get("records", [])
        if not records:
            break
        ts_primero = records[0].get("messageTimestamp", 0)
        ts_ultimo = records[-1].get("messageTimestamp", 0)
        dt_primero = datetime.datetime.fromtimestamp(ts_primero, tz=datetime.timezone.utc)
        dt_ultimo = datetime.datetime.fromtimestamp(ts_ultimo, tz=datetime.timezone.utc)
        print(f"Página {page}: {len(records)} msgs | De: {dt_primero.strftime('%d/%m/%Y %H:%M')} a: {dt_ultimo.strftime('%d/%m/%Y %H:%M')}")
EOF
cd /var/www/pcivildigital && ./venv/bin/python test_pages.py
"""

res = subprocess.run([
    'ssh', '-n',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    'root@107.170.59.223',
    script.strip()
], capture_output=True, text=True, encoding='utf-8')

print("PAGES:\n", res.stdout)
