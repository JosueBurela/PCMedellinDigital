import psycopg2
from datetime import datetime

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()

GROUP_JID = '120363042493725288@g.us'

print("=" * 70)
print("ANALISIS DETALLADO DEL HISTORIAL DE PROTECCION CIVIL")
print("=" * 70)

# Ver mensaje más antiguo y más nuevo del grupo
cur.execute('''
    SELECT 
        MIN(to_timestamp("messageTimestamp")),
        MAX(to_timestamp("messageTimestamp")),
        COUNT(*)
    FROM "Message"
    WHERE "key"->>'remoteJid' = %s
''', (GROUP_JID,))

min_d, max_d, total = cur.fetchone()
print(f"Grupo: {GROUP_JID}")
print(f"Total mensajes en DB: {total}")
print(f"Mensaje mas antiguo: {min_d}")
print(f"Mensaje mas reciente: {max_d}")

# Ver si hay mensajes antes del 6 de junio de 2026 en este grupo
cur.execute('''
    SELECT COUNT(*)
    FROM "Message"
    WHERE "key"->>'remoteJid' = %s AND to_timestamp("messageTimestamp") < '2026-06-06 00:00:00'
''', (GROUP_JID,))
pre_june = cur.fetchone()[0]
print(f"Mensajes antes del 6 de junio de 2026 en este grupo: {pre_june}")

# Ver los 5 mensajes más antiguos del grupo
print("\n--- 5 Mensajes más antiguos registrados del grupo ---")
cur.execute('''
    SELECT 
        to_timestamp("messageTimestamp"),
        "key"->>'id',
        "pushName",
        "messageType"
    FROM "Message"
    WHERE "key"->>'remoteJid' = %s
    ORDER BY "messageTimestamp" ASC
    LIMIT 5
''', (GROUP_JID,))
for row in cur.fetchall():
    print(f"Fecha: {row[0]} | ID: {row[1]} | Remitente: {row[2]} | Tipo: {row[3]}")

# Ver chats con mensajes más antiguos en toda la base de datos (para entender el sync)
print("\n--- Fecha más antigua sincronizada por tipo de chat en el teléfono ---")
cur.execute('''
    SELECT 
        CASE 
            WHEN "key"->>'remoteJid' LIKE '%@g.us' THEN 'Grupos'
            ELSE 'Chats Privados'
        END as tipo_chat,
        MIN(to_timestamp("messageTimestamp")),
        MAX(to_timestamp("messageTimestamp")),
        COUNT(*)
    FROM "Message"
    GROUP BY tipo_chat
''')
for row in cur.fetchall():
    print(f"Tipo: {row[0]:15} | Mas antiguo: {row[1]} | Mas reciente: {row[2]} | Total: {row[3]}")

conn.close()
