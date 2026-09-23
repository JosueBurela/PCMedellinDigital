import sqlite3
import pandas as pd
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Base consolidada anual
conn = sqlite3.connect('whatsapp_messages.db')
df_anual = pd.read_sql_query("SELECT * FROM servicios_anuales_2026", conn)

print("=== 1. SERVICIOS ANUALES 2026 (TABLA OFICIAL) ===")
print("Total emergencias:", len(df_anual))
print("Emergencias médicas:", len(df_anual[df_anual['categoria_macro'] == 'Atención Médica / Prehospitalaria']))

# Ver en df_anual cuántos traslados hay por mes según subtipo
print("\nSubtipo 'Traslado Interhospitalario' por mes:")
print(df_anual[df_anual['subtipo_servicio'] == 'Traslado Interhospitalario']['mes'].value_counts())

# 2. Análisis detallado en reporte_mensual_agosto_limpio.csv
df_agosto_limpio = pd.read_csv('reporte_mensual_agosto_limpio.csv')
print(f"\n=== 2. CASOS EN reporte_mensual_agosto_limpio.csv (Total: {len(df_agosto_limpio)}) ===")

# Revisar en cada caso de agosto si hay traslado a hospital o traslado programado
traslados_agosto = []
hosp_destinos = []
unidades_traslado = []

patrones_hosp = {
    'Hospital General de Boca del Río': [r'general de boca', r'hg boca', r'hgbv', r'hospital de boca', r'hg de boca'],
    'IMSS Clínica 71 (Díaz Mirón)': [r'cl[ií]nica 71', r'imss 71', r'71 de d[ií]as mir[oó]n', r'imss #71'],
    'IMSS Clínica 61 / Cuauhtémoc': [r'cl[ií]nica #?61', r'imss #?61', r'cuauht[eé]moc', r'61 de d[ií]as mir[oó]n'],
    'Hospital Naval (HOSNAVER)': [r'hosnaver', r'hospital naval'],
    'Torre Pediátrica': [r'torre pedi[aá]trica', r'torre pedi', r'infantil'],
    'Hospital de María / D\'María': [r'd\'mar[ií]a', r'hospital de mar[ií]a', r'd mar[ií]a'],
    'Cruz Roja Veracruz': [r'cruz roja'],
    'Hospital Regional de Alta Especialidad': [r'hospital regional', r'alta especialidad'],
    'Traslado a Domicilio (Alta Hospitalaria)': [r'a su domicilio', r'a domicilio', r'traslado a casa']
}

for idx, row in df_agosto_limpio.iterrows():
    text = str(row['Transcripcion_Incidente'])
    text_low = text.lower()
    
    # Checar si hubo negativa explícita de traslado
    negativa = bool(re.search(r'(no requiere traslado|sin traslado|no amerita traslado|no amerit[oó] traslado|se niega al traslado|niega traslado|firma deslinde|firma negativa de traslado|trasladaron.*por sus medios)', text_low))
    
    # Checar si hubo traslado
    es_traslado = False
    tipo_tr = None
    dest = []
    
    # Patrones de confirmación de traslado
    if bool(re.search(r'(traslado programado|inicia traslado|comienza traslado|se traslada|fue trasladado|sale u[ _-]?208.*a traslado|sale unidad 098.*a traslado|unidad.*traslada|se procede a trasladar|hospital de traslado:? [^nN]|arriba a hospital|ingresa a hospital|en espera de equipo|llegando a hospital)', text_low)):
        es_traslado = True
        tipo_tr = 'Traslado Efectivo'
    elif 'traslado' in text_low and not negativa and ('hospital' in text_low or 'clínica' in text_low or 'imss' in text_low):
        es_traslado = True
        tipo_tr = 'Traslado Efectivo'
        
    if es_traslado:
        # Detectar destino
        for hosp, pats in patrones_hosp.items():
            if any(re.search(p, text_low) for p in pats):
                dest.append(hosp)
        dest_str = ", ".join(dest) if dest else "Centro Hospitalario / No especificado"
        
        # Detectar ambulancia
        u = []
        if '208' in text or 'u-208' in text_low or 'u_208' in text_low: u.append('U-208')
        if '098' in text or 'u-098' in text_low: u.append('U-098')
        if '097' in text or 'u-097' in text_low: u.append('U-097')
        u_str = "/".join(u) if u else "Ambulancia Operativa"
        
        traslados_agosto.append({
            'caso_id': row['ID_Caso'],
            'fecha': row['Fecha_Reporte'],
            'hora': row['Hora_Inicio'],
            'unidad': u_str,
            'destino': dest_str,
            'negativa': negativa,
            'resumen': text[:150].replace('\n', ' ')
        })

df_tr_agosto = pd.DataFrame(traslados_agosto)
print(f"Total traslados identificados en casos operativos de Agosto: {len(df_tr_agosto)}")
print("\nDesglose por Destino Hospitalario:")
print(df_tr_agosto['destino'].value_counts())

print("\nDesglose por Unidad de Ambulancia:")
print(df_tr_agosto['unidad'].value_counts())

print("\nPrimeros 10 casos de traslados en Agosto:")
for i, r in df_tr_agosto.head(10).iterrows():
    print(f"- [{r['fecha']} {r['hora']}] ({r['unidad']}) -> {r['destino']}")
    print(f"  Texto: {r['resumen']}")

conn.close()
