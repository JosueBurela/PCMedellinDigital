import pandas as pd

df = pd.read_excel('Catalogo_Traslados_Medellin_2026.xlsx')
null_pac = df[df['Nombre_Paciente'].isnull()]
print(f"Total filas sin paciente estructurado: {len(null_pac)}")

for i, r in null_pac.head(20).iterrows():
    f = r['Fecha_Mensaje']
    t = str(r['Texto_Original']).replace('\n', ' ')[:120]
    print(f"[{f}] {t}")
