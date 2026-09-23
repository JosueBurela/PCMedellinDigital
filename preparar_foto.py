# -*- coding: utf-8 -*-
import os
from PIL import Image

# 1. Preparar imagen fotográfica ajustada
photo_src = 'Documentacion/evidencia_intercambio_motosierras.jpg'
photo_crop_path = 'Documentacion/foto_intercambio_ajustada.jpg'

if os.path.exists(photo_src):
    im = Image.open(photo_src)
    # Recorte proporcional para encuadre vertical limpio
    # Tamaño original: 576 x 1024
    # Vamos a guardar versión optimizada
    im.save(photo_crop_path, quality=95)
    print("Foto de evidencia preparada.")
