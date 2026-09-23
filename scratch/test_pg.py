import psycopg2, datetime

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()
cur.execute("""
    SELECT count(*), min("messageTimestamp"), max("messageTimestamp")
    FROM "Message"
    WHERE "key"->>'remoteJid' = '120363042493725288@g.us';
""")
row = cur.fetchone()
print("TOTAL MENSAJES:", row[0])
if row[1] and row[2]:
    print("MIN DT:", datetime.datetime.fromtimestamp(row[1]))
    print("MAX DT:", datetime.datetime.fromtimestamp(row[2]))
