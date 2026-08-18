import os
import sys
import qrcode
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Any, Optional

def get_asset_path(relative_path: str) -> str:
    """
    Obtiene la ruta absoluta para los recursos estáticos.
    Soporta la carpeta temporal de PyInstaller (Fase 5).
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class CardGenerator:
    def __init__(self, font_name: str = "Inter-Medium.ttf"):
        self.font_path = get_asset_path(os.path.join("assets", "fonts", font_name))
        
        # Paleta de colores Medellín de Bravo - TEMA CLARO
        self.color_bg = (242, 242, 242, 255)     # Gris muy claro (#F2F2F2)
        self.color_border = (217, 138, 41, 255) # Borde de la tarjeta en Oro Cálido
        self.color_gold = (217, 138, 41, 255)   # Amarillo / Oro (Detalles)
        self.color_green = (107, 142, 65, 255)  # Verde oliva (Cargos, Empresas)
        self.color_teal = (100, 116, 139, 255)  # Gris azulado para etiquetas de detalles
        self.color_name = (78, 27, 62, 255)     # Plum profundo (Nombre)
        self.color_text = (30, 41, 59, 255)     # Slate 900 para valores de texto
        self.color_divider = (217, 138, 41, 128) # Oro semi-transparente para divisor

    def _get_font(self, size: int, bold: bool = False) -> ImageFont.ImageFont:
        nombres_fuente = []
        if bold:
            nombres_fuente = [self.font_path, "segoeuib.ttf", "arialbd.ttf", "calibrib.ttf"]
        else:
            nombres_fuente = [self.font_path, "segoeui.ttf", "arial.ttf", "calibri.ttf"]
            
        for name in nombres_fuente:
            try:
                if name.endswith(".ttf") and os.path.exists(name):
                    return ImageFont.truetype(name, size)
                return ImageFont.truetype(name, size)
            except Exception:
                continue
                
        return ImageFont.load_default()

    def _cargar_logo(self, size_w: int, size_h: int) -> Optional[Image.Image]:
        logo_path = get_asset_path(os.path.join("assets", "logo_light.jpg"))
        if not os.path.exists(logo_path):
            logo_path = get_asset_path(os.path.join("assets", "logo_dark.jpg"))
            
        if not os.path.exists(logo_path):
            return None
            
        try:
            img = Image.open(logo_path).convert("RGBA")
            img = img.resize((size_w, size_h), Image.Resampling.LANCZOS)
            return img
        except Exception:
            return None

    def _recortar_circular(self, img_path: str, size: int) -> Optional[Image.Image]:
        if not img_path or not os.path.exists(img_path):
            return None
        try:
            img = Image.open(img_path).convert("RGBA")
            w_orig, h_orig = img.size
            min_dim = min(w_orig, h_orig)
            left = (w_orig - min_dim) / 2
            top = (h_orig - min_dim) / 2
            right = (w_orig + min_dim) / 2
            bottom = (h_orig + min_dim) / 2
            
            img_square = img.crop((left, top, right, bottom))
            img_resized = img_square.resize((size, size), Image.Resampling.LANCZOS)
            
            mask = Image.new("L", (size, size), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, size - 1, size - 1), fill=255)
            
            circular_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            circular_img.paste(img_resized, (0, 0), mask=mask)
            return circular_img
        except Exception as e:
            print(f"Error al procesar imagen circular: {e}")
            return None

    def _draw_text_autofit(self, draw: ImageDraw.ImageDraw, text: str, x: int, y: int, 
                           max_width: int, max_size: int, fill_color: tuple, 
                           bold: bool = True, center: bool = False) -> int:
        """
        Dibuja el texto ajustando dinámicamente el tamaño de la fuente para
        asegurar que quepa en max_width. Retorna el tamaño de fuente final utilizado.
        """
        size = max_size
        while size > 14:
            font = self._get_font(size, bold=bold)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            if text_width <= max_width:
                break
            size -= 1
            
        font = self._get_font(size, bold=bold)
        if center:
            draw.text((x, y), text, fill=fill_color, font=font, anchor="ma")
        else:
            draw.text((x, y), text, fill=fill_color, font=font)
            
        return size

    def generar_vcard(self, datos: Dict[str, Any]) -> str:
        nombre = datos.get("nombre", "").strip()
        partes = nombre.split(" ", 1)
        firstname = partes[0]
        lastname = partes[1] if len(partes) > 1 else ""

        vcard = [
            "BEGIN:VCARD",
            "VERSION:3.0",
            f"N:{lastname};{firstname};;;",
            f"FN:{nombre}",
            f"TEL;TYPE=CELL,VOICE:{datos.get('telefono', '').strip()}"
        ]

        if datos.get("email"):
            vcard.append(f"EMAIL;TYPE=PREF,INTERNET:{datos.get('email').strip()}")
        if datos.get("empresa"):
            vcard.append(f"ORG:{datos.get('empresa').strip()}")
        if datos.get("puesto"):
            vcard.append(f"TITLE:{datos.get('puesto').strip()}")
        if datos.get("web"):
            vcard.append(f"URL:{datos.get('web').strip()}")
        if datos.get("direccion"):
            vcard.append(f"ADR;TYPE=WORK:;;{datos.get('direccion').strip()};;;")

        vcard.append("END:VCARD")
        return "\n".join(vcard)

    def generar_qr(self, vcard_data: str) -> Image.Image:
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=1,
        )
        qr.add_data(vcard_data)
        qr.make(fit=True)
        return qr.make_image(fill_color="black", back_color="white").convert("RGBA")

    def crear_tarjeta(self, contactos: List[Dict[str, Any]], output_path: str, horizontal: bool = True) -> str:
        if not contactos:
            raise ValueError("La lista de contactos no puede estar vacía.")
        
        contactos = contactos[:5]
        num_contactos = len(contactos)

        if horizontal:
            width = 1000
            height = 600 if num_contactos == 1 else num_contactos * 220
        else:
            width = 640
            height = 1024 if num_contactos == 1 else num_contactos * 320

        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Lienzo claro con Borde Oro
        draw.rounded_rectangle(
            [(0, 0), (width, height)],
            radius=24,
            fill=self.color_bg,
            outline=self.color_border,
            width=3
        )

        if num_contactos == 1:
            contacto = contactos[0]
            foto_path = contacto.get("foto")
            if foto_path and not os.path.isabs(foto_path):
                foto_path = os.path.abspath(foto_path)
                
            tiene_foto = foto_path and os.path.exists(foto_path)

            if horizontal:
                if tiene_foto:
                    self._dibujar_contacto_horizontal_con_foto(draw, image, contacto, foto_path)
                else:
                    self._dibujar_contacto_horizontal(draw, image, contacto)
            else:
                if tiene_foto:
                    self._dibujar_contacto_vertical_con_foto(draw, image, contacto, foto_path)
                else:
                    self._dibujar_contacto_vertical(draw, image, contacto)
        else:
            for i, contacto in enumerate(contactos):
                if horizontal:
                    y_offset = i * 220
                    self._dibujar_contacto_horizontal_compacto(draw, image, contacto, x=40, y=y_offset + 10, w=920, h=200)
                    if i < num_contactos - 1:
                        draw.line([(60, y_offset + 220), (940, y_offset + 220)], fill=self.color_divider, width=1)
                else:
                    y_offset = i * 320
                    self._dibujar_contacto_vertical_compacto(draw, image, contacto, x=30, y=y_offset + 10, w=580, h=300)
                    if i < num_contactos - 1:
                        draw.line([(40, y_offset + 320), (600, y_offset + 320)], fill=self.color_divider, width=1)

        image.save(output_path, "PNG")
        return output_path

    # --- MÉTODOS DE DIBUJO ---

    def _dibujar_contacto_horizontal(self, draw: ImageDraw.ImageDraw, image: Image.Image, contacto: Dict[str, Any]):
        font_label = self._get_font(18, bold=True)
        font_value = self._get_font(22, bold=False)

        x_text = 70
        y_text = 80

        # Acento lateral oro
        draw.rounded_rectangle([(30, 80), (36, 520)], radius=3, fill=self.color_gold)

        # Nombre con autoajuste (Ancho máx de 640 para no solapar el logo)
        name_size = self._draw_text_autofit(
            draw, contacto.get("nombre", ""), x_text, y_text, 
            max_width=640, max_size=42, fill_color=self.color_name, bold=True
        )
        y_text += name_size + 15

        # Cargo con autoajuste
        puesto = contacto.get("puesto", "")
        empresa = contacto.get("empresa", "")
        subtitulo = f"{puesto} | {empresa}" if puesto and empresa else (puesto or empresa or "Ayuntamiento")
        sub_size = self._draw_text_autofit(
            draw, subtitulo, x_text, y_text, 
            max_width=640, max_size=20, fill_color=self.color_green, bold=False
        )
        y_text += sub_size + 25

        # Separador oro
        draw.line([(x_text, y_text), (600, y_text)], fill=self.color_divider, width=1)
        y_text += 25

        campos = [
            ("TEL", contacto.get("telefono", "")),
            ("EMAIL", contacto.get("email", "")),
            ("WEB", contacto.get("web", "")),
            ("DIR", contacto.get("direccion", ""))
        ]

        for label, valor in campos:
            if valor:
                draw.text((x_text, y_text), label, fill=self.color_teal, font=font_label)
                draw.text((x_text + 95, y_text - 2), valor, fill=self.color_text, font=font_value)
                y_text += 46

        # Logo Medellín
        logo = self._cargar_logo(150, 150)
        if logo:
            image.paste(logo, (725, 70), logo)

        # QR
        vcard_str = self.generar_vcard(contacto)
        qr_img = self.generar_qr(vcard_str)
        qr_size = 220
        qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
        
        container_size = 220
        qr_x = 690
        qr_y = 290
        
        draw.rounded_rectangle(
            [(qr_x, qr_y), (qr_x + container_size, qr_y + container_size)],
            radius=16,
            fill=(255, 255, 255, 255),
            outline=self.color_gold,
            width=2
        )
        qr_inner_size = 190
        qr_img_resized = qr_img.resize((qr_inner_size, qr_inner_size), Image.Resampling.LANCZOS)
        image.paste(qr_img_resized, (qr_x + 15, qr_y + 15), qr_img_resized)

    def _dibujar_contacto_horizontal_con_foto(self, draw: ImageDraw.ImageDraw, image: Image.Image, contacto: Dict[str, Any], foto_path: str):
        font_label = self._get_font(16, bold=True)
        font_value = self._get_font(20, bold=False)

        avatar_size = 210
        avatar_img = self._recortar_circular(foto_path, avatar_size)
        if avatar_img:
            avatar_x = 60
            avatar_y = (image.height - avatar_size) // 2
            
            draw.ellipse(
                [(avatar_x - 3, avatar_y - 3), (avatar_x + avatar_size + 3, avatar_y + avatar_size + 3)],
                outline=self.color_gold,
                width=3
            )
            image.paste(avatar_img, (avatar_x, avatar_y), avatar_img)

        # Textos
        x_text = 300
        y_text = 80

        # Nombre con autoajuste (Ancho máx de 460 para evitar solapar el logo a la derecha)
        name_size = self._draw_text_autofit(
            draw, contacto.get("nombre", ""), x_text, y_text, 
            max_width=460, max_size=38, fill_color=self.color_name, bold=True
        )
        y_text += name_size + 15

        puesto = contacto.get("puesto", "")
        empresa = contacto.get("empresa", "")
        subtitulo = f"{puesto} | {empresa}" if puesto and empresa else (puesto or empresa or "Ayuntamiento")
        sub_size = self._draw_text_autofit(
            draw, subtitulo, x_text, y_text, 
            max_width=460, max_size=18, fill_color=self.color_green, bold=False
        )
        y_text += sub_size + 25

        draw.line([(x_text, y_text), (680, y_text)], fill=self.color_divider, width=1)
        y_text += 25

        campos = [
            ("TEL", contacto.get("telefono", "")),
            ("EMAIL", contacto.get("email", "")),
            ("WEB", contacto.get("web", "")),
            ("DIR", contacto.get("direccion", ""))
        ]

        for label, valor in campos:
            if valor:
                draw.text((x_text, y_text), label, fill=self.color_teal, font=font_label)
                draw.text((x_text + 85, y_text - 2), valor, fill=self.color_text, font=font_value)
                y_text += 44

        # Logo Medellín
        logo = self._cargar_logo(110, 110)
        if logo:
            image.paste(logo, (785, 50), logo)

        # QR
        vcard_str = self.generar_vcard(contacto)
        qr_img = self.generar_qr(vcard_str)
        
        container_size = 220
        qr_x = 730
        qr_y = 270
        
        draw.rounded_rectangle(
            [(qr_x, qr_y), (qr_x + container_size, qr_y + container_size)],
            radius=16,
            fill=(255, 255, 255, 255),
            outline=self.color_gold,
            width=2
        )
        qr_inner_size = 190
        qr_img_resized = qr_img.resize((qr_inner_size, qr_inner_size), Image.Resampling.LANCZOS)
        image.paste(qr_img_resized, (qr_x + 15, qr_y + 15), qr_img_resized)

    def _dibujar_contacto_vertical(self, draw: ImageDraw.ImageDraw, image: Image.Image, contacto: Dict[str, Any]):
        font_label = self._get_font(16, bold=True)
        font_value = self._get_font(20, bold=False)

        # Logo centrado
        logo = self._cargar_logo(150, 150)
        if logo:
            image.paste(logo, ((image.width - 150) // 2, 50), logo)

        x_text = 60
        y_text = 230

        # Acento horizontal oro
        draw.rounded_rectangle([(60, 215), (580, 221)], radius=3, fill=self.color_gold)

        name_size = self._draw_text_autofit(
            draw, contacto.get("nombre", ""), 320, y_text, 
            max_width=520, max_size=34, fill_color=self.color_name, bold=True, center=True
        )
        y_text += name_size + 15

        puesto = contacto.get("puesto", "")
        empresa = contacto.get("empresa", "")
        subtitulo = f"{puesto} | {empresa}" if puesto and empresa else (puesto or empresa or "Ayuntamiento")
        sub_size = self._draw_text_autofit(
            draw, subtitulo, 320, y_text, 
            max_width=520, max_size=18, fill_color=self.color_green, bold=False, center=True
        )
        y_text += sub_size + 25

        draw.line([(x_text, y_text), (580, y_text)], fill=self.color_divider, width=1)
        y_text += 25

        campos = [
            ("TEL", contacto.get("telefono", "")),
            ("EMAIL", contacto.get("email", "")),
            ("WEB", contacto.get("web", "")),
            ("DIR", contacto.get("direccion", ""))
        ]

        for label, valor in campos:
            if valor:
                draw.text((x_text, y_text), label, fill=self.color_teal, font=font_label)
                draw.text((x_text + 95, y_text - 2), valor, fill=self.color_text, font=font_value)
                y_text += 44

        # QR centrado
        vcard_str = self.generar_vcard(contacto)
        qr_img = self.generar_qr(vcard_str)
        
        container_size = 220
        qr_x = (image.width - container_size) // 2
        qr_y = image.height - container_size - 60
        
        draw.rounded_rectangle(
            [(qr_x, qr_y), (qr_x + container_size, qr_y + container_size)],
            radius=16,
            fill=(255, 255, 255, 255),
            outline=self.color_gold,
            width=2
        )
        qr_inner_size = 190
        qr_img_resized = qr_img.resize((qr_inner_size, qr_inner_size), Image.Resampling.LANCZOS)
        image.paste(qr_img_resized, (qr_x + 15, qr_y + 15), qr_img_resized)

    def _dibujar_contacto_vertical_con_foto(self, draw: ImageDraw.ImageDraw, image: Image.Image, contacto: Dict[str, Any], foto_path: str):
        font_label = self._get_font(14, bold=True)
        font_value = self._get_font(18, bold=False)

        logo = self._cargar_logo(80, 80)
        if logo:
            image.paste(logo, (40, 40), logo)

        avatar_size = 180
        avatar_img = self._recortar_circular(foto_path, avatar_size)
        if avatar_img:
            avatar_x = (image.width - avatar_size) // 2
            avatar_y = 60
            
            draw.ellipse(
                [(avatar_x - 3, avatar_y - 3), (avatar_x + avatar_size + 3, avatar_y + avatar_size + 3)],
                outline=self.color_gold,
                width=3
            )
            image.paste(avatar_img, (avatar_x, avatar_y), avatar_img)

        # Textos centrados
        y_text = 270
        nombre = contacto.get("nombre", "")
        name_size = self._draw_text_autofit(
            draw, nombre, 320, y_text, 
            max_width=520, max_size=30, fill_color=self.color_name, bold=True, center=True
        )
        y_text += name_size + 15

        puesto = contacto.get("puesto", "")
        empresa = contacto.get("empresa", "")
        subtitulo = f"{puesto} | {empresa}" if puesto and empresa else (puesto or empresa or "Ayuntamiento")
        sub_size = self._draw_text_autofit(
            draw, subtitulo, 320, y_text, 
            max_width=520, max_size=18, fill_color=self.color_green, bold=False, center=True
        )
        y_text += sub_size + 25

        draw.line([(60, y_text), (580, y_text)], fill=self.color_divider, width=1)
        y_text += 25

        # Datos
        x_left = 80
        campos = [
            ("TEL", contacto.get("telefono", "")),
            ("EMAIL", contacto.get("email", "")),
            ("WEB", contacto.get("web", "")),
            ("DIR", contacto.get("direccion", ""))
        ]

        for label, valor in campos:
            if valor:
                draw.text((x_left, y_text), label, fill=self.color_teal, font=font_label)
                draw.text((x_left + 85, y_text - 2), valor, fill=self.color_text, font=font_value)
                y_text += 40

        # QR centrado
        vcard_str = self.generar_vcard(contacto)
        qr_img = self.generar_qr(vcard_str)
        
        container_size = 220
        qr_x = (image.width - container_size) // 2
        qr_y = image.height - container_size - 50
        
        draw.rounded_rectangle(
            [(qr_x, qr_y), (qr_x + container_size, qr_y + container_size)],
            radius=16,
            fill=(255, 255, 255, 255),
            outline=self.color_gold,
            width=2
        )
        qr_inner_size = 190
        qr_img_resized = qr_img.resize((qr_inner_size, qr_inner_size), Image.Resampling.LANCZOS)
        image.paste(qr_img_resized, (qr_x + 15, qr_y + 15), qr_img_resized)

    def _dibujar_contacto_horizontal_compacto(self, draw: ImageDraw.ImageDraw, image: Image.Image, contacto: Dict[str, Any], x: int, y: int, w: int, h: int):
        font_name = self._get_font(26, bold=True)
        font_sub = self._get_font(16, bold=False)
        font_body = self._get_font(15, bold=False)

        foto_path = contacto.get("foto")
        if foto_path and not os.path.isabs(foto_path):
            foto_path = os.path.abspath(foto_path)
        tiene_foto = foto_path and os.path.exists(foto_path)
        
        x_text = x + 20
        if tiene_foto:
            mini_size = 130
            mini_img = self._recortar_circular(foto_path, mini_size)
            if mini_img:
                mini_x = x + 20
                mini_y = y + (h - mini_size) // 2
                draw.ellipse(
                    [(mini_x - 2, mini_y - 2), (mini_x + mini_size + 2, mini_y + mini_size + 2)],
                    outline=self.color_gold,
                    width=2
                )
                image.paste(mini_img, (mini_x, mini_y), mini_img)
                x_text = mini_x + mini_size + 20

        # QR
        vcard_str = self.generar_vcard(contacto)
        qr_img = self.generar_qr(vcard_str)
        qr_size = 140
        qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
        
        container_size = 170
        qr_x = x + w - container_size - 10
        qr_y = y + (h - container_size) // 2

        draw.rounded_rectangle(
            [(qr_x, qr_y), (qr_x + container_size, qr_y + container_size)],
            radius=12,
            fill=(255, 255, 255, 255),
            outline=self.color_gold,
            width=1
        )
        qr_inner_size = 140
        qr_img_resized = qr_img.resize((qr_inner_size, qr_inner_size), Image.Resampling.LANCZOS)
        image.paste(qr_img_resized, (qr_x + 15, qr_y + 15), qr_img_resized)

        # Textos con autoajuste para directorio compacto
        text_y = y + 20
        name_size = self._draw_text_autofit(
            draw, contacto.get("nombre", ""), x_text, text_y, 
            max_width=w - container_size - (x_text - x) - 30, max_size=26, fill_color=self.color_name, bold=True
        )
        text_y += name_size + 9

        puesto = contacto.get("puesto", "")
        empresa = contacto.get("empresa", "")
        subtitulo = f"{puesto} | {empresa}" if puesto and empresa else (puesto or empresa or "")
        if subtitulo:
            sub_size = self._draw_text_autofit(
                draw, subtitulo, x_text, text_y, 
                max_width=w - container_size - (x_text - x) - 30, max_size=16, fill_color=self.color_green, bold=False
            )
            text_y += sub_size + 10

        telefono = contacto.get("telefono", "")
        email = contacto.get("email", "")
        detalles = f"📞 {telefono}"
        if email:
            detalles += f"   |   📧 {email}"
        draw.text((x_text, text_y), detalles, fill=self.color_text, font=font_body)
        text_y += 25

        web = contacto.get("web", "")
        direccion = contacto.get("direccion", "")
        extras = []
        if web:
            extras.append(f"🔗 {web}")
        if direccion:
            extras.append(f"📍 {direccion}")
        if extras:
            draw.text((x_text, text_y), "   |   ".join(extras), fill=self.color_teal, font=font_body)

    def _dibujar_contacto_vertical_compacto(self, draw: ImageDraw.ImageDraw, image: Image.Image, contacto: Dict[str, Any], x: int, y: int, w: int, h: int):
        font_body = self._get_font(13, bold=False)

        foto_path = contacto.get("foto")
        if foto_path and not os.path.isabs(foto_path):
            foto_path = os.path.abspath(foto_path)
        tiene_foto = foto_path and os.path.exists(foto_path)
        
        x_text = x + 10
        if tiene_foto:
            mini_size = 140
            mini_img = self._recortar_circular(foto_path, mini_size)
            if mini_img:
                mini_x = x + 10
                mini_y = y + (h - mini_size) // 2
                draw.ellipse(
                    [(mini_x - 2, mini_y - 2), (mini_x + mini_size + 2, mini_y + mini_size + 2)],
                    outline=self.color_gold,
                    width=2
                )
                image.paste(mini_img, (mini_x, mini_y), mini_img)
                x_text = mini_x + mini_size + 15

        # QR
        vcard_str = self.generar_vcard(contacto)
        qr_img = self.generar_qr(vcard_str)
        
        container_size = 180
        qr_x = x + w - container_size - 10
        qr_y = y + (h - container_size) // 2

        draw.rounded_rectangle(
            [(qr_x, qr_y), (qr_x + container_size, qr_y + container_size)],
            radius=12,
            fill=(255, 255, 255, 255),
            outline=self.color_gold,
            width=1
        )
        qr_inner_size = 150
        qr_img_resized = qr_img.resize((qr_inner_size, qr_inner_size), Image.Resampling.LANCZOS)
        image.paste(qr_img_resized, (qr_x + 15, qr_y + 15), qr_img_resized)

        # Textos
        text_y = y + 35
        name_size = self._draw_text_autofit(
            draw, contacto.get("nombre", ""), x_text, text_y, 
            max_width=w - container_size - (x_text - x) - 20, max_size=22, fill_color=self.color_name, bold=True
        )
        text_y += name_size + 8

        puesto = contacto.get("puesto", "")
        empresa = contacto.get("empresa", "")
        subtitulo = f"{puesto} | {empresa}" if puesto and empresa else (puesto or empresa or "")
        if subtitulo:
            sub_size = self._draw_text_autofit(
                draw, subtitulo, x_text, text_y, 
                max_width=w - container_size - (x_text - x) - 20, max_size=15, fill_color=self.color_green, bold=False
            )
            text_y += sub_size + 8

        draw.text((x_text, text_y), f"📞 {contacto.get('telefono', '')}", fill=self.color_text, font=font_body)
        text_y += 24

        email = contacto.get("email", "")
        if email:
            draw.text((x_text, text_y), f"📧 {email}", fill=self.color_teal, font=font_body)
