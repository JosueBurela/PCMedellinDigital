import zipfile
import xml.etree.ElementTree as ET

docx_path = r'C:\Users\burel\Downloads\CEDULA DE EVALUACION SIMU MEDELLIN.docx'

with zipfile.ZipFile(docx_path, 'r') as z:
    for name in z.namelist():
        if name.startswith('word/'):
            info = z.getinfo(name)
            print(f'{name}: {info.file_size} bytes')
