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

casos = []
for f, txt, wid in rows:
    if not txt: continue
    m = pat_muerte.findall(txt)
    if m:
        casos.append((f, set(m), txt.strip()))

print(f"Total casos con palabras de fallecido: {len(casos)}")
# Group or print unique events
for idx, (f, m_words, txt) in enumerate(casos, 1):
    # Print short summary
    first_line = txt.split('\n')[0][:80]
    print(f"[{idx:02d}] {f.strftime('%Y-%m-%d %H:%M')} | {list(m_words)[:3]} | {first_line}")
