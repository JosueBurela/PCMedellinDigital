import psycopg2
import re
import pandas as pd

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/evolution")
cur = conn.cursor()

GROUP_JID = '120363042493725288@g.us'

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

rows = cur.fetchall()

def es_reporte_medico(txt):
    t_lower = txt.lower()
    
    # 1. Ficha formal o parte clínico
    if any(k in t_lower for k in ['nombre del paciente', '*paciente*:', '*hospital de traslado*', 'hospital de traslado', '*ambulancia*:', '*tipo de servicio*']):
        return True
    if '*ambulancia*' in t_lower and ('*fecha*' in t_lower or 'operador' in t_lower or 'paramedico' in t_lower):
        return True
    # 2. Descripción clínica directa
    if 'paciente' in t_lower and any(k in t_lower for k in ['diagnostico', 'diagnóstico', 'dx:', 'se traslada', 'traslado a', 'hospital', 'edad', 'signos vitales', 'inconveniente']):
        return True
    # 3. Salida explícita a traslado
    if any(t_lower.strip().startswith(s) for s in ['sale unidad', 'sale la unidad', 'sale u-', 'sale u0', 'unidad sale', 'sale ambulancia']):
        if any(k in t_lower for k in ['traslado', 'paciente', 'apoyo', 'clínica', 'clinica', 'hospital', 'punto', 'lecionad', 'lesionad', 'atropellad', 'choque', 'derrapad']):
            return True
    # 4. Atención prehospitalaria
    if 'se atiende' in t_lower and any(k in t_lower for k in ['masculino', 'femenina', 'joven', 'menor', 'px', 'paciente', 'persona']):
        return True
    if 'procede al hospital' in t_lower or 'rumbo al hospital' in t_lower or 'va en ruta al' in t_lower:
        return True
    return False

reportes_medicos = []
for r in rows:
    if es_reporte_medico(r[4]):
        reportes_medicos.append(r)

print(f"Total reportes médicos y traslados detectados en 2026 (Enero a Septiembre): {len(reportes_medicos)}")

# Agrupar por mes
df_temp = pd.DataFrame([{'mes': r[1].strftime('%Y-%m')} for r in reportes_medicos])
print("\nDesglose por mes:")
print(df_temp['mes'].value_counts().sort_index())

conn.close()
