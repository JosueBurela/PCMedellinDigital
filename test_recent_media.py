import psycopg2
import requests
import json

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()

GROUP_JID = '120363042493725288@g.us'

# Tomar un mensaje de imagen reciente (por ejemplo de hoy 21 de septiembre o de ayer)
cur.execute('''
    SELECT "key", "message", to_timestamp("messageTimestamp")
    FROM "Message"
    WHERE "key"->>'remoteJid' = %s
      AND "messageType" = 'imageMessage'
    ORDER BY "messageTimestamp" DESC
    LIMIT 3;
''', (GROUP_JID,))

rows = cur.fetchall()

headers = {'apikey': 'MedellinPCSecretToken2026', 'Content-Type': 'application/json'}

for key_json, msg_json, ts in rows:
    print(f"\nProbando imagen reciente de fecha: {ts} (ID: {key_json.get('id')})")
    
    # Intento 1: payload con message objeto
    payload1 = {
        "message": {
            "key": key_json,
            "message": msg_json
        },
        "convertToMp4": False
    }
    r1 = requests.post("http://localhost:8080/chat/getBase64FromMediaMessage/PCHistorico", json=payload1, headers=headers)
    print("Intento 1 (objeto completo):", r1.status_code, "Len base64:", len(r1.json().get('base64', '')) if r1.status_code == 200 else r1.text[:150])

conn.close()
