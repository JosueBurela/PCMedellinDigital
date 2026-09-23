import docx
from docx import Document
from docx.shared import Inches, Pt

doc = Document()
sec = doc.sections[0]
sec.top_margin = Inches(0.3)
sec.bottom_margin = Inches(0.3)
sec.left_margin = Inches(0.5)
sec.right_margin = Inches(0.5)
p = doc.add_paragraph('Hola Medellín')
doc.save('Documentacion/test_space.docx')
print('File created!')
