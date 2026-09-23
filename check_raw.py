import os
import django
import sys
import psycopg2
import json

sys.path.insert(0, '/var/www/pcivildigital')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

conn = psycopg2.connect('postgresql://postgres:postgres@127.0.0.1:5432/evolution')
cur = conn.cursor()

# Get the last 20 messages from the group
cur.execute('''
    SELECT "messageTimestamp", "pushName", "message"
    FROM "Message"
    WHERE "key"->>'remoteJid' = '120363042493725288@g.us'
    ORDER BY "messageTimestamp" DESC
    LIMIT 30
''')

rows = cur.fetchall()
for r in reversed(rows):
    ts, push, msg = r
    msg_dict = json.loads(msg) if isinstance(msg, str) else msg
    text = ""
    if 'conversation' in msg_dict: text = msg_dict['conversation']
    elif 'extendedTextMessage' in msg_dict: text = msg_dict['extendedTextMessage'].get('text', '')
    elif 'imageMessage' in msg_dict: text = "[IMAGE] " + msg_dict['imageMessage'].get('caption', '')
    
    if text:
        print(f"[{push}] {text}")
