import sqlite3
import psycopg2
import requests
import base64
import os
from datetime import datetime

print("Iniciando descarga y almacenamiento de fotos de casos de Septiembre...")

sql_conn = sqlite3.connect('bitacora_casos_pc.db')
sql_cur = sql_conn.cursor()

pg_conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
pg_cur = pg_conn.cursor()

# Obtener mensajes con foto de casos en Septiembre 2026
sql_cur.execute('''
    SELECT cm.id, cm.id_caso, cm.wa_id, cm.fecha_hora, cm.rol_mensaje, cm.texto
    FROM caso_mensajes cm
    JOIN casos c ON c.id_caso = cm.id_caso
    WHERE cm.es_foto = 1
      AND cm.fecha_hora >= '2026-09-10 00:00:00'
    ORDER BY cm.fecha_hora ASC
''')
fotos_a_descargar = sql_cur.fetchall()
print(f"Total fotos de casos recientes a procesar: {len(fotos_a_descargar)}")

headers = {'apikey': 'MedellinPCSecretToken2026', 'Content-Type': 'application/json'}
url_api = "http://localhost:8080/chat/getBase64FromMediaMessage/PCHistorico"

descargadas_ok = 0
fallos = 0

for item in fotos_a_descargar:
    cm_id, id_caso, wa_id, f_hora, rol, txt = item
    
    # Crear carpeta para el caso
    caso_dir = os.path.join("Casos_PC_Medellin", id_caso, "fotos")
    os.makedirs(caso_dir, exist_ok=True)
    
    # Obtener payload del mensaje desde Postgres
    pg_cur.execute('''
        SELECT "key", "message"
        FROM "Message"
        WHERE "key"->>'id' = %s
        LIMIT 1;
    ''', (wa_id,))
    row_pg = pg_cur.fetchone()
    if not row_pg:
        continue
    
    key_json, msg_json = row_pg
    payload = {
        "message": {
            "key": key_json,
            "message": msg_json
        },
        "convertToMp4": False
    }
    
    try:
        r = requests.post(url_api, json=payload, headers=headers, timeout=15)
        if r.status_code in [200, 201]:
            data = r.json()
            b64 = data.get('base64')
            if b64:
                file_bytes = base64.b64decode(b64)
                # Nombre limpio: ROL_HORA_ID.jpg
                hora_str = f_hora.replace(':', '').replace('-', '').replace(' ', '_')
                filename = f"{rol}_{hora_str}_{wa_id[:6]}.jpg"
                filepath = os.path.join(caso_dir, filename)
                with open(filepath, "wb") as f:
                    f.write(file_bytes)
                
                # Actualizar ruta local en SQLite
                sql_cur.execute('''
                    UPDATE caso_mensajes 
                    SET foto_local_path = ?
                    WHERE id = ?
                ''', (filepath, cm_id))
                descargadas_ok += 1
            else:
                fallos += 1
        else:
            fallos += 1
    except Exception as e:
        fallos += 1

sql_conn.commit()
sql_conn.close()
pg_conn.close()

print(f"\nResumen de descarga:")
print(f"  - Fotos descargadas y vinculadas exitosamente: {descargadas_ok}")
print(f"  - Fotos no disponibles en CDN de WhatsApp: {fallos}")
