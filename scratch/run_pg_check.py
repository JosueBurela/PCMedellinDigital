import subprocess

script = """
cat << 'EOF' > /var/www/pcivildigital/test_pg.py
import psycopg2

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()
cur.execute('''
    SELECT count(*), min("messageTimestamp"), max("messageTimestamp")
    FROM "Message"
    WHERE "key"->>'remoteJid' = '120363042493725288@g.us'
''')
print("PG RESULT:", cur.fetchone())
EOF
cd /var/www/pcivildigital && ./venv/bin/python test_pg.py
"""

# Usar scp para subir el script
with open(r'c:\Users\burel\OneDrive\Documentos\PCivil Digital\scratch\test_pg.py', 'w') as f:
    f.write('''import psycopg2, datetime

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()
cur.execute("""
    SELECT count(*), min("messageTimestamp"), max("messageTimestamp")
    FROM "Message"
    WHERE "key"->>'remoteJid' = '120363042493725288@g.us';
""")
row = cur.fetchone()
print("TOTAL MENSAJES:", row[0])
if row[1] and row[2]:
    print("MIN DT:", datetime.datetime.fromtimestamp(row[1]))
    print("MAX DT:", datetime.datetime.fromtimestamp(row[2]))
''')

res_scp = subprocess.run([
    'scp',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    r'c:\Users\burel\OneDrive\Documentos\PCivil Digital\scratch\test_pg.py',
    'root@107.170.59.223:/var/www/pcivildigital/test_pg.py'
], capture_output=True, text=True, encoding='utf-8')

res_run = subprocess.run([
    'ssh', '-n',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    'root@107.170.59.223',
    'cd /var/www/pcivildigital && ./venv/bin/python test_pg.py'
], capture_output=True, text=True, encoding='utf-8')

print("RESULT:\n", res_run.stdout)
if res_run.stderr:
    print("STDERR:\n", res_run.stderr)
