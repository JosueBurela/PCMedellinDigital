# -*- coding: utf-8 -*-
import os, glob, subprocess
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from PIL import Image, ImageDraw, ImageFont

C_AZUL_INST   = "0A2342"
C_AUL_MEDIO  = "1E3A8A"
C_GUINDA      = "801438"
C_AZULL_CLARO  = "F1F5F9"
C_GRIS_FONDO  = "F8FAFC"
C_GRIS_BORDE  = "CBD511"
C_BORDE_DARK  = "94A3B8"
C_GRIS_TEXTO  = "334155"
C_NEGRO_SUAVE = "0F172A"
C_BLANCO      = "FFFFFF"
C_ROJO_FOLIO  = "B91C1C"
