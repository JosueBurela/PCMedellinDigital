# ==============================================================================
#  🛡️ SISTEMA DIGITAL DE PROTECCIÓN CIVIL Y BOMBEROS
#  Copyright (c) 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
#  Desarrollado y Diseñado por: Josué Jaziel Delgado Burela
#  Contacto y Soporte: jburela1@gmal.com
# ==============================================================================

import datetime

ESTADOS_MEXICO = {
    'AS': 'Aguascalientes', 'BC': 'Baja California', 'BS': 'Baja California Sur',
    'CC': 'Campeche', 'CL': 'Coahuila', 'CM': 'Colima', 'CS': 'Chiapas',
    'CH': 'Chihuahua', 'DF': 'Ciudad de México', 'DG': 'Durango', 'GT': 'Guanajuato',
    'GR': 'Guerrero', 'HG': 'Hidalgo', 'JC': 'Jalisco', 'MC': 'Estado de México',
    'MN': 'Michoacán', 'MS': 'Morelos', 'NT': 'Nayarit', 'NL': 'Nuevo León',
    'OC': 'Oaxaca', 'PL': 'Puebla', 'QT': 'Querétaro', 'QR': 'Quintana Roo',
    'SP': 'San Luis Potosí', 'SL': 'Sinaloa', 'SR': 'Sonora', 'TC': 'Tabasco',
    'TS': 'Tamaulipas', 'TL': 'Tlaxcala', 'VZ': 'Veracruz', 'YN': 'Yucatán',
    'ZS': 'Zacatecas', 'NE': 'Nacido en el Extranjero'
}

def parsear_curp(curp):
    """
    Decodifica y extrae datos demográficos básicos estructurados en el formato estándar de CURP de 18 caracteres.
    """
    if len(curp) != 18:
        return None
        
    try:
        # Extraer fecha (YYMMDD) en las posiciones 5 a 10 (0-indexed: 4 a 10)
        yy_str = curp[4:6]
        mm_str = curp[6:8]
        dd_str = curp[8:10]
        
        yy = int(yy_str)
        mm = int(mm_str)
        dd = int(dd_str)
        
        # Determinar siglo (corte en año actual 2026)
        anio = 2000 + yy if yy <= 26 else 1900 + yy
        fecha_nac = datetime.date(anio, mm, dd)
        
        # Extraer género (H / M) en la posición 11 (0-indexed: 10)
        genero_str = curp[10].upper()
        genero = 'Hombre' if genero_str == 'H' else 'Mujer' if genero_str == 'M' else 'Desconocido'
        
        # Extraer abreviatura de estado en posiciones 12 y 13 (0-indexed: 11 a 13)
        edo_str = curp[11:13].upper()
        estado = ESTADOS_MEXICO.get(edo_str, 'Desconocido / No Registrado')
        
        # Simulador de Extracción Automática de Nombres (Mock RENAPO)
        # Reconstruye nombres ficticios usando la primera letra del nombre y apellidos de la CURP
        primer_letra_ap1 = curp[0].upper()
        primer_letra_ap2 = curp[1].upper()
        primer_letra_nom = curp[3].upper()
        
        # Mocking de apellidos
        apellidos_mock = {
            'A': 'Aguilar', 'B': 'Bustamante', 'C': 'Castillo', 'D': 'Díaz', 'E': 'Estrada',
            'F': 'Flores', 'G': 'Gómez', 'H': 'Hernández', 'I': 'Ibarra', 'J': 'Jiménez',
            'K': 'Kempis', 'L': 'López', 'M': 'Martínez', 'N': 'Núñez', 'O': 'Ortega',
            'P': 'Pérez', 'Q': 'Quiroz', 'R': 'Rodríguez', 'S': 'Sánchez', 'T': 'Torres',
            'U': 'Uribe', 'V': 'Valdez', 'W': 'Williams', 'X': 'Xicoténcatl', 'Y': 'Yáñez',
            'Z': 'Zúñiga'
        }
        
        nombres_mock = {
            'A': 'Alejandro', 'B': 'Beatriz', 'C': 'Carlos', 'D': 'Daniela', 'E': 'Eduardo',
            'F': 'Fernando', 'G': 'Gabriela', 'H': 'Héctor', 'I': 'Isabel', 'J': 'Juan',
            'K': 'Karina', 'L': 'Luis', 'M': 'María', 'N': 'Nancy', 'O': 'Óscar',
            'P': 'Patricia', 'Q': 'Quentin', 'R': 'Roberto', 'S': 'Sofía', 'T': 'Tomás',
            'U': 'Ulises', 'V': 'Víctor', 'W': 'Walter', 'X': 'Ximena', 'Y': 'Yolanda',
            'Z': 'Zacarías'
        }
        
        nombre_simulado = nombres_mock.get(primer_letra_nom, 'Ciudadano')
        ap1_simulado = apellidos_mock.get(primer_letra_ap1, 'Pérez')
        ap2_simulado = apellidos_mock.get(primer_letra_ap2, 'Gómez')
        
        return {
            'fecha_nacimiento': fecha_nac,
            'genero': genero,
            'estado_nacimiento': estado,
            'nombre': nombre_simulado,
            'primer_apellido': ap1_simulado,
            'segundo_apellido': ap2_simulado
        }
    except Exception as e:
        print("Error al decodificar CURP: ", e)
        return None
