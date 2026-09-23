import psycopg2

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()
GROUP_JID = '120363042493725288@g.us'
cur.execute('''
    SELECT count(*), min(to_timestamp("messageTimestamp")), max(to_timestamp("messageTimestamp"))
    FROM "Message"
    WHERE "key"->>'remoteJid' = %s
''', (GROUP_JID,))
r = cur.fetchone()
print(f"Grupo {GROUP_JID}: Count={r[0]} | Min={r[1]} | Max={r[2]}")

# Ver si hay otros grupos de PC en la DB
cur.execute('''
    SELECT "key"->>'remoteJid', count(*), min(to_timestamp("messageTimestamp")), max(to_timestamp("messageTimestamp"))
    FROM "Message"
    WHERE "key"->>'remoteJid' LIKE '%@g.us'
    GROUP BY "key"->>'remoteJid'
    ORDER BY count(*) DESC;
''')
print("\nTodos los grupos en la DB:")
for row in cur.fetchall():
    print(f"JID: {row[0]} | Count: {row[1]} | Min: {row[2]} | Max: {row[3]}")

conn.close()
