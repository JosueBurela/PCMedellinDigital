import zipfile
import xml.etree.ElementTree as ET

docx_path = r'C:\Users\burel\Downloads\CEDULA DE EVALUACION SIMU MEDELLIN.docx'

with zipfile.ZipFile(docx_path, 'r') as z:
    doc_xml = z.read('word/document.xml').decode('utf-8')
    rels_xml = z.read('word/_rels/document.xml.rels').decode('utf-8')

print('=== RELS ===')
print(rels_xml)

# Buscar dónde aparecen los rId de las imágenes
root = ET.fromstring(doc_xml)
namespaces = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'v': 'urn:schemas-microsoft-com:vml',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}

drawings = root.findall('.//w:drawing', namespaces)
print(f'\nTotal w:drawing: {len(drawings)}')

for i, d in enumerate(drawings):
    blip = d.find('.//a:blip', namespaces)
    embed = blip.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed') if blip is not None else None
    
    # Buscar posicionamiento
    anchor = d.find('.//wp:anchor', namespaces)
    inline = d.find('.//wp:inline', namespaces)
    pos_type = 'anchor' if anchor is not None else ('inline' if inline is not None else 'unknown')
    
    # Si es anchor, ver coordenadas
    pos_info = ''
    if anchor is not None:
        posH = anchor.find('.//wp:positionH/wp:posOffset', namespaces)
        posV = anchor.find('.//wp:positionV/wp:posOffset', namespaces)
        h_off = posH.text if posH is not None else '?'
        v_off = posV.text if posV is not None else '?'
        pos_info = f'H_offset={h_off}, V_offset={v_off}'
        
    print(f'Drawing {i}: embed={embed}, type={pos_type}, {pos_info}')
