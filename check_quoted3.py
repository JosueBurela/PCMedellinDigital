import psycopg2, json
conn = psycopg2.connect("postgresql://postgres:postgres@127.0.0.1:5432/evolution")
cur = conn.cursor()
cur.execute("SELECT message FROM \"Message\" ORDER BY \"messageTimestamp\" DESC LIMIT 20")
for r in cur.fetchall():
    d = r[0] if isinstance(r[0], dict) else json.loads(r[0])
    msg = d.get('extendedTextMessage', {})
    if 'contextInfo' in msg:
        print(json.dumps(msg['contextInfo'], indent=2))
        break
