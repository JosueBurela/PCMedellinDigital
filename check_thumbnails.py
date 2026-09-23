import psycopg2

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()
GROUP_JID = '120363042493725288@g.us'
cur.execute('''
    SELECT 
        COUNT(*),
        COUNT("message"->'imageMessage'->'jpegThumbnail')
    FROM "Message"
    WHERE "key"->>'remoteJid' = %s
      AND "messageType" = 'imageMessage'
''', (GROUP_JID,))
tot, thumbs = cur.fetchone()
print(f"Total imagenes: {tot} | Con jpegThumbnail guardado directo en DB: {thumbs}")

# Ver si el thumbnail se puede decodificar y ver
cur.execute('''
    SELECT 
        "key"->>'id',
        to_timestamp("messageTimestamp"),
        "message"->'imageMessage'->>'caption',
        "message"->'imageMessage'->'jpegThumbnail'
    FROM "Message"
    WHERE "key"->>'remoteJid' = %s
      AND "messageType" = 'imageMessage'
      AND "message"->'imageMessage'->'jpegThumbnail' IS NOT NULL
      AND to_char(to_timestamp("messageTimestamp"), 'YYYY-MM') = '2026-06'
    LIMIT 1;
''', (GROUP_JID,))
row = cur.fetchone()
if row:
    print(f"Muestra de Junio: ID={row[0]} Fecha={row[1]} Caption={row[2]}")
    thumb_data = row[3]
    print(f"Tipo de datos de thumbnail: {type(thumb_data)}")
conn.close()
