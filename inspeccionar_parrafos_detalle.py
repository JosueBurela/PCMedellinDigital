import docx

path = r'C:\Users\burel\Downloads\CEDULA DE EVALUACION SIMU MEDELLIN.docx'
doc = docx.Document(path)

ns = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'v': 'urn:schemas-microsoft-com:vml'
}

print("=== ALL PARAGRAPHS WITH CONTENT OR BREAKS ===")
for i, p in enumerate(doc.paragraphs):
    txt = p.text.strip()
    drawings = len(p._p.xpath('.//w:drawing', namespaces=ns))
    vml = len(p._p.xpath('.//v:shape', namespaces=ns))
    sec_break = len(p._p.xpath('.//w:sectPr', namespaces=ns))
    page_break = len(p._p.xpath('.//w:br[@w:type="page"]', namespaces=ns))
    
    if txt or drawings or vml or sec_break or page_break:
        print(f"P{i:02d}: text='{txt[:50]}' | drawings={drawings} | vml={vml} | secBreak={sec_break} | pgBreak={page_break}")
