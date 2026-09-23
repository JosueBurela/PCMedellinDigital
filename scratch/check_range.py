import subprocess

script = """
docker exec postgres_local psql -U postgres -d evolution -c "
SELECT 
    MIN(to_timestamp(\\"messageTimestamp\\")) as mas_antiguo, 
    MAX(to_timestamp(\\"messageTimestamp\\")) as mas_reciente, 
    COUNT(*) as total_mensajes 
FROM \\"Message\\" 
WHERE \\"key\\"->>'remoteJid' = '120363042493725288@g.us';
"
"""

res = subprocess.run([
    'ssh', '-n',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    'root@107.170.59.223',
    script.strip()
], capture_output=True, text=True, encoding='utf-8')

print("POSTGRES RANGE:\n", res.stdout)
