import os
import django
import sys
import json
import psycopg2

sys.path.insert(0, '/var/www/pcivildigital')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

conn = psycopg2.connect('postgresql://postgres:postgres@127.0.0.1:5432/evolution')
cur = conn.cursor()

# Find a message that contains "Se traslada a femenina de 26"
cur.execute('''
    SELECT "message"
    FROM "Message"
    WHERE "message"::text ILIKE '%Se traslada a femenina de 26%'
    LIMIT 1
''')

row = cur.fetchone()
if row:
    print(json.dumps(row[0], indent=2)[:3000])
else:
    print("Not found")
