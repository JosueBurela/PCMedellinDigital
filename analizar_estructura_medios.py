import psycopg2
import json

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()
GROUP_JID = '120363042493725288@g.us'

# Revisar un mensaje de imagen
cur.execute('''
    SELECT id, "key", "messageType", "message", "messageTimestamp"
    FROM "Message"
    WHERE "key"->>'remoteJid' = %s AND "messageType" = 'imageMessage'
    LIMIT 1;
''', (GROUP_JID,))
img_row = cur.fetchone()
if img_row:
    print("=== EJEMPLO DE MENSAJE DE IMAGEN ===")
    print("ID:", img_row[0])
    print("Key:", img_row[1])
    print("Type:", img_row[2])
    msg_data = img_row[3]
    print("Message keys:", list(msg_data.keys()) if isinstance(msg_data, dict) else msg_data)
    if isinstance(msg_data, dict) and 'imageMessage' in msg_data:
        im = msg_data['imageMessage']
        print("imageMessage keys:", list(im.keys()))
        print("Mimetype:", im.get('mimetype'))
        print("Caption:", im.get('caption'))
        print("DirectPath:", im.get('directPath'))
        print("Has mediaKey?:", 'mediaKey' in im)
        print("Has url?:", 'url' in im)

# Revisar un mensaje de audio
cur.execute('''
    SELECT id, "key", "messageType", "message", "messageTimestamp"
    FROM "Message"
    WHERE "key"->>'remoteJid' = %s AND "messageType" = 'audioMessage'
    LIMIT 1;
''', (GROUP_JID,))
aud_row = cur.fetchone()
if aud_row:
    print("\n=== EJEMPLO DE MENSAJE DE AUDIO ===")
    print("ID:", aud_row[0])
    msg_data = aud_row[3]
    if isinstance(msg_data, dict) and 'audioMessage' in msg_data:
        am = msg_data['audioMessage']
        print("audioMessage keys:", list(am.keys()))
        print("Mimetype:", am.get('mimetype'))
        print("Seconds:", am.get('seconds'))

# Revisar si hay registros en la tabla "Media" de Evolution API
cur.execute('SELECT count(*) FROM "Media"')
print(f"\nTotal en tabla 'Media': {cur.fetchone()[0]}")

conn.close()
