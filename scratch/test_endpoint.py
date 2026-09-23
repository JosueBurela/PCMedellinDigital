import subprocess

script = """
curl -k -I https://107-170-59-223.sslip.io/api/whatsapp/estado/
"""

res = subprocess.run([
    'ssh', '-n',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    'root@107.170.59.223',
    script.strip()
], capture_output=True, text=True, encoding='utf-8')

print("HEADERS:\n", res.stdout[:500])
