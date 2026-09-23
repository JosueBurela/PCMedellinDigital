import openpyxl
import shutil

def generar_ejemplos():
    base_template = r'C:\Users\burel\Downloads\hojasdecalculoscuriosas\Plantilla_Finiquito_y_Recibo.xlsx'
    
    # -------------------------------------------------------------
    # EJEMPLO 1: FINIQUITO ORDINARIO (JOSE ANTONIO CRUZ - FOTO 2)
    # -------------------------------------------------------------
    ruta_ejemplo1 = r'C:\Users\burel\Downloads\hojasdecalculoscuriosas\Ejemplo_Finiquito_Jose_Antonio_Cruz.xlsx'
    shutil.copyfile(base_template, ruta_ejemplo1)
    
    wb1 = openpyxl.load_workbook(ruta_ejemplo1)
    ws1 = wb1['CALCULO_FINIQUITO']
    
    # Fechas y Salario
    ws1['C2'] = "03/05/2025"
    ws1['C3'] = "18/08/2026"
    ws1['G2'] = 493.42
    
    # Percepciones
    ws1['B6'] = 3.52   # Salarios (días)
    ws1['B7'] = 0      # Incentivo
    ws1['B8'] = 0      # Tiempo extra
    
    # Vacaciones 1 (6 días del 1er año completado)
    ws1['B10'] = 6
    ws1['G10'] = 365
    
    # Vacaciones 2 (14 días del 2do año proporcional, 108 días trabajados)
    ws1['B13'] = 14
    ws1['G13'] = 108
    
    # Aguinaldo (15 días de ley, 230 días trabajados en el año)
    ws1['B17'] = 15
    ws1['G17'] = 230
    
    # Gratificación finiquito (12 días)
    ws1['B18'] = 12
    
    # En finiquito normal, indemnización y antigüedad son 0
    ws1['B19'] = 0
    ws1['B20'] = 0
    
    # Deducciones
    ws1['H27'] = 1408.89 # Deudores
    
    # Datos del trabajador
    ws1['C37'] = "CRUZ GONZALEZ JOSE ANTONIO"
    ws1['C38'] = "PREVENTISTA"
    ws1['C39'] = 13228
    ws1['C40'] = "RESCISION"
    
    wb1.save(ruta_ejemplo1)
    print("Ejemplo 1 (Cruz Gonzalez) generado exitosamente.")
    
    # -------------------------------------------------------------
    # EJEMPLO 2: LIQUIDACIÓN COMPLETA (IÑAKI ULIBARRI - FOTO 1)
    # -------------------------------------------------------------
    ruta_ejemplo2 = r'C:\Users\burel\Downloads\hojasdecalculoscuriosas\Ejemplo_Liquidacion_Inaki_Ulibarri.xlsx'
    shutil.copyfile(base_template, ruta_ejemplo2)
    
    wb2 = openpyxl.load_workbook(ruta_ejemplo2)
    ws2 = wb2['CALCULO_FINIQUITO']
    
    # Fechas y Salario (Sueldo diario aproximado = 9,198.98 / 15 = 613.265)
    ws2['C2'] = "12/08/2025"
    ws2['C3'] = "29/07/2026"
    ws2['G2'] = 1314.14 # Salario diario integrado que produce 118,272.60 en 90 días
    
    # Salario devengado (7 días de sueldo)
    ws2['B6'] = 7
    
    # Prima vacacional y Aguinaldo
    ws2['F14'] = 19554.40 # Base vacaciones
    ws2['B17'] = 15
    ws2['G17'] = 236
    
    # Gratificación Finiquito
    ws2['B18'] = 7
    
    # INDEMNIZACIÓN CONSTITUCIONAL (90 DÍAS)
    ws2['B19'] = 90
    
    # PRIMA DE ANTIGÜEDAD (12 DÍAS TOPADOS A 2 UMA = 217.14)
    ws2['B20'] = 34.82
    
    # Deducciones
    ws2['H26'] = 2043.00 # Infonavit
    
    # Datos del trabajador
    ws2['C37'] = "ULIBARRI BONILLA IÑAKI"
    ws2['C38'] = "JEFE DE AUDITORIA OPERATIVA"
    ws2['C39'] = 124
    ws2['C40'] = "SEPARACION VOLUNTARIA (LIQUIDACION)"
    
    wb2.save(ruta_ejemplo2)
    print("Ejemplo 2 (Inaki Ulibarri) generado exitosamente.")

if __name__ == '__main__':
    generar_ejemplos()
