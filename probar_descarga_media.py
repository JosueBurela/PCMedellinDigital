import psycopg2
import urllib.request
import json

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()
GROUP_JID = '120363042493725288@g.us'

# Tomar una imagen reciente (ordenada por messageTimestamp descendente)
cur.execute('''
    SELECT "key", "message", "messageTimestamp"
    FROM "Message"
    WHERE "key"->>'remoteJid' = %s AND "messageType" = 'imageMessage'
    ORDER BY "messageTimestamp" DESC
    LIMIT 3;
''', (GROUP_JID,))
rows = cur.fetchall()
conn.close()

for idx, (key, message, ts) in enumerate(rows):
    print(f"\n--- Probando Imagen Reciente #{idx+1} (TS: {ts}) ---")
    payload = {
        "message": {
            "key": key,
            "message": message
        },
        "convertToMp4": False
    }
    
    req = urllib.request.Request(
        'http://localhost:8080/chat/getBase64FromMediaMessage/PCHistorico',
        headers={'apikey': 'MedellinPCSecretToken2026', 'Content-Type': 'application/json'},
        data=json.dumps(payload).encode(),
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            if 'base64' in data and data['base64']:
                print(f"[EXITO] Imagen descargada y desencriptada! Tamaño base64: {len(data['base64'])} bytes")
                # Guardar muestra para verificar
                import base64
                b64_clean = data['base64'].split(',', 1)[1] if ',' in data['base64'] else data['base64']
                with open(f"muestra_imagen_{idx+1}.jpg", "wb") as f_img:
                    f_img.write(base64.b64decode(b64_clean))
                print(f"[OK] Guardada en disco como muestra_imagen_{idx+1}.jpg")
                break
            else:
                print("Respuesta sin base64:", data)
    except urllib.error.HTTPError as e:
        print("HTTPError code:", e.code)
        print("HTTPError body:", e.read().decode()[:300])
    except Exception as e:
        print("Error:", e)
