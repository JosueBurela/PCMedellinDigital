with open('c:/Users/burel/OneDrive/Documentos/PCivil Digital/portal/views/salidas.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    start = -1
    for i, line in enumerate(lines):
        if 'def imprimir_reporte_salidas_pdf' in line:
            start = i
            break
    if start != -1:
        print("".join(lines[start:start+50]))
