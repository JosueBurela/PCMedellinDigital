import sqlite3
import re
import sys
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('whatsapp_messages.db')
c = conn.cursor()
c.execute("""
SELECT id, datetime(message_timestamp, 'unixepoch', 'localtime') as dt, text_content
FROM messages
WHERE text_content LIKE '%PARAMEDICO%' OR text_content LIKE '%PARAMÉDICO%'
ORDER BY message_timestamp ASC
""")
rows = c.fetchall()
print(f"Total mensajes con PARAMEDICO: {len(rows)}")

def clean(v):
    if not v: return None
    v = v.strip()
    v = re.sub(r'^\*+|\*+$', '', v).strip()
    return v if v else None

parsed_frap_db = []

for r in rows:
    text = r[2]
    # Buscar campos FRAP
    def get_f(pat):
        m = re.search(pat, text, re.IGNORECASE)
        return m.group(1).strip() if m else None

    paciente = clean(get_f(r'NOMBRE DEL PACIENTE\*?[:\s]*([^\n\*]+)'))
    if not paciente:
        # Algunos escriben NOMBRE DEL PACIENTE en la siguiente línea o con espacios
        m_p = re.search(r'NOMBRE DEL PACIENTE\s*\*?\s*:?\s*([A-ZÁÉÍÓÚÑ][^\n\*]+)', text, re.IGNORECASE)
        if m_p:
            paciente = clean(m_p.group(1))

    if paciente:
        fecha = clean(get_f(r'FECHA\*?[:\s]*([^\n\*]+)'))
        hora = clean(get_f(r'HORA(?: DEL REPORTE)?\*?[:\s]*([^\n\*]+)'))
        unidad = clean(get_f(r'AMBULANCIA\*?[:\s]*([^\n\*]+)'))
        operador = clean(get_f(r'OPERADOR\*?[:\s]*([^\n\*]+)'))
        paramedico = clean(get_f(r'PARAM[ÉE]DICO\*?[:\s]*([^\n\*]+)'))
        edad = clean(get_f(r'EDAD\*?[:\s]*([^\n\*]+)'))
        dx = clean(get_f(r'DIAGN[^\*:\n]+STICO\*?[:\s]*([^\n\*]+)'))
        desc = clean(get_f(r'DESCRIPCI[^\*:\n]+N DE LO OCURRIDO\*?[:\s]*([^\*]+?)(?=\*[A-Z]|\Z)'))
        hosp = clean(get_f(r'HOSPITAL\s+DE\s+TRASLADO\*?[:\s]*([^\n\*]+)'))
        recibe = clean(get_f(r'RECIBE\*?[:\s]*([^\n\*]+)'))
        dir_serv = clean(get_f(r'DIRECCI[^\*:\n]+N DEL SERVICIO\*?[:\s]*([^\n\*]+)'))
        codigo = clean(get_f(r'C[^\*:\n]+DIGO\*?[:\s]*([^\n\*]+)'))

        h_low = str(hosp).lower()
        es_neg = any(w in h_low for w in ['no amerit', 'n/a', 'na', 'niega', 'deslinde', 'no se traslada', 'no aporta', 'particular'])
        
        parsed_frap_db.append({
            'msg_id': r[0],
            'dt_msg': r[1],
            'fecha_frap': fecha if fecha else r[1][:10],
            'hora_frap': hora if hora else r[1][11:16],
            'unidad': unidad if unidad else 'U-208 / U-098',
            'paciente': paciente,
            'edad': edad if edad else 'No especificada',
            'diagnostico': dx if dx else 'Atención médica prehospitalaria',
            'descripcion': desc.replace('\n', ' ') if desc else '',
            'hospital': hosp if hosp else 'Centro Hospitalario',
            'recibe': recibe if recibe else 'Personal de Triage',
            'direccion': dir_serv if dir_serv else 'Medellín de Bravo',
            'trasladado': bool(hosp) and not es_neg
        })

conn.close()

df_db_frap = pd.DataFrame(parsed_frap_db)
print(f"\nTotal partes FRAP con paciente nominal encontrados: {len(df_db_frap)}")
print(f"Total traslados efectivos confirmados: {df_db_frap['trasladado'].sum()}")
print(f"Total valorados en sitio (sin traslado): {(~df_db_frap['trasladado']).sum()}")

print("\n--- DETALLE DE TRASLADOS EFECTIVOS DE LA DB ---")
for i, r in df_db_frap[df_db_frap['trasladado']].iterrows():
    print(f"[{r['fecha_frap']} {r['hora_frap']}] {r['unidad']}")
    print(f"  Paciente: {r['paciente']} (Edad: {r['edad']})")
    print(f"  Por qué (Dx): {r['diagnostico']}")
    print(f"  A dónde (Destino): {r['hospital']} (Recibe: {r['recibe']})")
    print(f"  Lugar: {r['direccion']}")
    print("-" * 75)
