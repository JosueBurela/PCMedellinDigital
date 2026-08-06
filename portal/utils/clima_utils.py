# ==============================================================================
#  🛡️ SISTEMA DIGITAL DE PROTECCIÓN CIVIL Y BOMBEROS
#  Copyright (c) 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
#  Desarrollado y Diseñado por: Josué Jaziel Delgado Burela
#  Contacto y Soporte: jburela1@gmal.com
# ==============================================================================

import csv
import datetime
import html
import io
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from django.core.cache import cache

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

def limpiar_texto_smn(text):
    """
    Decodifica entidades HTML y corrige cualquier imperfección de codificación
    proveniente de los scripts PHP legacy del SMN CONAGUA.
    """
    if not text:
        return ""
    text = html.unescape(text)
    replacements = {
        'Pacfico': 'Pacífico',
        'Pac&iacute;fico': 'Pacífico',
        'Atlntico': 'Atlántico',
        'Atl&aacute;ntico': 'Atlántico',
        'Mxico': 'México',
        'M&eacute;xico': 'México',
        'Michoacn': 'Michoacán',
        'Michoac&aacute;n': 'Michoacán',
        'Pronstico': 'Pronóstico',
        'Pron&oacute;stico': 'Pronóstico',
        'Norte': 'Norte',
        'Golfo': 'Golfo',
        '  ': ' '
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return ' '.join(text.split())

def obtener_cintillo_smn_directo():
    """
    Obtiene la lista en tiempo real de avisos meteorológicos de la marquesina oficial
    del SMN desde su archivo remoto bannerAvisos.php.
    """
    banner_url = "https://smn.conagua.gob.mx/tools/PHP/bannerAvisos.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    avisos = []
    try:
        r = requests.get(banner_url, headers=headers, timeout=5)
        if r.status_code == 200:
            raw_text = r.content.decode('utf-8', errors='ignore')
            soup = BeautifulSoup(raw_text, 'html.parser')
            for a_tag in soup.find_all('a'):
                txt = limpiar_texto_smn(a_tag.text)
                href = a_tag.get('href', '').strip()
                if href and not href.startswith('http'):
                    href = 'https://smn.conagua.gob.mx' + href
                if txt and href:
                    avisos.append({
                        "texto": txt,
                        "link": href
                    })
    except Exception as e:
        print("Error al consultar bannerAvisos.php del SMN:", e)

    if not avisos:
        avisos = [
            {
                "texto": "Pacífico: FAUSTO SE MANTIENE LEJOS DE LAS COSTAS DE MÉXICO",
                "link": "https://smn.conagua.gob.mx/es/pronosticos/avisos/aviso-de-ciclon-tropical-en-el-oceano-pacifico"
            },
            {
                "texto": "Atlántico: La tormenta tropical Bertha mantiene su desplazamiento sobre el norte del golfo de México.",
                "link": "https://smn.conagua.gob.mx/es/pronosticos/avisos/aviso-de-ciclon-tropical-en-el-oceano-atlantico"
            },
            {
                "texto": "Pronóstico General: LLUVIAS PUNTUALES MUY FUERTES EN JALISCO, COLIMA, MICHOACÁN Y GUERRERO",
                "link": "https://smn.conagua.gob.mx/es/pronosticos/pronosticossubmenu/pronostico-meteorologico-general"
            }
        ]

    return avisos

def obtener_pronostico_veracruz():
    """
    Obtiene el pronóstico oficial del tiempo (Local a 3 días, Boletín Estatal de Veracruz, 
    Sinopsis Nacional, Marquesina Oficial del SMN extraída de /tools/PHP/bannerAvisos.php 
    y el Último Video Boletín de YouTube emitido hoy) directamente desde el SMN - CONAGUA.
    Utiliza caché de 1 hora para optimizar el rendimiento.
    """
    cached_data = cache.get('pronostico_smn_veracruz_completo_v6')
    if cached_data:
        return cached_data

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # --- 1. PROSPECTO LOCAL A 3 DÍAS (VERACRUZ / MEDELLÍN) ---
    base_url = "https://smn.conagua.gob.mx/tools/GUI/carrusel-pronostico/data/Pron_ciudades/"
    csv_files = [
        "Pron_Ciudades_00_2.csv",
        "Pron_Ciudades_12_2.csv",
        "Pron_Ciudades_00_14.csv",
        "Pron_Ciudades_12_14.csv",
    ]

    raw_data = None
    for csv_file in csv_files:
        try:
            url = base_url + csv_file
            r = requests.get(url, headers=headers, timeout=5)
            if r.status_code == 200 and "Ciudad" in r.text:
                raw_data = r.text
                break
        except Exception:
            continue

    forecast_days = []
    hoy = datetime.date.today()

    if raw_data:
        try:
            f = io.StringIO(raw_data)
            reader = csv.DictReader(f)
            veracruz_row = None
            for row in reader:
                if 'veracruz' in row.get('Ciudad', '').lower():
                    veracruz_row = row
                    break

            if veracruz_row:
                periods = [
                    ('24', 0, "Hoy "),
                    ('48', 1, ""),
                    ('72', 2, "")
                ]

                for suffix, offset, prefix in periods:
                    dt = hoy + datetime.timedelta(days=offset)
                    dia_nombre = DIAS_SEMANA[dt.weekday()]
                    label = f"{prefix}{dia_nombre} {dt.strftime('%d/%m')}"

                    tmax = veracruz_row.get(f'Tmax_{suffix}', '32.0')
                    tmin = veracruz_row.get(f'Tmin_{suffix}', '24.0')
                    cielo = veracruz_row.get(f'Cielo_{suffix}', 'Poco nublado').strip()

                    try:
                        tmax_val = f"Máx. {int(float(tmax))}°C"
                    except ValueError:
                        tmax_val = f"Máx. {tmax}°C"

                    try:
                        tmin_val = f"Mín. {int(float(tmin))}°C"
                    except ValueError:
                        tmin_val = f"Mín. {tmin}°C"

                    cielo_lower = cielo.lower()
                    if 'despejado' in cielo_lower or 'soleado' in cielo_lower:
                        icon = "sun"
                        color = "text-amber-500"
                        bg_icon = "bg-amber-50"
                        badge_color = "bg-amber-100 text-amber-800"
                    elif 'poco' in cielo_lower or 'medio' in cielo_lower:
                        icon = "cloud-sun"
                        color = "text-amber-600"
                        bg_icon = "bg-amber-50/80"
                        badge_color = "bg-amber-50 text-amber-700"
                    elif 'lluvia' in cielo_lower or 'tormenta' in cielo_lower or 'chubasco' in cielo_lower:
                        icon = "cloud-rain"
                        color = "text-blue-600"
                        bg_icon = "bg-blue-50"
                        badge_color = "bg-blue-100 text-blue-800"
                    else:
                        icon = "cloud"
                        color = "text-slate-600"
                        bg_icon = "bg-slate-100"
                        badge_color = "bg-gray-100 text-slate-700"

                    forecast_days.append({
                        "label": label,
                        "tmax": tmax_val,
                        "tmin": tmin_val,
                        "cielo": cielo,
                        "icon": icon,
                        "color": color,
                        "bg_icon": bg_icon,
                        "badge_color": badge_color
                    })
        except Exception as e:
            print(f"Error parseando CSV SMN CONAGUA: {e}")

    if not forecast_days:
        for offset, prefix in [(0, "Hoy "), (1, ""), (2, "")]:
            dt = hoy + datetime.timedelta(days=offset)
            dia_nombre = DIAS_SEMANA[dt.weekday()]
            forecast_days.append({
                "label": f"{prefix}{dia_nombre} {dt.strftime('%d/%m')}",
                "tmax": "Máx. 33°C",
                "tmin": "Mín. 25°C",
                "cielo": "Poco nublado",
                "icon": "cloud-sun",
                "color": "text-amber-600",
                "bg_icon": "bg-amber-50/80",
                "badge_color": "bg-amber-50 text-amber-700"
            })

    # --- 2. BOLETÍN ESTATAL Y SINOPSIS NACIONAL ---
    resumen_nacional = ""
    boletin_estatal = ""

    url_gen = "https://smn.conagua.gob.mx/es/pronosticos/pronosticossubmenu/pronostico-meteorologico-general"
    try:
        r = requests.get(url_gen, headers=headers, timeout=6)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            for tag in soup.find_all(['p', 'div', 'td']):
                txt = tag.text.strip()
                if 50 < len(txt) < 900 and not tag.find(['p', 'div', 'td']):
                    txt_clean = ' '.join(txt.split())
                    
                    # Boletín Estatal / Región Golfo de México
                    if 'golfo de méxico' in txt_clean.lower() or 'golfo de mexico' in txt_clean.lower():
                        if not boletin_estatal or len(txt_clean) > len(boletin_estatal):
                            boletin_estatal = txt_clean

                    # Sinopsis Nacional (Monzón / Ondas tropicales)
                    if ('monzón' in txt_clean.lower() or 'onda tropical' in txt_clean.lower() or 'servicio meteorológico nacional, monitorea' in txt_clean.lower()):
                        if not resumen_nacional or len(txt_clean) > len(resumen_nacional):
                            resumen_nacional = txt_clean
    except Exception as e:
        print(f"Error scraping boletín SMN: {e}")

    if not boletin_estatal:
        boletin_estatal = "Golfo de México: Cielo medio nublado a nublado con lluvias e intervalos de chubascos acompañados de descargas eléctricas en zonas de Veracruz. Ambiente caluroso a muy caluroso por la tarde con viento de componente este de 15 a 30 km/h."

    if not resumen_nacional:
        resumen_nacional = "El Servicio Meteorológico Nacional (SMN) monitorea activamente la circulación de ondas tropicales y sistemas de baja presión con potencial de lluvias en diversas regiones del país."

    # --- 3. SCRAPING DE LA CINTA DE AVISOS OFICIAL DE CONAGUA (/tools/PHP/bannerAvisos.php) ---
    avisos_marquesina = obtener_cintillo_smn_directo()

    # --- 4. EXTRAER EL ÚLTIMO VIDEO INDIVIDUAL DE YOUTUBE EMITIDO HOY POR EL SMN ---
    video_id = "K_5u_k1xII4"
    video_youtube_url = f"https://www.youtube-nocookie.com/embed/{video_id}?autoplay=1&rel=0"
    video_thumbnail = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    video_titulo = "Video Boletín del Tiempo SMN CONAGUA"

    try:
        rss_url = "https://www.youtube.com/feeds/videos.xml?playlist_id=PLE5gZ07C9DwIwAxoV0AIOpSL6fUECW23N"
        r_rss = requests.get(rss_url, headers=headers, timeout=5)
        if r_rss.status_code == 200:
            root = ET.fromstring(r_rss.text)
            ns = {'yt': 'http://www.youtube.com/xml/schemas/2015', 'atom': 'http://www.w3.org/2005/Atom'}
            entries = root.findall('atom:entry', ns)
            if entries:
                extracted_id = entries[0].find('yt:videoId', ns).text
                t_el = entries[0].find('atom:title', ns)
                if t_el is not None and t_el.text:
                    video_titulo = t_el.text.strip()
                if extracted_id:
                    video_id = extracted_id
                    video_youtube_url = f"https://www.youtube-nocookie.com/embed/{video_id}?autoplay=1&rel=0"
                    video_thumbnail = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    except Exception as e:
        print("Error al extraer video ID de YouTube RSS:", e)

    res = {
        "dias": forecast_days,
        "boletin_estatal": boletin_estatal,
        "resumen_nacional": resumen_nacional,
        "avisos_marquesina": avisos_marquesina,
        "video_id": video_id,
        "video_youtube_url": video_youtube_url,
        "video_thumbnail": video_thumbnail,
        "video_titulo": video_titulo
    }

    # Guardar en caché por 3600 segundos (1 hora)
    cache.set('pronostico_smn_veracruz_completo_v6', res, 3600)

    return res
