import psycopg2
import re
from datetime import datetime

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()

GROUP_JID = '120363042493725288@g.us'

# Consultar todos los mensajes de 2026
cur.execute('''
    SELECT 
        "id",
        to_timestamp("messageTimestamp") as fecha,
        "pushName",
        "messageType",
        COALESCE(
            "message"->>'conversation',
            "message"->'extendedTextMessage'->>'text',
            "message"->'imageMessage'->>'caption',
            "message"->'videoMessage'->>'caption',
            ''
        ) as texto,
        "key"->>'id' as wa_id
    FROM "Message"
    WHERE "key"->>'remoteJid' = %s
      AND to_timestamp("messageTimestamp") >= '2026-01-01 00:00:00'
    ORDER BY "messageTimestamp" ASC
''', (GROUP_JID,))

todos_2026 = cur.fetchall()
print(f"Total mensajes en 2026 para Proteccion Civil: {len(todos_2026)}")

# Ver distribución por mes de términos médicos y traslados
meses_conteo = {}
fichas_totales = []

for r in todos_2026:
    db_id, fecha, remitente, mtype, texto, wa_id = r
    if not texto:
        continue
    t_lower = texto.lower()
    mes = fecha.strftime('%Y-%m')
    
    es_ficha = False
    if any(k in t_lower for k in ['nombre del paciente', '*paciente*:', '*ambulancia*', '*hospital de traslado*', 'hospital de traslado', '*tipo de servicio*']):
        es_ficha = True
    elif 'paciente' in t_lower and any(k in t_lower for k in ['diagnostico', 'diagnóstico', 'traslado', 'edad', 'dx:', 'se traslada']):
        es_ficha = True
    elif 'sale unidad' in t_lower and any(k in t_lower for k in ['traslado', '097', '098', '208', 'ambulancia']):
        es_ficha = True
    elif 'se atiende' in t_lower and ('masculino' in t_lower or 'femenina' in t_lower or 'joven' in t_lower or 'menor' in t_lower):
        es_ficha = True

    if es_ficha:
        fichas_totales.append(r)
        meses_conteo[mes] = meses_conteo.get(mes, 0) + 1

print(f"\nTotal servicios / traslados / reportes médicos detectados en 2026: {len(fichas_totales)}")
print("\nDesglose por mes en 2026:")
for m, c in sorted(meses_conteo.items()):
    print(f"  Mes: {m} -> {c} servicios/traslados")

conn.close()
