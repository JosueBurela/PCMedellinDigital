import subprocess

script = """
docker exec postgres_local psql -U postgres -d evolution -t -A -c "
SELECT json_build_object(
    'key', key,
    'pushName', \\"pushName\\",
    'messageTimestamp', \\"messageTimestamp\\",
    'message', message
)
FROM \\"Message\\"
WHERE \\"key\\"->>'remoteJid' = '120363042493725288@g.us'
  AND \\"messageTimestamp\\" >= 1789624801
ORDER BY \\"messageTimestamp\\" ASC;
" | head -n 5
"""

res = subprocess.run([
    'ssh', '-n',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    'root@107.170.59.223',
    script.strip()
], capture_output=True, text=True, encoding='utf-8')

print("PG JSON OUTPUT:\n", res.stdout[:1500].encode('ascii', 'replace').decode('ascii'))
