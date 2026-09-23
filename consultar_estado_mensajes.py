import psycopg2
from datetime import datetime

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()

# FILTRO ESTRICTO: Única y exclusivamente el grupo oficial de Protección Civil Medellín
GROUP_JID = '120363042493725288@g.us'

print("=" * 60)
print("  AUDITORIA EXCLUSIVA: GRUPO PROTECCION CIVIL MEDELLIN")
print(f"  JID Oficial: {GROUP_JID}")
print("=" * 60)

cur.execute('''
    SELECT count(*), min("messageTimestamp"), max("messageTimestamp")
    FROM "Message"
    WHERE "key"->>'remoteJid' = %s
''', (GROUP_JID,))
row = cur.fetchone()
count_pc = row[0]
min_ts = row[1]
max_ts = row[2]

print(f"\nTotal de mensajes sincronizados de Proteccion Civil: {count_pc}")
if min_ts and max_ts:
    print(f"Mensaje mas antiguo en DB: {datetime.fromtimestamp(min_ts)}")
    print(f"Mensaje mas reciente en DB: {datetime.fromtimestamp(max_ts)}")

# Desglose por tipo de mensaje (texto, imagen, audio, documento, video)
cur.execute('''
    SELECT "messageType", count(*)
    FROM "Message"
    WHERE "key"->>'remoteJid' = %s
    GROUP BY "messageType"
    ORDER BY count(*) DESC;
''', (GROUP_JID,))

print("\nDesglose de contenido:")
for mtype, cant in cur.fetchall():
    print(f"  - {mtype or 'texto/desconocido'}: {cant}")

conn.close()
