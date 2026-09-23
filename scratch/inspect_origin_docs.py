import openpyxl
import docx
import pandas as pd
import sqlite3
import os

print("=== 1. INSPECCIONANDO 'Documentacion/ORIGEN/100 dias.xlsx' ===")
try:
    wb = openpyxl.load_workbook('Documentacion/ORIGEN/100 dias.xlsx', data_only=True)
    print("Hojas en 100 dias.xlsx:", wb.sheetnames)
    for sheet in wb.sheetnames:
        ws = wb[sheet]
        print(f"\n--- Hoja: {sheet} (filas: {ws.max_row}, cols: {ws.max_column}) ---")
        # Mostrar primeras 15 filas y 10 columnas si no está vacía
        for r in range(1, min(ws.max_row + 1, 16)):
            row_vals = [str(ws.cell(row=r, column=c).value) for c in range(1, min(ws.max_column + 1, 10))]
            if any(v != 'None' for v in row_vals):
                print(f"Fila {r}: {row_vals}")
except Exception as e:
    print("Error 100 dias:", e)

print("\n=== 2. INSPECCIONANDO 'Documentacion/ORIGEN/informe de resultados.docx' ===")
try:
    doc = docx.Document('Documentacion/ORIGEN/informe de resultados.docx')
    print("Total parrafos:", len(doc.paragraphs))
    print("Total tablas:", len(doc.tables))
    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if t and any(w in t.lower() for w in ['traslado', 'emergencia', 'servicio', 'total', 'ambulan']):
            print(f"P{i}: {t}")
    for t_idx, table in enumerate(doc.tables):
        print(f"\nTabla {t_idx} (filas: {len(table.rows)}, cols: {len(table.columns)}):")
        for r in table.rows[:8]:
            print([c.text.strip() for c in r.cells])
except Exception as e:
    print("Error docx:", e)

print("\n=== 3. INSPECCIONANDO 'Documentacion/ORIGEN/R Antonio Rosas-Anel.docx' ===")
try:
    doc2 = docx.Document('Documentacion/ORIGEN/R Antonio Rosas-Anel.docx')
    for i, p in enumerate(doc2.paragraphs):
        t = p.text.strip()
        if t and any(w in t.lower() for w in ['traslado', 'total', 'emergencia', 'medica']):
            print(f"P{i}: {t[:120]}")
except Exception as e:
    print("Error doc2:", e)
