import subprocess

script = """
echo "=== 1. CONNECTION STATE ==="
curl -s -H "apikey: MedellinPCSecretToken2026" http://localhost:8080/instance/connectionState/PCMedellin
echo ""

echo "=== 2. CONNECT (QR) ==="
curl -s -H "apikey: MedellinPCSecretToken2026" http://localhost:8080/instance/connect/PCMedellin | head -c 200
echo ""
"""

res = subprocess.run([
    'ssh', '-n',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    'root@107.170.59.223',
    script.strip()
], capture_output=True, text=True, encoding='utf-8')

print("TEST API:\n", res.stdout)
