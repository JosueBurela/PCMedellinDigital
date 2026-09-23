import psycopg2
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()
GROUP_JID = '120363042493725288@g.us'

cur.execute("""
    SELECT 
        to_timestamp("messageTimestamp") as fecha,
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
""", (GROUP_JID,))

rows = cur.fetchall()

pat_muerte = re.compile(
    r'\b(?:c[oó]digo\s+(?:14|negro)|ya\s+era\s+14|era\s+14|es\s+14|es\s+el\s+14|px\s*14|px_14|fallecid[oa]s?|[oó]bito|sin\s+signos\s+vitales|sin\s+vida|cad[aá]ver|post\s*mortem|rigor\s*mortis|livideses|muerte\s+patol[oó]gica|muerte\s+por\s+asfixia)\b', 
    re.IGNORECASE
)

# Filter unique messages by text content
vistos = set()
unicos = []
for f, txt, wid in rows:
    if not txt: continue
    t_clean = re.sub(r'\s+', ' ', txt.strip())
    if t_clean in vistos: continue
    vistos.add(t_clean)
    if pat_muerte.search(txt):
        unicos.append((f, txt))

print(f"Total mensajes únicos de fallecidos: {len(unicos)}")
for i, (f, txt) in enumerate(unicos, 1):
    print(f"\n==================== [CASO {i:02d}] {f.strftime('%Y-%m-%d %H:%M')} ====================")
    print(txt[:400])
