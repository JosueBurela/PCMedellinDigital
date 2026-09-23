import psycopg2
import requests
import json
import base64
import os
from datetime import datetime

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()

GROUP_JID = '120363042493725288@g.us'

# Buscar imágenes de salida de ambulancias en diferentes meses (Junio, Julio, Agosto, Septiembre)
meses = ['2026-06', '2026-07', '2026-08', '2026-09']

muestras = []
for mes in meses:
    cur.execute('''
        SELECT 
            "id",
            to_timestamp("messageTimestamp") as fecha,
            "pushName",
            "messageType",
            COALESCE(
                "message"->'imageMessage'->>'caption',
                "message"->>'conversation',
                ''
            ) as caption,
            "key",
            "message"
        FROM "Message"
        WHERE "key"->>'remoteJid' = %s
          AND "messageType" = 'imageMessage'
          AND to_char(to_timestamp("messageTimestamp"), 'YYYY-MM') = %s
          AND (
              "message"->'imageMessage'->>'caption' ILIKE '%%sale%%'
              OR "message"->'imageMessage'->>'caption' ILIKE '%%base%%'
              OR "message"->'imageMessage'->>'caption' ILIKE '%%unidad%%'
          )
        ORDER BY "messageTimestamp" ASC
        LIMIT 1;
    ''', (GROUP_JID, mes))
    row = cur.fetchone()
    if row:
        muestras.append(row)

print(f"Total muestras encontradas para probar descarga: {len(muestras)}")

headers = {
    'apikey': 'MedellinPCSecretToken2026',
    'Content-Type': 'application/json'
}

os.makedirs('test_descargas', exist_ok=True)

for m in muestras:
    db_id, fecha, push, mtype, caption, key_json, msg_json = m
    wa_id = key_json.get('id')
    print(f"\n--- Probando descarga de mes {fecha.strftime('%Y-%m')} ---")
    print(f"Fecha: {fecha} | ID: {wa_id} | Caption: {caption}")
    
    payload = {
        "message": {
            "key": key_json,
            "message": msg_json
        },
        "convertToMp4": False
    }
    
    try:
        url = "http://localhost:8080/chat/getBase64FromMediaMessage/PCHistorico"
        resp = requests.post(url, json=payload, headers=headers, timeout=20)
        print(f"Status HTTP: {resp.status_code}")
        if resp.status_code in [200, 201]:
            data = resp.json()
            b64 = data.get('base64')
            if b64:
                file_bytes = base64.b64decode(b64)
                file_path = f"test_descargas/prueba_{fecha.strftime('%Y%m%d_%H%M%S')}_{wa_id[:6]}.jpg"
                with open(file_path, "wb") as f:
                    f.write(file_bytes)
                print(f"  --> DESCARGADA Y DESCIFRADA EXITOSAMENTE: {file_path} ({len(file_bytes)} bytes)")
            else:
                print(f"  --> Respuesta sin campo base64: {list(data.keys())}")
        else:
            print(f"  --> Error HTTP: {resp.text[:200]}")
    except Exception as e:
        print(f"  --> Excepción: {e}")

conn.close()
