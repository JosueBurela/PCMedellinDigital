import psycopg2
import requests
import json
import base64

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()

GROUP_JID = '120363042493725288@g.us'

# Buscar 1 imagen de cada día hacia atrás (21 sep, 20 sep, 19 sep, 15 sep, 1 sep, 15 ago...)
dias = ['2026-09-21', '2026-09-20', '2026-09-18', '2026-09-15', '2026-09-10', '2026-09-01', '2026-08-15', '2026-08-01', '2026-07-15']

headers = {'apikey': 'MedellinPCSecretToken2026', 'Content-Type': 'application/json'}

print("Verificando ventana de validez de descarga de imágenes...")

for dia in dias:
    cur.execute('''
        SELECT "key", "message", to_timestamp("messageTimestamp")
        FROM "Message"
        WHERE "key"->>'remoteJid' = %s
          AND "messageType" = 'imageMessage'
          AND to_char(to_timestamp("messageTimestamp"), 'YYYY-MM-DD') = %s
        ORDER BY "messageTimestamp" DESC
        LIMIT 1;
    ''', (GROUP_JID, dia))
    row = cur.fetchone()
    if not row:
        print(f"[{dia}] No hay imagen de muestra")
        continue
    
    key_json, msg_json, ts = row
    payload = {
        "message": {
            "key": key_json,
            "message": msg_json
        },
        "convertToMp4": False
    }
    try:
        r = requests.post("http://localhost:8080/chat/getBase64FromMediaMessage/PCHistorico", json=payload, headers=headers, timeout=10)
        ok = r.status_code in [200, 201] and 'base64' in r.json()
        status_txt = "OK (Descargada)" if ok else f"Fallo ({r.status_code})"
        print(f"[{dia} {ts.strftime('%H:%M')}] -> {status_txt}")
    except Exception as e:
        print(f"[{dia}] Error: {e}")

conn.close()
