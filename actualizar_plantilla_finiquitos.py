import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import os

def actualizar_plantilla():
    ruta_archivo = r'C:\Users\burel\Downloads\hojasdecalculoscuriosas\Plantilla_Finiquito_y_Recibo.xlsx'
    
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    
    font_titulo = Font(name='Calibri', size=13, bold=True, color='0A2342')
    font_encabezado_tabla = Font(name='Calibri', size=9.5, bold=True, color='FFFFFF')
    font_negrita = Font(name='Calibri', size=9.5, bold=True, color='000000')
    font_normal = Font(name='Calibri', size=9.5, bold=False, color='000000')
    font_verde = Font(name='Calibri', size=11, bold=True, color='065F46')
    
    fill_azul_oscuro = PatternFill(start_color='0A2342', end_color='0A2342', fill_type='solid')
    fill_azul_marino = PatternFill(start_color='1E3A8A', end_color='1E3A8A', fill_type='solid')
    fill_celeste_captura = PatternFill(start_color='CCF2FF', end_color='CCF2FF', fill_type='solid')
    fill_gris_formula = PatternFill(start_color='EDEDED', end_color='EDEDED', fill_type='solid')
    fill_verde_neto = PatternFill(start_color='CEEFC6', end_color='CEEFC6', fill_type='solid')
    fill_amarillo_suave = PatternFill(start_color='FEF08A', end_color='FEF08A', fill_type='solid')
    
    border_delgado = Border(
        left=Side(style='thin', color='CCCCCC'),
        right=Side(style='thin', color='CCCCCC'),
        top=Side(style='thin', color='CCCCCC'),
        bottom=Side(style='thin', color='CCCCCC')
    )
    
    border_total = Border(
        top=Side(style='thin', color='000000'),
        bottom=Side(style='double', color='000000')
    )
    
    border_recibo = Border(
        left=Side(style='thin', color='94A3B8'),
        right=Side(style='thin', color='94A3B8'),
        top=Side(style='thin', color='94A3B8'),
        bottom=Side(style='thin', color='94A3B8')
    )

    # =========================================================================
    # 1. PESTAÑA: Tarifa_Mensual_SAT
    # =========================================================================
    ws_sat = wb.create_sheet(title='Tarifa_Mensual_SAT')
    ws_sat.views.sheetView[0].showGridLines = True
    
    ws_sat.column_dimensions['A'].width = 17
    ws_sat.column_dimensions['B'].width = 18
    ws_sat.column_dimensions['C'].width = 14
    ws_sat.column_dimensions['D'].width = 15
    ws_sat.column_dimensions['E'].width = 4
    ws_sat.column_dimensions['F'].width = 33
    ws_sat.column_dimensions['G'].width = 14
    
    ws_sat.merge_cells('A1:D1')
    ws_sat['A1'] = "TARIFA OFICIAL MENSUAL DE RETENCION DE ISR (ART. 96 LISR)"
    ws_sat['A1'].font = font_titulo
    ws_sat['A1'].alignment = Alignment(horizontal='left', vertical='center')
    
    ws_sat.merge_cells('F1:G1')
    ws_sat['F1'] = "PARAMETROS FISCALES Y UMA VIGENTE"
    ws_sat['F1'].font = font_titulo
    ws_sat['F1'].alignment = Alignment(horizontal='left', vertical='center')
    
    encabezados_sat = ['Limite Inferior ($)', 'Limite Superior ($)', 'Cuota Fija ($)', '% s/ Excedente']
    for c_idx, enc in enumerate(encabezados_sat, start=1):
        cell = ws_sat.cell(3, c_idx, enc)
        cell.font = font_encabezado_tabla
        cell.fill = fill_azul_oscuro
        cell.alignment = Alignment(horizontal='center', vertical='center')
        
    for c_idx, enc in enumerate(['Parametros UMA / LISR', 'Importe ($)'], start=6):
        cell = ws_sat.cell(3, c_idx, enc)
        cell.font = font_encabezado_tabla
        cell.fill = fill_azul_marino
        cell.alignment = Alignment(horizontal='center', vertical='center')
        
    filas_tarifa = [
        (0.01, 746.04, 0.00, 0.0192),
        (746.05, 6332.05, 14.32, 0.0640),
        (6332.06, 11128.01, 371.83, 0.1088),
        (11128.02, 12935.82, 893.14, 0.1600),
        (12935.83, 15487.71, 1182.41, 0.1792),
        (15487.72, 31236.49, 1640.18, 0.2136),
        (31236.50, 49233.00, 5004.12, 0.2352),
        (49233.01, 93993.90, 9236.89, 0.3000),
        (93993.91, 125325.20, 22665.17, 0.3200),
        (125325.21, 375975.61, 32691.18, 0.3400),
        (375975.62, 999999999.00, 117912.32, 0.3500)
    ]
    
    for r_idx, row in enumerate(filas_tarifa, start=4):
        for c_idx, val in enumerate(row, start=1):
            cell = ws_sat.cell(r_idx, c_idx, val)
            cell.font = font_normal
            cell.border = border_delgado
            if c_idx == 4:
                cell.number_format = '0.00%'
                cell.alignment = Alignment(horizontal='right')
            else:
                cell.number_format = '$#,##0.00'
                cell.alignment = Alignment(horizontal='right')
                
    ws_sat['F4'] = "UMA Diaria Vigente:"
    ws_sat['G4'] = 108.57
    ws_sat['F5'] = "Exencion Aguinaldo (30 UMAs):"
    ws_sat['G5'] = "=G4*30"
    ws_sat['F6'] = "Exencion Prima Vac. (15 UMAs):"
    ws_sat['G6'] = "=G4*15"
    ws_sat['F7'] = "Exencion Separacion/Ano (90 UMAs):"
    ws_sat['G7'] = "=G4*90"
    ws_sat['F8'] = "Tope Prima Antiguedad (2 UMAs):"
    ws_sat['G8'] = "=G4*2"
    ws_sat['F9'] = "3 UMAs Diarias (Limite IMSS):"
    ws_sat['G9'] = "=G4*3"
    
    for r in range(4, 10):
        cell_f = ws_sat.cell(r, 6)
        cell_g = ws_sat.cell(r, 7)
        cell_f.font = font_negrita
        cell_f.border = border_delgado
        cell_g.font = font_normal
        cell_g.border = border_delgado
        cell_g.number_format = '$#,##0.00'
        cell_g.alignment = Alignment(horizontal='right')

    # =========================================================================
    # 2. PESTAÑA: Tabla_IMSS
    # =========================================================================
    ws_imss = wb.create_sheet(title='Tabla_IMSS')
    ws_imss.views.sheetView[0].showGridLines = True
    
    ws_imss.column_dimensions['A'].width = 40
    ws_imss.column_dimensions['B'].width = 20
    ws_imss.column_dimensions['C'].width = 18
    ws_imss.column_dimensions['D'].width = 18
    ws_imss.column_dimensions['E'].width = 18
    ws_imss.column_dimensions['F'].width = 25
    
    ws_imss.merge_cells('A1:F1')
    ws_imss['A1'] = "TABLA OFICIAL DE CUOTAS OBRERO-PATRONALES DEL IMSS (LEY DEL SEGURO SOCIAL)"
    ws_imss['A1'].font = font_titulo
    ws_imss['A1'].alignment = Alignment(horizontal='left', vertical='center')
    
    ws_imss.merge_cells('A2:F2')
    ws_imss['A2'] = "Desglose por rama de aseguramiento para el calculo automatico de la cuota obrera retenida en finiquitos."
    ws_imss['A2'].font = Font(name='Calibri', size=10, italic=True, color='475569')
    
    encabezados_imss = [
        'Ramo de Aseguramiento',
        'Base de Cotizacion',
        'Cuota Patronal (%)',
        'Cuota Obrera (%)',
        'Total Cuota (%)',
        'Fundamento Legal LSS'
    ]
    for c_idx, enc in enumerate(encabezados_imss, start=1):
        cell = ws_imss.cell(4, c_idx, enc)
        cell.font = font_encabezado_tabla
        cell.fill = fill_azul_oscuro
        cell.alignment = Alignment(horizontal='center', vertical='center')
        
    filas_imss = [
        ("Enf. y Mat. - Prestaciones Especie (Cuota Fija)", "1 UMA", 0.2040, 0.0000, "=C5+D5", "Art. 106 Fracc. I"),
        ("Enf. y Mat. - Exc. > 3 UMA", "Excedente s/ 3 UMA", 0.0110, 0.0040, "=C6+D6", "Art. 106 Fracc. II"),
        ("Enf. y Mat. - Prestaciones en Dinero", "SBC", 0.0070, 0.0025, "=C7+D7", "Art. 107"),
        ("Enf. y Mat. - Gastos Medicos Pensionados", "SBC", 0.0105, 0.00375, "=C8+D8", "Art. 25"),
        ("Invalidez y Vida", "SBC", 0.0175, 0.00625, "=C9+D9", "Art. 147"),
        ("Retiro (SAR)", "SBC", 0.0200, 0.0000, "=C10+D10", "Art. 168 Fracc. I"),
        ("Cesantia en Edad Avanzada y Vejez", "SBC", 0.0424, 0.01125, "=C11+D11", "Art. 168 Fracc. II"),
        ("Riesgos de Trabajo (Prima Media / Empresa)", "SBC", 0.0054355, 0.0000, "=C12+D12", "Art. 71-73"),
        ("Guarderias y Prestaciones Sociales", "SBC", 0.0100, 0.0000, "=C13+D13", "Art. 211")
    ]
    
    for r_idx, row in enumerate(filas_imss, start=5):
        for c_idx, val in enumerate(row, start=1):
            cell = ws_imss.cell(r_idx, c_idx, val)
            cell.font = font_normal
            cell.border = border_delgado
            if c_idx in (3, 4, 5):
                cell.number_format = '0.000%' if c_idx == 4 and r_idx in (8, 9) else '0.00%'
                cell.alignment = Alignment(horizontal='right')
            elif c_idx == 6:
                cell.alignment = Alignment(horizontal='center')
                cell.font = Font(name='Calibri', size=9, italic=True, color='475569')
            else:
                cell.alignment = Alignment(horizontal='left')
                
    ws_imss.cell(14, 1, "TOTAL CUOTAS GENERALES:").font = font_negrita
    ws_imss.cell(14, 1).alignment = Alignment(horizontal='right')
    ws_imss.cell(14, 3, "=SUM(C5:C13)").font = font_negrita
    ws_imss.cell(14, 3).number_format = '0.00%'
    ws_imss.cell(14, 4, "=SUM(D5:D13)").font = font_negrita
    ws_imss.cell(14, 4).number_format = '0.000%'
    ws_imss.cell(14, 5, "=SUM(E5:E13)").font = font_negrita
    ws_imss.cell(14, 5).number_format = '0.00%'
    for c in range(1, 7):
        ws_imss.cell(14, c).border = border_total
        
    ws_imss.merge_cells('A16:D16')
    ws_imss['A16'] = "RESUMEN DE CUOTA OBRERA APLICABLE EN LA NOMINA / FINIQUITO"
    ws_imss['A16'].font = font_titulo
    ws_imss['A16'].alignment = Alignment(horizontal='left')
    
    ws_imss['A17'] = "Tasa Fija Cuota Obrera sobre SBC (Dinero + GMP + Invalidez + Cesantia):"
    ws_imss['A17'].font = font_negrita
    ws_imss['D17'] = "=D7+D8+D9+D11" # 2.375%
    ws_imss['D17'].font = font_negrita
    ws_imss['D17'].number_format = '0.000%'
    ws_imss['D17'].fill = fill_amarillo_suave
    ws_imss['E17'] = "2.375% s/ SBC"
    ws_imss['E17'].font = Font(name='Calibri', size=9, italic=True)
    
    ws_imss['A18'] = "Tasa Adicional Obrero por Excedente de 3 UMAs:"
    ws_imss['A18'].font = font_negrita
    ws_imss['D18'] = "=D6" # 0.400%
    ws_imss['D18'].font = font_negrita
    ws_imss['D18'].number_format = '0.000%'
    ws_imss['D18'].fill = fill_amarillo_suave
    ws_imss['E18'] = "0.400% s/ Excedente"
    ws_imss['E18'].font = Font(name='Calibri', size=9, italic=True)
    
    ws_imss['A19'] = "Valor Limite Excedente (3 UMAs Diarias):"
    ws_imss['A19'].font = font_negrita
    ws_imss['D19'] = "=Tarifa_Mensual_SAT!G9"
    ws_imss['D19'].font = font_negrita
    ws_imss['D19'].number_format = '$#,##0.00'
    ws_imss['D19'].fill = fill_amarillo_suave
    ws_imss['E19'] = "Limite de 3 UMAs diarias"
    ws_imss['E19'].font = Font(name='Calibri', size=9, italic=True)

    for r in range(17, 20):
        for c in range(1, 6):
            ws_imss.cell(r, c).border = border_delgado

    # =========================================================================
    # 3. PESTAÑA: CALCULO_FINIQUITO
    # =========================================================================
    ws_calc = wb.create_sheet(title='CALCULO_FINIQUITO')
    ws_calc.views.sheetView[0].showGridLines = True
    
    ws_calc.column_dimensions['A'].width = 28
    ws_calc.column_dimensions['B'].width = 11
    ws_calc.column_dimensions['C'].width = 13
    ws_calc.column_dimensions['D'].width = 11
    ws_calc.column_dimensions['E'].width = 9
    ws_calc.column_dimensions['F'].width = 11
    ws_calc.column_dimensions['G'].width = 12
    ws_calc.column_dimensions['H'].width = 16

    ws_calc['A2'] = "FECHA DE INGRESO"
    ws_calc['A2'].font = font_negrita
    ws_calc.merge_cells('C2:D2')
    ws_calc['C2'].fill = fill_celeste_captura
    ws_calc['C2'].alignment = Alignment(horizontal='center')
    ws_calc['C2'].border = border_delgado
    
    ws_calc['F2'] = "Salario"
    ws_calc['F2'].font = font_negrita
    ws_calc['F2'].alignment = Alignment(horizontal='right')
    ws_calc.merge_cells('G2:H2')
    ws_calc['G2'].fill = fill_celeste_captura
    ws_calc['G2'].alignment = Alignment(horizontal='right')
    ws_calc['G2'].number_format = '$#,##0.00'
    ws_calc['G2'].border = border_delgado
    
    ws_calc['A3'] = "FECHA ULTIMO DIA TRABAJADO"
    ws_calc['A3'].font = font_negrita
    ws_calc.merge_cells('C3:D3')
    ws_calc['C3'].fill = fill_celeste_captura
    ws_calc['C3'].alignment = Alignment(horizontal='center')
    ws_calc['C3'].border = border_delgado

    headers_calc = [
        (1, 'PERCEPCIONES'),
        (2, 'DIAS'),
        (3, 'SALARIO'),
        (6, 'D-ANOS'),
        (7, 'D-TRABAJ.'),
        (8, 'RESULTADO')
    ]
    for col_idx, text in headers_calc:
        c = ws_calc.cell(5, col_idx, text)
        c.font = font_negrita
        c.alignment = Alignment(horizontal='center' if col_idx > 1 else 'left')

    # R6: Salarios
    ws_calc['A6'] = "SALARIOS"
    ws_calc['B6'].fill = fill_celeste_captura
    ws_calc['B6'].alignment = Alignment(horizontal='right')
    ws_calc['B6'].number_format = '0.00'
    ws_calc['C6'] = '=IF(G2>0, G2, "")'
    ws_calc['C6'].alignment = Alignment(horizontal='right')
    ws_calc['C6'].number_format = '$#,##0.00'
    ws_calc['H6'] = '=IF(OR(B6="", C6=""), 0, ROUND(B6*C6, 2))'
    ws_calc['H6'].alignment = Alignment(horizontal='right')
    ws_calc['H6'].number_format = '$#,##0.00'
    
    # R7: Incentivo
    ws_calc['A7'] = "INCENTIVO"
    ws_calc['B7'].fill = fill_celeste_captura
    ws_calc['B7'].alignment = Alignment(horizontal='right')
    ws_calc['C7'].fill = fill_celeste_captura
    ws_calc['C7'].alignment = Alignment(horizontal='right')
    ws_calc['H7'] = '=IF(OR(B7="", C7=""), 0, ROUND(B7*C7, 2))'
    ws_calc['H7'].alignment = Alignment(horizontal='right')
    ws_calc['H7'].number_format = '$#,##0.00'

    # R8: Tiempo Extra
    ws_calc['A8'] = "TIEMPO EXTRA"
    ws_calc['B8'].fill = fill_celeste_captura
    ws_calc['C8'] = "-"
    ws_calc['C8'].alignment = Alignment(horizontal='center')
    ws_calc['H8'] = '=IF(B8>0, B8, 0)'
    ws_calc['H8'].alignment = Alignment(horizontal='right')
    ws_calc['H8'].number_format = '$#,##0.00'

    # R10 & R11: Vacaciones 1er Período
    ws_calc['A10'] = "VACACIONES"
    ws_calc['B10'].fill = fill_celeste_captura
    ws_calc['B10'].alignment = Alignment(horizontal='right')
    ws_calc['C10'] = '=IF(G2>0, G2, "")'
    ws_calc['C10'].alignment = Alignment(horizontal='right')
    ws_calc['C10'].number_format = '$#,##0.00'
    ws_calc['D10'] = '=IF(OR(B10="", C10=""), "", B10*C10)'
    ws_calc['D10'].alignment = Alignment(horizontal='right')
    ws_calc['D10'].number_format = '$#,##0.00'
    ws_calc['E10'] = 365
    ws_calc['E10'].alignment = Alignment(horizontal='center')
    ws_calc['F10'] = '=IF(OR(D10="", E10=""), "", ROUND(D10/E10, 2))'
    ws_calc['F10'].alignment = Alignment(horizontal='right')
    ws_calc['G10'].fill = fill_celeste_captura
    ws_calc['G10'].alignment = Alignment(horizontal='right')
    ws_calc['H10'] = '=IF(OR(F10="", G10=""), 0, ROUND(F10*G10, 2))'
    ws_calc['H10'].alignment = Alignment(horizontal='right')
    ws_calc['H10'].number_format = '$#,##0.00'

    ws_calc['A11'] = "PRIMA VACACIONAL"
    ws_calc['F11'].fill = fill_celeste_captura
    ws_calc['F11'].alignment = Alignment(horizontal='right')
    ws_calc['F11'].number_format = '$#,##0.00'
    ws_calc['G11'] = 0.25
    ws_calc['G11'].alignment = Alignment(horizontal='right')
    ws_calc['G11'].number_format = '0%'
    ws_calc['H11'] = '=IF(ISNUMBER(F11), ROUND(F11*G11, 2), 0)'
    ws_calc['H11'].alignment = Alignment(horizontal='right')
    ws_calc['H11'].number_format = '$#,##0.00'

    # R13 & R14: Vacaciones 2do Período
    ws_calc['A13'] = "VACACIONES"
    ws_calc['B13'].fill = fill_celeste_captura
    ws_calc['B13'].alignment = Alignment(horizontal='right')
    ws_calc['C13'] = '=IF(G2>0, G2, "")'
    ws_calc['C13'].alignment = Alignment(horizontal='right')
    ws_calc['C13'].number_format = '$#,##0.00'
    ws_calc['D13'] = '=IF(OR(B13="", C13=""), "", B13*C13)'
    ws_calc['D13'].alignment = Alignment(horizontal='right')
    ws_calc['D13'].number_format = '$#,##0.00'
    ws_calc['E13'] = 365
    ws_calc['E13'].alignment = Alignment(horizontal='center')
    ws_calc['F13'] = '=IF(OR(D13="", E13=""), "", ROUND(D13/E13, 2))'
    ws_calc['F13'].alignment = Alignment(horizontal='right')
    ws_calc['G13'].fill = fill_celeste_captura
    ws_calc['G13'].alignment = Alignment(horizontal='right')
    ws_calc['H13'] = '=IF(OR(F13="", G13=""), 0, ROUND(F13*G13, 2))'
    ws_calc['H13'].alignment = Alignment(horizontal='right')
    ws_calc['H13'].number_format = '$#,##0.00'

    ws_calc['A14'] = "PRIMA VACACIONAL"
    ws_calc['F14'] = '=IF(H13>0, H13, "")'
    ws_calc['F14'].alignment = Alignment(horizontal='right')
    ws_calc['F14'].number_format = '$#,##0.00'
    ws_calc['G14'] = 0.25
    ws_calc['G14'].alignment = Alignment(horizontal='right')
    ws_calc['G14'].number_format = '0%'
    ws_calc['H14'] = '=IF(ISNUMBER(F14), ROUND(F14*G14, 2), 0)'
    ws_calc['H14'].alignment = Alignment(horizontal='right')
    ws_calc['H14'].number_format = '$#,##0.00'

    # R15 & R16: Vacaciones 3er Período
    ws_calc['A15'] = "VACACIONES"
    ws_calc['B15'].fill = fill_celeste_captura
    ws_calc['B15'].alignment = Alignment(horizontal='right')
    ws_calc['C15'] = '=IF(G2>0, G2, "")'
    ws_calc['C15'].alignment = Alignment(horizontal='right')
    ws_calc['C15'].number_format = '$#,##0.00'
    ws_calc['D15'] = '=IF(OR(B15="", C15=""), "", B15*C15)'
    ws_calc['D15'].alignment = Alignment(horizontal='right')
    ws_calc['D15'].number_format = '$#,##0.00'
    ws_calc['E15'] = 365
    ws_calc['E15'].alignment = Alignment(horizontal='center')
    ws_calc['F15'] = '=IF(OR(D15="", E15=""), "", ROUND(D15/E15, 2))'
    ws_calc['F15'].alignment = Alignment(horizontal='right')
    ws_calc['G15'].fill = fill_celeste_captura
    ws_calc['G15'].alignment = Alignment(horizontal='right')
    ws_calc['H15'] = '=IF(OR(F15="", G15=""), 0, ROUND(F15*G15, 2))'
    ws_calc['H15'].alignment = Alignment(horizontal='right')
    ws_calc['H15'].number_format = '$#,##0.00'

    ws_calc['A16'] = "PRIMA VACACIONAL"
    ws_calc['F16'] = '=IF(H15>0, H15, "")'
    ws_calc['F16'].alignment = Alignment(horizontal='right')
    ws_calc['F16'].number_format = '$#,##0.00'
    ws_calc['G16'] = 0.25
    ws_calc['G16'].alignment = Alignment(horizontal='right')
    ws_calc['G16'].number_format = '0%'
    ws_calc['H16'] = '=IF(ISNUMBER(F16), ROUND(F16*G16, 2), 0)'
    ws_calc['H16'].alignment = Alignment(horizontal='right')
    ws_calc['H16'].number_format = '$#,##0.00'

    # R17: Aguinaldo
    ws_calc['A17'] = "AGUINALDO"
    ws_calc['B17'].fill = fill_celeste_captura
    ws_calc['B17'].alignment = Alignment(horizontal='right')
    ws_calc['C17'] = '=IF(G2>0, G2, "")'
    ws_calc['C17'].alignment = Alignment(horizontal='right')
    ws_calc['C17'].number_format = '$#,##0.00'
    ws_calc['D17'] = '=IF(OR(B17="", C17=""), "", B17*C17)'
    ws_calc['D17'].alignment = Alignment(horizontal='right')
    ws_calc['D17'].number_format = '$#,##0.00'
    ws_calc['E17'] = 365
    ws_calc['E17'].alignment = Alignment(horizontal='center')
    ws_calc['F17'] = '=IF(OR(D17="", E17=""), "", ROUND(D17/E17, 2))'
    ws_calc['F17'].alignment = Alignment(horizontal='right')
    ws_calc['G17'].fill = fill_celeste_captura
    ws_calc['G17'].alignment = Alignment(horizontal='right')
    ws_calc['H17'] = '=IF(OR(F17="", G17=""), 0, ROUND(F17*G17, 2))'
    ws_calc['H17'].alignment = Alignment(horizontal='right')
    ws_calc['H17'].number_format = '$#,##0.00'

    # R18: Gratificación Finiquito
    ws_calc['A18'] = "Gratificacion Finiquito"
    ws_calc['B18'].fill = fill_celeste_captura
    ws_calc['B18'].alignment = Alignment(horizontal='right')
    ws_calc['C18'] = '=IF(G2>0, G2, "")'
    ws_calc['C18'].alignment = Alignment(horizontal='right')
    ws_calc['C18'].number_format = '$#,##0.00'
    ws_calc['H18'] = '=IF(OR(B18="", C18=""), 0, ROUND(B18*C18, 2))'
    ws_calc['H18'].alignment = Alignment(horizontal='right')
    ws_calc['H18'].number_format = '$#,##0.00'

    # -------------------------------------------------------------
    # NUEVA SECCIÓN: INDEMNIZACIÓN Y PRIMA DE ANTIGÜEDAD (R19 y R20)
    # -------------------------------------------------------------
    ws_calc['A19'] = "INDEMNIZACION CONSTITUCIONAL"
    ws_calc['A19'].font = Font(name='Calibri', size=9.5, bold=True, color='0A2342')
    ws_calc['B19'].fill = fill_celeste_captura
    ws_calc['B19'].alignment = Alignment(horizontal='right')
    ws_calc['B19'].number_format = '0.00'
    ws_calc['C19'] = '=IF(G2>0, G2, "")'
    ws_calc['C19'].alignment = Alignment(horizontal='right')
    ws_calc['C19'].number_format = '$#,##0.00'
    ws_calc['D19'] = "90 Dias LFT"
    ws_calc['D19'].font = Font(name='Calibri', size=8.5, italic=True, color='64748B')
    ws_calc['D19'].alignment = Alignment(horizontal='center')
    ws_calc['H19'] = '=IF(OR(B19="", C19=""), 0, ROUND(B19*C19, 2))'
    ws_calc['H19'].alignment = Alignment(horizontal='right')
    ws_calc['H19'].number_format = '$#,##0.00'

    ws_calc['A20'] = "PRIMA DE ANTIGUEDAD"
    ws_calc['A20'].font = Font(name='Calibri', size=9.5, bold=True, color='0A2342')
    ws_calc['B20'].fill = fill_celeste_captura
    ws_calc['B20'].alignment = Alignment(horizontal='right')
    ws_calc['B20'].number_format = '0.00'
    ws_calc['C20'] = '=IF(G2>0, MIN(G2, Tarifa_Mensual_SAT!$G$8), "")'
    ws_calc['C20'].alignment = Alignment(horizontal='right')
    ws_calc['C20'].number_format = '$#,##0.00'
    ws_calc['D20'] = "Tope 2 UMAs"
    ws_calc['D20'].font = Font(name='Calibri', size=8.5, italic=True, color='64748B')
    ws_calc['D20'].alignment = Alignment(horizontal='center')
    ws_calc['H20'] = '=IF(OR(B20="", C20=""), 0, ROUND(B20*C20, 2))'
    ws_calc['H20'].alignment = Alignment(horizontal='right')
    ws_calc['H20'].number_format = '$#,##0.00'

    # R21: ISPT A FAVOR
    ws_calc['A21'] = "ISPT A FAVOR"
    ws_calc['H21'].fill = fill_celeste_captura
    ws_calc['H21'].alignment = Alignment(horizontal='right')
    ws_calc['H21'].number_format = '$#,##0.00'

    # R22: TOTAL DE PERCEPCIONES
    ws_calc['A22'] = "TOTAL DE PERCEPCIONES"
    ws_calc['A22'].font = font_negrita
    ws_calc['H22'] = '=SUM(H6:H8, H10:H11, H13:H14, H15:H16, H17:H21)'
    ws_calc['H22'].font = font_negrita
    ws_calc['H22'].alignment = Alignment(horizontal='right')
    ws_calc['H22'].number_format = '$#,##0.00'
    ws_calc['H22'].border = border_total

    # -------------------------------------------------------------
    # SECCIÓN DEDUCCIONES (R24 a R32)
    # -------------------------------------------------------------
    # R24: ISPT
    ws_calc['A24'] = "ISPT"
    ws_calc['A24'].font = font_negrita
    formula_ispt = (
        '=IF(H22<=0, 0, _xlfn.LET('
        '_xlpm.exAgui, MIN(N(H17), Tarifa_Mensual_SAT!$G$5), '
        '_xlpm.exPrima, MIN(SUM(N(H11), N(H14), N(H16)), Tarifa_Mensual_SAT!$G$6), '
        '_xlpm.anios, MAX(1, IF(OR(C2="", C3=""), 1, ROUND((C3-C2)/365.25, 0))), '
        '_xlpm.exSep, MIN(SUM(N(H19), N(H20)), _xlpm.anios * Tarifa_Mensual_SAT!$G$7), '
        '_xlpm.base, MAX(0, H22 - _xlpm.exAgui - _xlpm.exPrima - _xlpm.exSep), '
        'IF(_xlpm.base<=0, 0, ROUND(VLOOKUP(_xlpm.base, Tarifa_Mensual_SAT!$A$4:$D$14, 3, TRUE) + '
        '((_xlpm.base - VLOOKUP(_xlpm.base, Tarifa_Mensual_SAT!$A$4:$D$14, 1, TRUE)) * '
        'VLOOKUP(_xlpm.base, Tarifa_Mensual_SAT!$A$4:$D$14, 4, TRUE)), 2))))'
    )
    ws_calc['H24'] = formula_ispt
    ws_calc['H24'].font = font_negrita
    ws_calc['H24'].fill = fill_gris_formula
    ws_calc['H24'].alignment = Alignment(horizontal='right')
    ws_calc['H24'].number_format = '$#,##0.00'

    # R25: IMSS (AUTOMATIZADO CON TABLA_IMSS)
    ws_calc['A25'] = "IMSS"
    ws_calc['A25'].font = font_negrita
    formula_imss = (
        '=IF(OR(B6="", C6=""), 0, ROUND('
        'B6 * ((C6 * Tabla_IMSS!$D$17) + IF(C6 > Tabla_IMSS!$D$19, (C6 - Tabla_IMSS!$D$19) * Tabla_IMSS!$D$18, 0)), 2))'
    )
    ws_calc['H25'] = formula_imss
    ws_calc['H25'].font = font_negrita
    ws_calc['H25'].fill = fill_gris_formula
    ws_calc['H25'].alignment = Alignment(horizontal='right')
    ws_calc['H25'].number_format = '$#,##0.00'
    ws_calc['B25'] = "Automatico s/ Tabla IMSS"
    ws_calc['B25'].font = Font(name='Calibri', size=8, italic=True, color='64748B')

    # R26 a R31: Otras Deducciones
    deducciones_list = [
        (26, "INFONAVIT"),
        (27, "DEUDORES"),
        (28, "INFONACOT"),
        (29, "PENSION ALIMENTICIA"),
        (30, "GASTOS A COMPROBAR"),
        (31, "CUOTA SINDICAL")
    ]
    for r_idx, nom in deducciones_list:
        ws_calc.cell(r_idx, 1, nom).font = font_normal
        c_h = ws_calc.cell(r_idx, 8)
        c_h.fill = fill_celeste_captura
        c_h.alignment = Alignment(horizontal='right')
        c_h.number_format = '$#,##0.00'

    # R32: TOTAL DE DEDUCCIONES
    ws_calc['A32'] = "TOTAL DE DEDUCCIONES"
    ws_calc['A32'].font = font_negrita
    ws_calc['H32'] = '=SUM(H24:H31)'
    ws_calc['H32'].font = font_negrita
    ws_calc['H32'].alignment = Alignment(horizontal='right')
    ws_calc['H32'].number_format = '$#,##0.00'
    ws_calc['H32'].border = border_total

    # R34: NETO A PAGAR
    ws_calc['A34'] = "Neto a pagar"
    ws_calc['A34'].font = font_titulo
    ws_calc['H34'] = '=H22-H32'
    ws_calc['H34'].font = font_verde
    ws_calc['H34'].fill = fill_verde_neto
    ws_calc['H34'].alignment = Alignment(horizontal='right')
    ws_calc['H34'].number_format = '$#,##0.00'
    ws_calc['H34'].border = border_total

    campos_empleado = [
        (37, "Nombre"),
        (38, "Puesto"),
        (39, "Clave"),
        (40, "Motivo de baja")
    ]
    for r_idx, label in campos_empleado:
        ws_calc.cell(r_idx, 1, label).font = font_negrita
        ws_calc.merge_cells(start_row=r_idx, start_column=3, end_row=r_idx, end_column=6)
        c = ws_calc.cell(r_idx, 3)
        c.fill = fill_celeste_captura
        c.border = border_delgado
        c.alignment = Alignment(horizontal='left')

    ws_calc.merge_cells('A42:D42')
    ws_calc['A42'] = "Autorizado por FGC."
    ws_calc['A42'].font = font_negrita

    # =========================================================================
    # 4. PESTAÑA: RECIBO_FINIQUITO
    # =========================================================================
    ws_rec = wb.create_sheet(title='RECIBO_FINIQUITO')
    ws_rec.views.sheetView[0].showGridLines = True
    
    ws_rec.column_dimensions['A'].width = 15
    ws_rec.column_dimensions['B'].width = 19
    ws_rec.column_dimensions['C'].width = 14
    ws_rec.column_dimensions['D'].width = 4
    ws_rec.column_dimensions['E'].width = 15
    ws_rec.column_dimensions['F'].width = 19
    ws_rec.column_dimensions['G'].width = 14

    ws_rec.merge_cells('A1:G1')
    ws_rec['A1'] = "COMERCIALIZADORA DE PRODUCTOS CERVECEROS, S.A. DE C.V."
    ws_rec['A1'].font = font_titulo
    ws_rec['A1'].alignment = Alignment(horizontal='center', vertical='center')

    ws_rec.merge_cells('A2:G2')
    ws_rec['A2'] = "RECIBO DE FINIQUITO Y LIQUIDACION LABORAL"
    ws_rec['A2'].font = Font(name='Calibri', size=11, bold=True, color='D97706')
    ws_rec['A2'].alignment = Alignment(horizontal='center', vertical='center')

    ws_rec['A4'] = "TRABAJADOR:"
    ws_rec['A4'].font = font_negrita
    ws_rec.merge_cells('B4:D4')
    ws_rec['B4'] = '=IF(CALCULO_FINIQUITO!C37="","",CALCULO_FINIQUITO!C37)'
    ws_rec['B4'].font = font_normal
    ws_rec['E4'] = "CLAVE NOMINA:"
    ws_rec['E4'].font = font_negrita
    ws_rec.merge_cells('F4:G4')
    ws_rec['F4'] = '=IF(CALCULO_FINIQUITO!C39="","",CALCULO_FINIQUITO!C39)'
    ws_rec['F4'].font = font_normal

    ws_rec['A5'] = "PUESTO:"
    ws_rec['A5'].font = font_negrita
    ws_rec.merge_cells('B5:D5')
    ws_rec['B5'] = '=IF(CALCULO_FINIQUITO!C38="","",CALCULO_FINIQUITO!C38)'
    ws_rec['B5'].font = font_normal
    ws_rec['E5'] = "SALARIO DIARIO:"
    ws_rec['E5'].font = font_negrita
    ws_rec.merge_cells('F5:G5')
    ws_rec['F5'] = '=IF(CALCULO_FINIQUITO!G2="","",CALCULO_FINIQUITO!G2)'
    ws_rec['F5'].font = font_normal
    ws_rec['F5'].number_format = '$#,##0.00'

    ws_rec['A6'] = "FECHA INGRESO:"
    ws_rec['A6'].font = font_negrita
    ws_rec['B6'] = '=IF(CALCULO_FINIQUITO!C2="","",CALCULO_FINIQUITO!C2)'
    ws_rec['C6'] = "FECHA BAJA:"
    ws_rec['C6'].font = font_negrita
    ws_rec['D6'] = '=IF(CALCULO_FINIQUITO!C3="","",CALCULO_FINIQUITO!C3)'
    ws_rec['E6'] = "MOTIVO DE BAJA:"
    ws_rec['E6'].font = font_negrita
    ws_rec.merge_cells('F6:G6')
    ws_rec['F6'] = '=IF(CALCULO_FINIQUITO!C40="","",CALCULO_FINIQUITO!C40)'

    for r in range(4, 7):
        for c in range(1, 8):
            ws_rec.cell(r, c).border = border_recibo

    ws_rec.merge_cells('A8:B8')
    ws_rec['A8'] = "CONCEPTO PERCEPCION"
    ws_rec['A8'].font = font_encabezado_tabla
    ws_rec['A8'].fill = fill_azul_oscuro
    ws_rec['A8'].alignment = Alignment(horizontal='center', vertical='center')

    ws_rec['C8'] = "IMPORTE"
    ws_rec['C8'].font = font_encabezado_tabla
    ws_rec['C8'].fill = fill_azul_oscuro
    ws_rec['C8'].alignment = Alignment(horizontal='center', vertical='center')

    ws_rec.merge_cells('E8:F8')
    ws_rec['E8'] = "CONCEPTO DEDUCCION"
    ws_rec['E8'].font = font_encabezado_tabla
    ws_rec['E8'].fill = fill_azul_oscuro
    ws_rec['E8'].alignment = Alignment(horizontal='center', vertical='center')

    ws_rec['G8'] = "IMPORTE"
    ws_rec['G8'].font = font_encabezado_tabla
    ws_rec['G8'].fill = fill_azul_oscuro
    ws_rec['G8'].alignment = Alignment(horizontal='center', vertical='center')

    conceptos_recibo = [
        ("Salarios Ordinarios", "=CALCULO_FINIQUITO!H6", "Retencion I.S.R. (Art. 96)", "=CALCULO_FINIQUITO!H24"),
        ("Incentivos y Bonos", "=IF(CALCULO_FINIQUITO!H7=\"\", 0, CALCULO_FINIQUITO!H7)", "Cuota Obrera I.M.S.S.", "=IF(CALCULO_FINIQUITO!H25=\"\", 0, CALCULO_FINIQUITO!H25)"),
        ("Tiempo Extraordinario", "=IF(CALCULO_FINIQUITO!H8=\"\", 0, CALCULO_FINIQUITO!H8)", "Amortizacion Credito INFONAVIT", "=IF(CALCULO_FINIQUITO!H26=\"\", 0, CALCULO_FINIQUITO!H26)"),
        ("Vacaciones Pendientes / Prop.", "=CALCULO_FINIQUITO!H10+CALCULO_FINIQUITO!H13+CALCULO_FINIQUITO!H15", "Deudores Diversos / Prestamos", "=IF(CALCULO_FINIQUITO!H27=\"\", 0, CALCULO_FINIQUITO!H27)"),
        ("Prima Vacacional Legal", "=CALCULO_FINIQUITO!H11+CALCULO_FINIQUITO!H14+CALCULO_FINIQUITO!H16", "Credito FONACOT", "=IF(CALCULO_FINIQUITO!H28=\"\", 0, CALCULO_FINIQUITO!H28)"),
        ("Aguinaldo Proporcional", "=CALCULO_FINIQUITO!H17", "Pension Alimenticia", "=IF(CALCULO_FINIQUITO!H29=\"\", 0, CALCULO_FINIQUITO!H29)"),
        ("Gratificacion Finiquito", "=CALCULO_FINIQUITO!H18", "Gastos a Comprobar", "=IF(CALCULO_FINIQUITO!H30=\"\", 0, CALCULO_FINIQUITO!H30)"),
        ("Indemnizacion Constitucional", "=CALCULO_FINIQUITO!H19", "Cuota Sindical", "=IF(CALCULO_FINIQUITO!H31=\"\", 0, CALCULO_FINIQUITO!H31)"),
        ("Prima de Antiguedad", "=CALCULO_FINIQUITO!H20", "Otros Descuentos / Caja Chica", "0"),
        ("ISPT a Favor", "=IF(CALCULO_FINIQUITO!H21=\"\", 0, CALCULO_FINIQUITO!H21)", "-", "0")
    ]

    for idx, (p_nom, p_form, d_nom, d_form) in enumerate(conceptos_recibo, start=9):
        ws_rec.merge_cells(start_row=idx, start_column=1, end_row=idx, end_column=2)
        cell_p_nom = ws_rec.cell(idx, 1, p_nom)
        cell_p_nom.font = font_normal
        cell_p_nom.border = border_recibo
        
        cell_p_val = ws_rec.cell(idx, 3, p_form)
        cell_p_val.font = font_normal
        cell_p_val.border = border_recibo
        cell_p_val.number_format = '$#,##0.00'
        cell_p_val.alignment = Alignment(horizontal='right')
        
        ws_rec.merge_cells(start_row=idx, start_column=5, end_row=idx, end_column=6)
        cell_d_nom = ws_rec.cell(idx, 5, d_nom)
        cell_d_nom.font = font_normal
        cell_d_nom.border = border_recibo
        
        cell_d_val = ws_rec.cell(idx, 7, float(d_form) if d_form.isnumeric() else d_form)
        cell_d_val.font = font_normal
        cell_d_val.border = border_recibo
        cell_d_val.number_format = '$#,##0.00'
        cell_d_val.alignment = Alignment(horizontal='right')

    ws_rec.merge_cells('A19:B19')
    ws_rec['A19'] = "TOTAL PERCEPCIONES"
    ws_rec['A19'].font = font_negrita
    ws_rec['C19'] = "=CALCULO_FINIQUITO!H22"
    ws_rec['C19'].font = font_negrita
    ws_rec['C19'].number_format = '$#,##0.00'
    ws_rec['C19'].alignment = Alignment(horizontal='right')
    
    ws_rec.merge_cells('E19:F19')
    ws_rec['E19'] = "TOTAL DEDUCCIONES"
    ws_rec['E19'].font = font_negrita
    ws_rec['G19'] = "=CALCULO_FINIQUITO!H32"
    ws_rec['G19'].font = font_negrita
    ws_rec['G19'].number_format = '$#,##0.00'
    ws_rec['G19'].alignment = Alignment(horizontal='right')
    
    for c in range(1, 8):
        ws_rec.cell(19, c).border = border_total

    ws_rec.merge_cells('A21:D21')
    ws_rec['A21'] = "NETO A RECIBIR EN EFECTIVO:"
    ws_rec['A21'].font = font_titulo
    ws_rec['A21'].alignment = Alignment(horizontal='right', vertical='center')
    
    ws_rec.merge_cells('E21:G21')
    ws_rec['E21'] = "=CALCULO_FINIQUITO!H34"
    ws_rec['E21'].font = font_verde
    ws_rec['E21'].fill = fill_verde_neto
    ws_rec['E21'].alignment = Alignment(horizontal='center', vertical='center')
    ws_rec['E21'].number_format = '$#,##0.00'
    ws_rec['E21'].border = border_total

    ws_rec.merge_cells('A23:G25')
    ws_rec['A23'] = (
        "Hago constar que con la cantidad neta indicada en el presente recibo, me son cubiertas todas y cada una de las "
        "percepciones ordinarias y extraordinarias a que tuve derecho durante el tiempo que preste mis servicios, no reservandome "
        "ninguna accion ni derecho que ejercitar en contra de la empresa ni de quien legalmente la represente, otorgando el mas "
        "amplio finiquito que en derecho proceda a entera satisfaccion."
    )
    ws_rec['A23'].font = Font(name='Calibri', size=8.5, italic=True, color='334155')
    ws_rec['A23'].alignment = Alignment(horizontal='justify', vertical='center', wrap_text=True)

    ws_rec.merge_cells('A29:C29')
    ws_rec['A29'] = '=IF(CALCULO_FINIQUITO!C37="","",CALCULO_FINIQUITO!C37)'
    ws_rec['A29'].font = font_negrita
    ws_rec['A29'].alignment = Alignment(horizontal='center')
    ws_rec['A29'].border = Border(top=Side(style='thin', color='000000'))
    
    ws_rec.merge_cells('E29:G29')
    ws_rec['E29'] = "COMERCIALIZADORA DE PRODUCTOS CERVECEROS"
    ws_rec['E29'].font = font_negrita
    ws_rec['E29'].alignment = Alignment(horizontal='center')
    ws_rec['E29'].border = Border(top=Side(style='thin', color='000000'))

    ws_rec.merge_cells('A30:C30')
    ws_rec['A30'] = "RECIBI DE CONFORMIDAD"
    ws_rec['A30'].font = Font(name='Calibri', size=9, bold=True, color='64748B')
    ws_rec['A30'].alignment = Alignment(horizontal='center')

    ws_rec.merge_cells('E30:G30')
    ws_rec['E30'] = "AUTORIZADO POR DIRECCION / FGC"
    ws_rec['E30'].font = Font(name='Calibri', size=9, bold=True, color='64748B')
    ws_rec['E30'].alignment = Alignment(horizontal='center')

    wb.save(ruta_archivo)
    print("Plantilla_Finiquito_y_Recibo.xlsx actualizada exitosamente.")

if __name__ == '__main__':
    actualizar_plantilla()
