import subprocess

script = """
curl -s -H "apikey: MedellinPCSecretToken2026" http://localhost:8080/group/fetchAllGroups/PCMedellin?getParticipants=false
"""

res = subprocess.run([
    'ssh', '-n',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    'root@107.170.59.223',
    script.strip()
], capture_output=True, text=True, encoding='utf-8')

print("GROUPS:\n", res.stdout[:2000].encode('ascii', 'replace').decode('ascii'))
