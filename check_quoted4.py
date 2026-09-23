import psycopg2, json
conn = psycopg2.connect("postgresql://postgres:postgres@127.0.0.1:5432/evolution")
cur = conn.cursor()
cur.execute("SELECT message FROM \"Message\" WHERE message::text LIKE '%contextInfo%' LIMIT 1")
r = cur.fetchone()
if r:
    d = r[0] if isinstance(r[0], dict) else json.loads(r[0])
    msg = d.get('extendedTextMessage', {})
    if 'contextInfo' in msg:
        print(json.dumps(msg['contextInfo'], indent=2))
else:
    print("none")
