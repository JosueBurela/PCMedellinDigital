import sqlite3
import json
import os

print("--- AUDITORIA DE whatsapp_messages.db ---")
if os.path.exists('whatsapp_messages.db'):
    conn = sqlite3.connect('whatsapp_messages.db')
    c = conn.cursor()
    tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print("Tablas:", tables)
    for t in tables:
        count = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        cols = [d[1] for d in c.execute(f"PRAGMA table_info({t})").fetchall()]
        print(f"Tabla: {t} | Filas: {count} | Columnas: {cols}")
        
    if 'messages' in tables:
        import datetime
        min_ts, max_ts = c.execute("SELECT MIN(message_timestamp), MAX(message_timestamp) FROM messages").fetchone()
        print(f"Rango timestamps: {min_ts} a {max_ts}")
        try:
            d_min = datetime.datetime.fromtimestamp(int(min_ts))
            d_max = datetime.datetime.fromtimestamp(int(max_ts))
            print(f"Rango fechas: {d_min} a {d_max}")
        except Exception as e:
            print("Error parseando timestamp:", e)
            
        jids = c.execute("SELECT remote_jid, count(*) FROM messages GROUP BY remote_jid").fetchall()
        print("Grupos / Chats:")
        for j in jids:
            print(f"  JID: {j[0]} | Msgs: {j[1]}")
            
        sample = c.execute("SELECT message_timestamp, push_name, text_content FROM messages WHERE text_content IS NOT NULL AND text_content != '' LIMIT 5").fetchall()
        print("Muestra:")
        for s in sample:
            ts_str = str(datetime.datetime.fromtimestamp(int(s[0]))) if s[0] else "N/A"
            txt = str(s[2])[:80].replace('\n', ' ').encode('ascii', errors='replace').decode('ascii')
            print("  ", ts_str, s[1], txt)

print("\n--- AUDITORIA DE messages.jsonl ---")
if os.path.exists('messages.jsonl'):
    import datetime
    line_count = 0
    min_ts = 99999999999
    max_ts = 0
    with open('messages.jsonl', 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line_count += 1
            try:
                data = json.loads(line)
                ts = data.get('messageTimestamp') or (data.get('key', {}).get('messageTimestamp'))
                if ts:
                    ts = int(ts)
                    if ts < min_ts: min_ts = ts
                    if ts > max_ts: max_ts = ts
            except:
                pass
    print(f"Total líneas en messages.jsonl: {line_count}")
    if max_ts > 0:
        print(f"Rango fechas messages.jsonl: {datetime.datetime.fromtimestamp(min_ts)} a {datetime.datetime.fromtimestamp(max_ts)}")

print("\n--- AUDITORIA DE messages_dump.json ---")
if os.path.exists('messages_dump.json'):
    import datetime
    size_mb = os.path.getsize('messages_dump.json') / (1024*1024)
    print(f"Tamaño de messages_dump.json: {size_mb:.2f} MB")
    try:
        with open('messages_dump.json', 'r', encoding='utf-8', errors='ignore') as f:
            dump_data = json.load(f)
            print(f"Tipo en dump: {type(dump_data)}, Total items: {len(dump_data) if isinstance(dump_data, list) else 'dict'}")
            if isinstance(dump_data, list) and len(dump_data) > 0:
                d_min_ts = min([int(m.get('messageTimestamp', 0)) for m in dump_data if m.get('messageTimestamp')])
                d_max_ts = max([int(m.get('messageTimestamp', 0)) for m in dump_data if m.get('messageTimestamp')])
                print(f"Rango fechas dump: {datetime.datetime.fromtimestamp(d_min_ts)} a {datetime.datetime.fromtimestamp(d_max_ts)}")
    except Exception as e:
        print("Error leyendo messages_dump.json:", e)
