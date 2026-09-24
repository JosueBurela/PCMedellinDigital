import re
import datetime
from django.utils import timezone
from django.core.files.base import ContentFile
import base64
import urllib.request
import json
import logging
from portal.models import BitacoraSalidaVehiculo, VehiculoUnidad
from .whatsapp_utils import (
    EVOLUTION_API_URL,
    EVOLUTION_API_KEY,
    INSTANCE_NAME
)

GRUPO_SALIDAS_JID = "120363042493725288@g.us"

logger = logging.getLogger(__name__)

def normalizar_texto(texto):
    return re.sub(r'[^\w\s]', '', texto).lower()

def extraer_unidad(texto):
    patron = r'\b(?:unidad|u-?|movil|pipa|moto)?\s*(041|047|072|073|096|097|098|208)\b'
    match = re.search(patron, texto, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def buscar_vehiculo(num_unidad):
    num_limpio = num_unidad.strip()
    return VehiculoUnidad.objects.filter(numero_unidad=num_limpio).first()

def obtener_base64_media(key, message):
    url = f"{EVOLUTION_API_URL}/chat/getBase64FromMediaMessage/{INSTANCE_NAME}"
    headers = {"Content-Type": "application/json", "apikey": EVOLUTION_API_KEY}
    payload = {"message": {"key": key, "message": message}, "convertToMp4": False}
    try:
        req_data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=req_data, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode('utf-8')).get("base64")
    except Exception as e:
        logger.error(f"Error media: {e}")
        return None

def clasificar_mensaje_operativo(texto_original):
    texto = normalizar_texto(texto_original)
    
    # Pre-filtro: Si el mensaje es una simple confirmación de la central, no es llegada ni salida
    if re.search(r'^(enterado|recibido|copiado|qsl|pendiente|ok)\s+(en\s+)?(base|central|estacion)$', texto.strip()):
        return 'NOVEDAD'
        
    # Remover frases de confirmación que contienen "en base" para evitar falsos positivos
    texto_evaluar = re.sub(r'\b(enterado|recibido|copiado|qsl|pendiente)\s+(en\s+)?base\b', '', texto)

    patrones_llegada = [
        r'\b(?:llegando|llegada|llegamos|llega|arribando)\s+(?:a|al)?\s*(?:base|central|estacion)\b',
        r'\ben\s+base\b',
        r'\b(?:entra|entrada|entrando|retorna|retorno|retornando)\s+(?:a|al)?\s*(?:base|central|sin novedad)\b',
        r'\b10[-\s]?8\b',
        r'\bconcluy(?:e|endo|o)\b'
    ]
    for p in patrones_llegada:
        if re.search(p, texto_evaluar): return 'ENTRADA'

    patrones_salida = [
        r'\b(?:sale|salida|saliendo|salimos)\b',
        r'\b(?:rumbo|comision|despacho|encomienda)\b',
        r'\b(?:se traslada|traslado|trasladamos)\b',
        r'\b(?:atender|apoyo)\b',
        r'\b(?:al servicio|al punto|en camino|avanza|avanzando|aproxima|aproximando|procede|dirige|dirigiendo)\b'
    ]
    for p in patrones_salida:
        if re.search(p, texto_evaluar): return 'SALIDA'
    return 'NOVEDAD'

def procesar_mensaje_grupo_salidas(data):
    key = data.get("key", {})
    remote_jid = key.get("remoteJid", "") or data.get("remoteJid", "")
    participant_jid = key.get("participant", "") or data.get("participant", "")
    
    if remote_jid != GRUPO_SALIDAS_JID:
        return {"status": "ignored_different_group"}

    push_name = data.get("pushName", "") or "Personal Operativo"
    if not participant_jid:
        participant_jid = push_name

    msg_timestamp = data.get("messageTimestamp")
    if msg_timestamp:
        try:
            dt_evento = timezone.localtime(datetime.datetime.fromtimestamp(int(msg_timestamp), tz=datetime.timezone.utc))
        except Exception: dt_evento = timezone.now()
    else: dt_evento = timezone.now()

    message = data.get("message", {})
    image_msg = message.get("imageMessage")
    texto = message.get("conversation", message.get("extendedTextMessage", {}).get("text", image_msg.get("caption", "") if image_msg else ""))
    texto_limpio = texto.strip()
    if not texto_limpio and not image_msg: return {"status": "empty_message"}

    logger.info(f"[WHATSAPP PC] Mensaje de {push_name} ({participant_jid}): '{texto_limpio}'")

    num_unidad = extraer_unidad(texto_limpio)
    vehiculo = buscar_vehiculo(num_unidad) if num_unidad else None

    salida_activa_usuario = BitacoraSalidaVehiculo.objects.filter(
        operador_telefono=participant_jid, completado=False,
        fecha_salida__gte=dt_evento - datetime.timedelta(hours=14)
    ).order_by('-fecha_salida').first()

    tipo_evento = clasificar_mensaje_operativo(texto_limpio)

    # Inferencia inteligente si no se nombra unidad
    if not vehiculo:
        quoted_context = message.get("extendedTextMessage", {}).get("contextInfo", {})
        quoted_participant = quoted_context.get("participant", "")
        quoted_msg = quoted_context.get("quotedMessage", {})
        
        # 1. ¿El mensaje original mencionado tiene unidad?
        if quoted_msg:
            quoted_text = quoted_msg.get("conversation", quoted_msg.get("extendedTextMessage", {}).get("text", ""))
            if not quoted_text and "imageMessage" in quoted_msg:
                quoted_text = quoted_msg["imageMessage"].get("caption", "")
            if quoted_text:
                num_unidad = extraer_unidad(quoted_text)
                if num_unidad: vehiculo = buscar_vehiculo(num_unidad)

        # 2. ¿El participante al que le están respondiendo tiene una salida activa?
        if not vehiculo and quoted_participant:
            salida_citada = BitacoraSalidaVehiculo.objects.filter(
                operador_telefono=quoted_participant, completado=False,
                fecha_salida__gte=dt_evento - datetime.timedelta(hours=14)
            ).order_by('-fecha_salida').first()
            if salida_citada: vehiculo = salida_citada.unidad

        # 3. ¿El autor actual tiene salida activa?
        if not vehiculo and salida_activa_usuario:
            vehiculo = salida_activa_usuario.unidad
            
        # 4. Fallback general a la salida más reciente de la flotilla
        if not vehiculo:
            salida_pendiente = BitacoraSalidaVehiculo.objects.filter(completado=False, fecha_salida__gte=dt_evento - datetime.timedelta(hours=14)).order_by('-fecha_salida').first()
            if salida_pendiente: vehiculo = salida_pendiente.unidad

    if not vehiculo: return {"status": "no_unit_detected"}

    foto_archivo = None
    foto_url = ""
    if image_msg:
        b64_str = data.get("base64") or image_msg.get("base64")
        if not b64_str: b64_str = obtener_base64_media(key, message)
        if b64_str:
            try:
                if "," in b64_str: b64_str = b64_str.split(",")[1]
                file_data = base64.b64decode(b64_str)
                foto_archivo = ContentFile(file_data, name=f"tab_{vehiculo.numero_unidad}_{int(dt_evento.timestamp())}.jpg")
                from django.core.files.storage import default_storage
                saved_name = default_storage.save(f"salidas_media/nov_{vehiculo.numero_unidad}_{int(dt_evento.timestamp())}.jpg", ContentFile(file_data))
                foto_url = default_storage.url(saved_name)
            except Exception as e:
                logger.error(f"Error procesando foto URL: {e}")

    if foto_url:
        raw_text = f"{texto_limpio} [FOTO_URL:{foto_url}]".strip()
    else:
        raw_text = texto_limpio if texto_limpio else "[FOTO / IMAGEN]"
        
    formatted_msg = f"[{dt_evento.strftime('%H:%M')}] {push_name}: {raw_text}"

    if tipo_evento == 'SALIDA':
        if salida_activa_usuario:
            minutos = (dt_evento - salida_activa_usuario.fecha_salida).total_seconds() / 60
            if salida_activa_usuario.unidad == vehiculo and minutos < 60:
                if foto_archivo and not salida_activa_usuario.foto_odometro_salida: salida_activa_usuario.foto_odometro_salida = foto_archivo
                salida_activa_usuario.descripcion_servicio += f"\n{formatted_msg}"
                salida_activa_usuario.save()
                return {"status": "salida_updated"}
            else:
                salida_activa_usuario.completado = True
                salida_activa_usuario.fecha_llegada = dt_evento
                salida_activa_usuario.descripcion_servicio += "\n[Cierre automático: Operador tomó otra unidad]"
                salida_activa_usuario.save()
                salida_activa_usuario.unidad.estatus = 'DISPONIBLE'
                salida_activa_usuario.unidad.save()

        salida_existente = BitacoraSalidaVehiculo.objects.filter(unidad=vehiculo, completado=False, fecha_salida__gte=dt_evento - datetime.timedelta(hours=14)).first()
        if salida_existente:
            if foto_archivo and not salida_existente.foto_odometro_salida: salida_existente.foto_odometro_salida = foto_archivo
            salida_existente.descripcion_servicio += f"\n{formatted_msg}"
            salida_existente.operador_telefono = participant_jid
            salida_existente.operador_nombre = push_name
            salida_existente.save()
            return {"status": "salida_updated_taken_over"}

        nueva = BitacoraSalidaVehiculo.objects.create(
            unidad=vehiculo, operador_nombre=push_name, operador_telefono=participant_jid,
            descripcion_servicio=formatted_msg, fecha_salida=dt_evento,
            odometro_salida=vehiculo.odometro_actual or 0, gasolina_salida=vehiculo.nivel_gasolina_actual or 'Lleno',
            foto_odometro_salida=foto_archivo, completado=False
        )
        vehiculo.estatus = 'EN_SERVICIO'
        vehiculo.save()
        return {"status": "salida_creada", "salida_id": nueva.id}

    elif tipo_evento == 'ENTRADA':
        salida = BitacoraSalidaVehiculo.objects.filter(unidad=vehiculo, completado=False).order_by('-fecha_salida').first()
        if salida:
            salida.fecha_llegada = dt_evento
            salida.duracion_minutos = max(1, int((dt_evento - salida.fecha_salida).total_seconds() / 60))
            salida.completado = True
            salida.descripcion_servicio += f"\n{formatted_msg}"
            if foto_archivo: salida.foto_odometro_llegada = foto_archivo
            salida.save()
        else:
            BitacoraSalidaVehiculo.objects.create(
                unidad=vehiculo, operador_nombre=push_name, operador_telefono=participant_jid,
                descripcion_servicio=f"[CORTESÍA / RETORNO SIN SALIDA PREVIA]\n{formatted_msg}", fecha_salida=dt_evento - datetime.timedelta(minutes=30),
                fecha_llegada=dt_evento, duracion_minutos=30, foto_odometro_llegada=foto_archivo,
                odometro_salida=vehiculo.odometro_actual or 0, completado=True
            )
        vehiculo.estatus = 'DISPONIBLE'
        vehiculo.ultima_salida_finalizada = dt_evento
        vehiculo.save()
        return {"status": "entrada_registrada"}

    else:
        salida_activa = BitacoraSalidaVehiculo.objects.filter(unidad=vehiculo, completado=False).order_by('-fecha_salida').first()
        if salida_activa:
            salida_activa.descripcion_servicio += f"\n{formatted_msg}"
            if foto_archivo and not salida_activa.foto_odometro_salida: salida_activa.foto_odometro_salida = foto_archivo
            salida_activa.save()
            return {"status": "novedad_anexada"}
        return {"status": "mensaje_ignorado"}
