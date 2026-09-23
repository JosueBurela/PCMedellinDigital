import subprocess

script = """
docker exec evolution_api_local node -e 'fetch("https://107-170-59-223.sslip.io/api/whatsapp/webhook/", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({ping: true})}).then(r => r.json()).then(console.log).catch(console.error)'
"""

res = subprocess.run([
    'ssh', '-n',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    'root@107.170.59.223',
    script.strip()
], capture_output=True, text=True, encoding='utf-8')

print("NODE FETCH TO SSL DOMAIN:\n", res.stdout)
print("STDERR:\n", res.stderr)
