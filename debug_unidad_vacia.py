import pandas as pd

df = pd.read_csv('datos_limpios_catalogo.csv', keep_default_na=False)
vacios = df[df['Unidad_Atiende'] == '']
print(f"Total vacios: {len(vacios)}")
for i, r in vacios.head(5).iterrows():
    print(f"No_Folio: {r['No_Folio']} | Paciente: {r['Persona_Trasladada_Paciente']}")
    print(f"Resumen: {r['Resumen_Operativo'][:100]}\n")
