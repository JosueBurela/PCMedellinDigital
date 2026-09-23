import psycopg2
import json
from datetime import datetime
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()
GROUP_JID = '120363042493725288@g.us'

cur.execute('''
    SELECT "messageTimestamp", "messageType", "message", "key"
    FROM "Message"
    WHERE "key"->>'remoteJid' = %s
    ORDER BY "messageTimestamp" ASC
    LIMIT 10;
''', (GROUP_JID,))

print("=== PRIMEROS 10 MENSAJES REGISTRADOS EN EL GRUPO ===")
for ts, mtype, msg, key in cur.fetchall():
    fecha = datetime.fromtimestamp(ts)
    text = ""
    if isinstance(msg, dict):
        if 'conversation' in msg:
            text = msg['conversation']
        elif 'extendedTextMessage' in msg:
            text = msg['extendedTextMessage'].get('text', '')
        elif 'protocolMessage' in msg:
            text = f"[ProtocolMessage: {msg['protocolMessage']}]"
        elif 'imageMessage' in msg:
            text = f"[Imagen: {msg['imageMessage'].get('caption')}]"
        else:
            text = str(list(msg.keys()))
    print(f"[{fecha}] ({mtype}) de {key.get('participant') or key.get('remoteJid')}: {text[:150]}")

conn.close()
