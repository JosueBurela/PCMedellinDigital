import os
import sys
from fpdf import FPDF
import sqlite3
import pandas as pd

def txt(texto):
    if pd.isna(texto): return ""
    return str(texto).encode('latin-1', 'replace').decode('latin-1')

class PDFInforme(FPDF):
    def header(self):
        banner_top = 'Documentacion/banner_superior_oficial.png'
        if os.path.exists(banner_top):
            self.image(banner_top, x=0, y=0, w=215.9) # Ancho carta
            self.set_y(32)
        else:
            self.set_y(15)

    def footer(self):
        banner_bot = 'Documentacion/banner_inferior_oficial.png'
        if os.path.exists(banner_bot):
            self.image(banner_bot, x=0, y=260, w=215.9)
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, txt(f'Página {self.page_no()} | Dirección de Protección Civil de Medellín de Bravo, Ver.'), 0, 0, 'C')

def generar_pdf():
    pdf = PDFInforme(orientation='P', unit='mm', format='Letter')
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.add_page()

    # Título Institucional
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(214, 40, 40) # Rojo institucional
    pdf.cell(0, 6, txt('H. AYUNTAMIENTO DE MEDELLÍN DE BRAVO, VERACRUZ'), 0, 1, 'C')
    
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(10, 35, 66) # Azul marino
    pdf.cell(0, 7, txt('DIRECCIÓN DE PROTECCIÓN CIVIL Y BOMBEROS MUNICIPALES'), 0, 1, 'C')
    
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(23, 86, 118)
    pdf.cell(0, 6, txt('INFORME EJECUTIVO ANUAL DE EMERGENCIAS Y TRASLADOS 2026'), 0, 1, 'C')
    
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, txt('Periodo: 01 de Enero al 10 de Septiembre de 2026 | Titular: Lic. Daniel Eduardo Romero Pilar'), 0, 1, 'C')
    pdf.ln(4)

    # Línea divisoria
    pdf.set_draw_color(200, 205, 215)
    pdf.set_line_width(0.5)
    pdf.line(15, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    # =========================================================================
    # SECCIÓN 1: PANORAMA GENERAL
    # =========================================================================
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(10, 35, 66)
    pdf.cell(0, 6, txt('1. PANORAMA GENERAL DE EMERGENCIAS TRABAJADAS EN EL AÑO'), 0, 1, 'L')
    
    pdf.set_font('Arial', '', 9.5)
    pdf.set_text_color(40, 40, 40)
    texto_p1 = (
        "Durante el periodo comprendido del 01 de Enero al 10 de Septiembre de 2026, la Dirección de Protección Civil "
        "y Bomberos de Medellín de Bravo ha intervenido en un total acumulado de 1,753 servicios de emergencia y auxilio ciudadano. "
        "La operatividad se concentra principalmente en la atención médica prehospitalaria (65.5%), seguida del combate a incendios (11.5%) "
        "y contingencias hidrometeorológicas (8.3%)."
    )
    pdf.multi_cell(0, 4.8, txt(texto_p1))
    pdf.ln(3)

    # Tabla 1: Categorías
    pdf.set_font('Arial', 'B', 8.5)
    pdf.set_fill_color(10, 35, 66)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(85, 6, txt('Rama / Categoría Operativa'), 1, 0, 'L', 1)
    pdf.cell(30, 6, txt('Servicios'), 1, 0, 'C', 1)
    pdf.cell(25, 6, txt('% Anual'), 1, 0, 'C', 1)
    pdf.cell(50, 6, txt('Resumen de Despliegue'), 1, 1, 'L', 1)

    t1_data = [
        ("Atención Médica / Prehospitalaria", "1,149", "65.54%", "Urgencias, choques moto, traslados"),
        ("Incendios (Pastizal, Vivienda, Gas)", "202", "11.52%", "Combate y liquidación de siniestros"),
        ("Agentes Perturbadores / Lluvias", "145", "8.27%", "Inundaciones, desazolves, árboles"),
        ("Control de Fauna Silvestre", "124", "7.07%", "Abejas, ofidios/serpientes, semovientes"),
        ("Servicios Comunitarios y Pipas", "60", "3.42%", "Abastecimiento de agua y apoyo social"),
        ("Accidentes Vehiculares Directos", "48", "2.74%", "Choques automotores y abanderamiento"),
        ("TOTAL ANUAL DE SERVICIOS", "1,753", "100.0%", "Consolidado Operativo 2026")
    ]

    pdf.set_font('Arial', '', 8)
    for idx, (cat, serv, pct, desc) in enumerate(t1_data):
        is_tot = (idx == len(t1_data) - 1)
        if is_tot:
            pdf.set_font('Arial', 'B', 8.5)
            pdf.set_fill_color(233, 236, 239)
            pdf.set_text_color(10, 35, 66)
        else:
            pdf.set_font('Arial', '', 8)
            pdf.set_fill_color(248, 249, 250) if idx % 2 == 1 else pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(40, 40, 40)
            
        pdf.cell(85, 5.2, txt(cat), 1, 0, 'L', 1)
        pdf.cell(30, 5.2, txt(serv), 1, 0, 'C', 1)
        pdf.cell(25, 5.2, txt(pct), 1, 0, 'C', 1)
        pdf.cell(50, 5.2, txt(desc), 1, 1, 'L', 1)

    pdf.ln(5)

    # =========================================================================
    # SECCIÓN 2: TRASLADOS REALIZADOS
    # =========================================================================
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(10, 35, 66)
    pdf.cell(0, 6, txt('2. EXTRACCIÓN Y AUDITORÍA DE TRASLADOS EN AMBULANCIA'), 0, 1, 'L')
    
    pdf.set_font('Arial', '', 9.5)
    pdf.set_text_color(40, 40, 40)
    texto_p2 = (
        "De los 1,149 auxilios médicos atendidos por el personal paramédico y de ambulancias (U-208, U-098 y U-097):\n"
        "1. Catálogo Consolidado Anual: Se tienen formalmente etiquetados 53 traslados directos (43 interhospitalarios y 10 de urgencia obstétrica/parto).\n"
        "2. Auditoría Operativa de Guardias en Campo: Se identificaron 118 servicios con traslado efectivo de pacientes a nosocomios de la conurbación o retorno asistido a domicilio. El 68% restante de los auxilios médicos fueron resueltos en el lugar (curaciones, signos estables o negativa de traslado firmada)."
    )
    pdf.multi_cell(0, 4.6, txt(texto_p2))
    pdf.ln(3)

    # Tabla 2: Centros Receptores
    pdf.set_font('Arial', 'B', 8.5)
    pdf.set_fill_color(10, 35, 66)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(80, 6, txt('Centro Hospitalario / Destino'), 1, 0, 'L', 1)
    pdf.cell(25, 6, txt('Traslados'), 1, 0, 'C', 1)
    pdf.cell(25, 6, txt('% Traslados'), 1, 0, 'C', 1)
    pdf.cell(60, 6, txt('Tipo de Paciente / Patología'), 1, 1, 'L', 1)

    t2_data = [
        ("Hospital General de Boca del Río", "37", "31.4%", "Trauma vial, choques moto, caídas graves"),
        ("IMSS Clínica 71 (Díaz Mirón)", "15", "12.7%", "Derechohabientes IMSS, fracturas expuestas"),
        ("IMSS Hospital Cuauhtémoc (Clínica 61)", "15", "12.7%", "Derivaciones, medicina interna, altas"),
        ("Hospital Regional de Alta Especialidad", "7", "5.9%", "Traumatismo craneoencefálico, código rojo"),
        ("Torre Pediátrica de Veracruz", "5", "4.2%", "Convulsiones infantiles y caídas pediátricas"),
        ("Hospital Naval (HOSNAVER)", "3", "2.5%", "Derechohabientes SEMAR con trauma"),
        ("Centros Privados y Cruz Roja", "5", "4.2%", "Particulares (D'María / Cruz Roja)"),
        ("Traslados a Domicilio (Alta Hospitalaria)", "13", "11.0%", "Pacientes postquirúrgicos / apoyo social"),
        ("Otras Clínicas de Zona", "18", "15.3%", "Centros de salud y valoración periférica"),
        ("TOTAL TRASLADOS AUDITADOS", "118", "100.0%", "Servicios de transporte sanitario efectivo")
    ]

    for idx, (hosp, num, pct, perfil) in enumerate(t2_data):
        is_tot = (idx == len(t2_data) - 1)
        if is_tot:
            pdf.set_font('Arial', 'B', 8.5)
            pdf.set_fill_color(233, 236, 239)
            pdf.set_text_color(10, 35, 66)
        else:
            pdf.set_font('Arial', '', 8)
            pdf.set_fill_color(248, 249, 250) if idx % 2 == 1 else pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(40, 40, 40)
            
        pdf.cell(80, 5.0, txt(hosp), 1, 0, 'L', 1)
        pdf.cell(25, 5.0, txt(num), 1, 0, 'C', 1)
        pdf.cell(25, 5.0, txt(pct), 1, 0, 'C', 1)
        pdf.cell(60, 5.0, txt(perfil), 1, 1, 'L', 1)

    pdf.ln(4)

    # Tabla 3: Unidades de Ambulancia
    pdf.set_font('Arial', 'B', 8.5)
    pdf.set_fill_color(23, 86, 118)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(50, 5.5, txt('Unidad de Ambulancia'), 1, 0, 'L', 1)
    pdf.cell(40, 5.5, txt('Capacidad Técnica'), 1, 0, 'L', 1)
    pdf.cell(35, 5.5, txt('Traslados Realizados'), 1, 0, 'C', 1)
    pdf.cell(65, 5.5, txt('Cobertura Geográfica'), 1, 1, 'L', 1)

    t3_data = [
        ("Ambulancia U-208", "Soporte Vital Avanzado", "58 traslados", "Foráneos, IMSS Cuauhtémoc y zona rural"),
        ("Ambulancia U-098", "Soporte Vital Básico", "54 traslados", "Puente Moreno, El Tejar, Boca del Río"),
        ("Ambulancia U-097", "Unidad RAM Soporte", "15 traslados", "Apoyo en cuadrantes rurales y relevos")
    ]
    pdf.set_font('Arial', '', 8)
    pdf.set_text_color(40, 40, 40)
    for idx, (u, cap, tras, cob) in enumerate(t3_data):
        pdf.set_fill_color(248, 249, 250) if idx % 2 == 1 else pdf.set_fill_color(255, 255, 255)
        pdf.cell(50, 4.8, txt(u), 1, 0, 'L', 1)
        pdf.cell(40, 4.8, txt(cap), 1, 0, 'L', 1)
        pdf.cell(35, 4.8, txt(tras), 1, 0, 'C', 1)
        pdf.cell(65, 4.8, txt(cob), 1, 1, 'L', 1)

    pdf.ln(5)

    # =========================================================================
    # SECCIÓN 3: CONCENTRADO MENSUAL Y FIRMAS
    # =========================================================================
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(10, 35, 66)
    pdf.cell(0, 6, txt('3. HISTÓRICO MENSUAL DE EMERGENCIAS Y TRASLADOS 2026'), 0, 1, 'L')

    pdf.set_font('Arial', 'B', 8)
    pdf.set_fill_color(10, 35, 66)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(35, 5.5, txt('Mes Operativo'), 1, 0, 'L', 1)
    pdf.cell(30, 5.5, txt('Total Servicios'), 1, 0, 'C', 1)
    pdf.cell(35, 5.5, txt('Atención Médica'), 1, 0, 'C', 1)
    pdf.cell(30, 5.5, txt('Traslados Est.'), 1, 0, 'C', 1)
    pdf.cell(30, 5.5, txt('Efectividad'), 1, 0, 'C', 1)
    pdf.cell(30, 5.5, txt('% del Año'), 1, 1, 'C', 1)

    t4_data = [
        ("Enero", "210", "137", "18*", "91.4%", "12.0%"),
        ("Febrero", "190", "124", "15*", "88.9%", "10.8%"),
        ("Marzo", "210", "138", "19*", "90.0%", "12.0%"),
        ("Abril", "200", "131", "16*", "89.5%", "11.4%"),
        ("Mayo", "157", "132", "14*", "84.1%", "9.0%"),
        ("Junio", "204", "169", "21*", "82.8%", "11.6%"),
        ("Julio", "166", "136", "16*", "81.9%", "9.5%"),
        ("Agosto", "379", "163", "50", "89.2%", "21.6%"),
        ("Septiembre (al 10)", "37", "20", "3", "94.6%", "2.1%"),
        ("TOTAL ACUMULADO", "1,753", "1,149", "172*", "87.6%", "100.0%")
    ]

    for idx, (m, tot, med, tr, ef, pct) in enumerate(t4_data):
        is_tot = (idx == len(t4_data) - 1)
        if is_tot:
            pdf.set_font('Arial', 'B', 8.5)
            pdf.set_fill_color(233, 236, 239)
            pdf.set_text_color(10, 35, 66)
        else:
            pdf.set_font('Arial', '', 8)
            pdf.set_fill_color(248, 249, 250) if idx % 2 == 1 else pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(40, 40, 40)
            
        pdf.cell(35, 4.8, txt(m), 1, 0, 'L', 1)
        pdf.cell(30, 4.8, txt(tot), 1, 0, 'C', 1)
        pdf.cell(35, 4.8, txt(med), 1, 0, 'C', 1)
        pdf.cell(30, 4.8, txt(tr), 1, 0, 'C', 1)
        pdf.cell(30, 4.8, txt(ef), 1, 0, 'C', 1)
        pdf.cell(30, 4.8, txt(pct), 1, 1, 'C', 1)

    pdf.set_font('Arial', 'I', 7.5)
    pdf.set_text_color(110, 110, 110)
    pdf.cell(0, 4, txt('* Enero-Julio proyectado con base en la tasa histórica de traslado (12%-15% sobre servicios prehospitalarios).'), 0, 1, 'L')
    pdf.ln(6)

    # Firmas
    pdf.set_font('Arial', 'B', 8.5)
    pdf.set_text_color(10, 35, 66)
    pdf.cell(0, 4, txt('ATENTAMENTE'), 0, 1, 'C')
    pdf.cell(0, 4, txt('"PREVENCIÓN, AUXILIO Y SERVICIO A LA COMUNIDAD"'), 0, 1, 'C')
    pdf.ln(10)
    pdf.cell(0, 4, txt('_____________________________________________'), 0, 1, 'C')
    pdf.cell(0, 4, txt('LIC. DANIEL EDUARDO ROMERO PILAR'), 0, 1, 'C')
    pdf.set_font('Arial', '', 8)
    pdf.cell(0, 4, txt('DIRECTOR DE PROTECCIÓN CIVIL Y BOMBEROS MUNICIPALES'), 0, 1, 'C')
    pdf.cell(0, 4, txt('H. AYUNTAMIENTO DE MEDELLÍN DE BRAVO, VERACRUZ'), 0, 1, 'C')

    pdf_out = 'Documentacion/Informe_Oficial_Emergencias_y_Traslados_2026.pdf'
    pdf.output(pdf_out, 'F')
    print(f"Documento PDF generado exitosamente en: {pdf_out}")

if __name__ == '__main__':
    generar_pdf()
