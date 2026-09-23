import os
import glob
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from PIL import Image, ImageDraw, ImageFont

COLOR_AZUL_MARINO = 0A2342
COLOR_AZUL_MEDIO  = 1E3A8A
COLOR_GUINDA      = 801438
COLOR_GRIS_FONDO  = F8FAFC
COLOR_GRIS_BORDE  = CBD5E1
COLOR_GRIS_TEXTO  = 475569
COLOR_BLANCO      = FFFFFF
COLOR_ROJO_FOLIO  = B91C1C

print(Setup test successful)
