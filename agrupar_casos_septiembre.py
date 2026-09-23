import psycopg2
import re
import json
from datetime import datetime, timedelta

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()

GROUP_JID = '120363042493725288@g.us'

# Buscar partes médicos de Septiembre 2026
cur.execute('''
    SELECT 
        "id",
        to_timestamp("messageTimestamp") as fecha_msg,
        "pushName",
        COALESCE(
            "message"->>'conversation',
            "message"->'extendedTextMessage'->>'text',
            "message"->'imageMessage'->>'caption',
            ''
        ) as texto,
        "key"->>'id' as wa_id
    FROM "Message"
    WHERE "key"->>'remoteJid' = %s
      AND to_char(to_timestamp("messageTimestamp"), 'YYYY-MM') = '2026-09'
      AND (
          "message"::text ILIKE '%%*NOMBRE DEL PACIENTE*%%'
          OR "message"::text ILIKE '%%*PACIENTE*%%'
      )
    ORDER BY "messageTimestamp" DESC
    LIMIT 3;
''', (GROUP_JID,))

partes_sep = cur.fetchall()

print(f"Partes médicos encontrados en Septiembre: {len(partes_sep)}")

for p in partes_sep:
    db_id, fecha_msg, remitente, texto, wa_id = p
    print("=" * 80)
    print(f"PARTE MEDICO: {fecha_msg} | Remitente: {remitente}")
    print("-" * 80)
    print(texto[:300] + ("..." if len(texto) > 300 else ""))
    
    # Buscar mensajes asociados a este servicio en una ventana de 2 horas antes y 1 hora despues
    t_inicio = fecha_msg - timedelta(hours=2)
    t_fin = fecha_msg + timedelta(hours=2)
    
    cur.execute('''
        SELECT 
            to_timestamp("messageTimestamp") as f,
            "pushName",
            "messageType",
            COALESCE(
                "message"->'imageMessage'->>'caption',
                "message"->>'conversation',
                "message"->'extendedTextMessage'->>'text',
                ''
            ) as txt,
            "message"->'imageMessage' IS NOT NULL as tiene_img,
            "key"->>'id' as mid,
            "key",
            "message"
        FROM "Message"
        WHERE "key"->>'remoteJid' = %s
          AND to_timestamp("messageTimestamp") BETWEEN %s AND %s
        ORDER BY "messageTimestamp" ASC
    ''', (GROUP_JID, t_inicio, t_fin))
    
    mensajes_entorno = cur.fetchall()
    print(f"\nMensajes en la ventana del servicio ({t_inicio.strftime('%H:%M')} a {t_fin.strftime('%H:%M')}): {len(mensajes_entorno)}")
    for me in mensajes_entorno:
        f_me, push_me, mtype_me, txt_me, tiene_img_me, mid_me, k_me, msg_me = me
        t_clean = (txt_me or '').replace('\n', ' ')[:70]
        marca = ""
        if tiene_img_me:
            marca = "[FOTO]"
        if 'sale' in t_clean.lower():
            marca += " [SALIDA]"
        if 'base' in t_clean.lower():
            marca += " [RETORNO/BASE]"
        if 'hospital' in t_clean.lower():
            marca += " [HOSPITAL]"
        if marca:
            clean_print = f"  {f_me.strftime('%H:%M:%S')} | {str(push_me)[:15]:15} | {marca} {t_clean}".encode('ascii', errors='replace').decode('ascii')
            print(clean_print)

conn.close()
