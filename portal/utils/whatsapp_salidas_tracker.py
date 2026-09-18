# ==============================================================================
#  🚑 ALGORITMO DE SEGUIMIENTO Y PROCESAMIENTO AUTOMÁTICO DE SALIDAS
#  Grupo Oficial: Protección civil Medellín (120363042493725288@g.us)
#  Copyright (c) 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
# ==============================================================================

import re
import json
import base64
import logging
import datetime
import urllib.request
from io import BytesIO
from django.utils import timezone
from django.core.files.base import ContentFile
from django.db.models import Q
from portal.models import VehiculoUnidad, BitacoraSalidaVehiculo
from portal.utils.whatsapp_utils import EVOLUTION_API_URL, EVOLUTION_API_KEY, INSTANCE_NAME

logger = logging.getLogger(__name__)

GRUPO_SALIDAS_JID = "120363042493725288@g.us"


def normalizar_texto(texto):
    """Limpia tildes, caracteres especiales y convierte a minúsculas para análisis regex robusto."""
    if not texto:
        return ""
    s = texto.lower().strip()
    s = s.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    return s


def extraer_unidad(texto_original):
    """
    Detecta la unidad operativa mencionada en el texto (ej: 'Unidad 041', 'U-098', '098', 'Sale la 208').
    Retorna el número de unidad en formato limpio (ej: '041', '098', '208', '072') o None.
    """
    texto = normalizar_texto(texto_original)
    
    # 1. Patrón con prefijos: 'unidad 041', 'u-098', 'sale la 208', 'u 098', 'amb-208', 'pipa 072'
    m = re.search(r'(?:unidad|u|amb|ambulancia|pipa|camion|camioneta|moto|sale\s+la|sale\s+el|llega\s+la|entra\s+la)[-\s:]*(\d{2,4})', texto)
    if m:
        return m.group(1)

    # 2. Si el texto inicia directamente con el número de unidad (ej: '041 en base', '098 llegando')
    m_inicio = re.match(r'^(\d{2,4})\b', texto)
    if m_inicio:
        return m_inicio.group(1)

    # 3. Números típicos de 3 dígitos (como 041, 098, 208, 072) que no sean códigos 10
    digitos = re.findall(r'\b\d{2,4}\b', texto)
    for num in digitos:
        if num in ['10', '108', '104', '1020']:  # evitar códigos clave 10
            continue
        # Si tiene 3 dígitos o empieza con 0 (ej: 041, 098, 072, 096, 208)
        if num.startswith('0') or len(num) == 3:
            return num
        # Si coincide con alguna unidad en la base de datos
        num_clean = num.lstrip('0') or '0'
        if VehiculoUnidad.objects.filter(
            Q(numero_unidad__icontains=num) |
            Q(numero_unidad__icontains=num_clean) |
            Q(nombre_identificador__icontains=num)
        ).exists():
            return num

    return None


def buscar_o_crear_vehiculo(num_unidad):
    """
    Encuentra la unidad en VehiculoUnidad o la crea automáticamente si es nueva.
    """
    if not num_unidad:
        return None
        
    num_limpio = num_unidad.strip()
    num_sin_ceros = num_limpio.lstrip('0') or '0'

    # Buscar por coincidencia exacta o parcial
    unidad = VehiculoUnidad.objects.filter(
        Q(numero_unidad__iexact=num_limpio) |
        Q(numero_unidad__iexact=f"U-{num_limpio}") |
        Q(numero_unidad__icontains=num_limpio) |
        Q(nombre_identificador__icontains=num_limpio)
    ).first()

    if not unidad:
        # Fallback con el número sin ceros a la izquierda (ej: '98' para '098')
        unidad = VehiculoUnidad.objects.filter(
            Q(numero_unidad__icontains=num_sin_ceros) |
            Q(nombre_identificador__icontains=num_sin_ceros)
        ).first()

    if not unidad:
        # Crear la unidad para no perder el registro
        tipo = 'PickUp'
        try:
            val_int = int(num_sin_ceros)
            if val_int in [97, 98, 208]:
                tipo = 'Ambulancia'
            elif val_int in [72, 73]:
                tipo = 'Pipa'
            elif val_int in [47]:
                tipo = 'Moto'
        except Exception:
            pass

        unidad = VehiculoUnidad.objects.create(
            numero_unidad=f"U-{num_limpio}",
            nombre_identificador=f"Unidad {num_limpio}",
            tipo_vehiculo=tipo,
            estatus='DISPONIBLE'
        )
        logger.info(f"Unidad creada automáticamente en base de datos: {unidad.nombre_identificador}")

    return unidad


def obtener_base64_media(key, message):
    """
    Obtiene la imagen en base64 desde Evolution API si el webhook no la trajo directa.
    """
    url = f"{EVOLUTION_API_URL}/chat/getBase64FromMediaMessage/{INSTANCE_NAME}"
    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_API_KEY
    }
    payload = {
        "message": {
            "key": key,
            "message": message
        },
        "convertToMp4": False
    }

    try:
        req_data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=req_data, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=15) as response:
            res_json = json.loads(response.read().decode('utf-8'))
            return res_json.get("base64")
    except Exception as e:
        logger.error(f"Error al obtener base64 de media: {e}")
        return None


def clasificar_mensaje_operativo(texto_original):
    """
    Analiza el texto y clasifica si es 'SALIDA', 'ENTRADA' o 'NOVEDAD'.
    Retorna (tipo_evento, motivo_o_detalle)
    """
    texto = normalizar_texto(texto_original)

    # 1. Patrones de LLEGADA / ENTRADA A BASE (Prioridad de cierre)
    patrones_llegada = [
        r'\b(?:llegando|llegada|llegamos|llega|arribando)\s+(?:a|al)?\s*(?:base|central|estacion)\b',
        r'\ben\s+base\b',
        r'\b(?:entra|entrada|entrando|retorna|retorno|retornando)\s+(?:a|al)?\s*(?:base|central|sin novedad)\b',
        r'\b10[-\s]?8\b',
        r'\bconcluy(?:e|endo|o)\b'
    ]
    for p in patrones_llegada:
        if re.search(p, texto):
            return 'ENTRADA', texto_original.strip()

    # 2. Patrones de SALIDA / DESPACHO
    patrones_salida = [
        r'\b(?:sale|salida|saliendo|salimos)\s+(?:a|hacia|al|rumbo a)?\s*(.+)',
        r'\b(?:rumbo|comision|despacho)\s+(?:a|hacia|al)?\s*(.+)',
        r'\b(?:se traslada|traslado)\s+(?:a|hacia|al)?\s*(.+)',
        r'\b(?:atender|apoyo)\s+(?:a|en)?\s*(.+)'
    ]
    for p in patrones_salida:
        m = re.search(p, texto)
        if m:
            motivo = m.group(1).strip()
            # Limpiar residuos comunes respetando límites de palabras (ej: no cortar 'a' de 'asuntos')
            motivo = re.sub(r'^(?:la|el|unidad|u-?)?\s*\d*\s*(?:\b(?:a|al|hacia)\b\s*)?', '', motivo)
            return 'SALIDA', motivo.capitalize() if motivo else "Servicio operativo / comisión"

    # Si menciona 'sale' aunque no tenga el motivo claro
    if 'sale' in texto or 'salida' in texto:
        motivo_limpio = re.sub(r'^(?:sale|salida)\s+(?:la|el|unidad|u-?)?\s*\d*\s*(?:\b(?:a|al|hacia)\b\s*)?', '', texto)
        return 'SALIDA', motivo_limpio.capitalize() if motivo_limpio else "Salida operativa"

    return 'NOVEDAD', texto_original.strip()


def procesar_mensaje_grupo_salidas(data):
    """
    Procesador maestro para los mensajes del grupo 'Protección civil Medellín'.
    Extrae unidades, fotos del tablero (odómetro/gasolina), horarios y actualiza la bitácora.
    """
    key = data.get("key", {})
    remote_jid = key.get("remoteJid", "") or data.get("remoteJid", "")
    
    # ⚠️ REGLA DE ORO: Filtrar EXCLUSIVAMENTE el grupo de Protección Civil Medellín
    if remote_jid != GRUPO_SALIDAS_JID:
        return {"status": "ignored_different_group"}

    push_name = data.get("pushName", "") or "Personal Operativo"
    msg_timestamp = data.get("messageTimestamp")
    
    if msg_timestamp:
        try:
            dt_evento = datetime.datetime.fromtimestamp(int(msg_timestamp), tz=datetime.timezone.utc)
            dt_evento = timezone.localtime(dt_evento)
        except Exception:
            dt_evento = timezone.now()
    else:
        dt_evento = timezone.now()

    message = data.get("message", {})
    image_msg = message.get("imageMessage")
    
    # Extraer el texto del mensaje (conversación directa o pie de foto)
    texto = ""
    if "conversation" in message:
        texto = message["conversation"]
    elif "extendedTextMessage" in message:
        texto = message["extendedTextMessage"].get("text", "")
    elif image_msg:
        texto = image_msg.get("caption", "")

    texto_limpio = texto.strip()
    if not texto_limpio and not image_msg:
        return {"status": "empty_message"}

    logger.info(f"[WHATSAPP PC] Mensaje recibido de {push_name}: '{texto_limpio}' (Tiene foto: {bool(image_msg)})")

    # Identificar la unidad
    num_unidad = extraer_unidad(texto_limpio)
    
    # Si no detectó la unidad en el texto pero es un mensaje con foto o llegada,
    # verificar si el remitente tiene una salida activa reciente para asociarla
    vehiculo = None
    if num_unidad:
        vehiculo = buscar_o_crear_vehiculo(num_unidad)
    else:
        # Buscar la salida activa más reciente si dice 'llegando a base' o 'en base'
        salida_pendiente = BitacoraSalidaVehiculo.objects.filter(
            completado=False,
            fecha_salida__gte=dt_evento - datetime.timedelta(hours=14)
        ).order_by('-fecha_salida').first()
        if salida_pendiente and ('base' in normalizar_texto(texto_limpio) or '10-8' in normalizar_texto(texto_limpio)):
            vehiculo = salida_pendiente.unidad
            num_unidad = vehiculo.numero_unidad

    if not vehiculo:
        logger.info(f"[WHATSAPP PC] No se detectó unidad vehicular en el mensaje: '{texto_limpio}'")
        return {"status": "no_unit_detected", "text": texto_limpio}

    # Clasificar el tipo de evento: SALIDA vs ENTRADA vs NOVEDAD
    tipo_evento, detalle_evento = clasificar_mensaje_operativo(texto_limpio)

    # Descargar la imagen del tablero si viene adjunta
    foto_archivo = None
    if image_msg:
        b64_str = data.get("base64") or image_msg.get("base64")
        if not b64_str:
            b64_str = obtener_base64_media(key, message)

        if b64_str:
            try:
                # Quitar prefijo data:image/... si lo tiene
                if "," in b64_str:
                    b64_str = b64_str.split(",")[1]
                img_data = base64.b64decode(b64_str)
                nombre_archivo = f"tablero_{vehiculo.numero_unidad}_{int(dt_evento.timestamp())}.jpg"
                foto_archivo = ContentFile(img_data, name=nombre_archivo)
            except Exception as e:
                logger.error(f"Error al decodificar foto del tablero: {e}")

    # =========================================================================
    # CASO 1: SALIDA DE UNIDAD (ABRIR SERVICIO)
    # =========================================================================
    if tipo_evento == 'SALIDA':
        # Verificar si ya existe una salida abierta para esta unidad en las últimas 4 horas
        salida_existente = BitacoraSalidaVehiculo.objects.filter(
            unidad=vehiculo,
            completado=False,
            fecha_salida__gte=dt_evento - datetime.timedelta(hours=6)
        ).first()

        if salida_existente:
            # Ya estaba abierta, anexar novedad o actualizar foto si no tenía
            if foto_archivo and not salida_existente.foto_odometro_salida:
                salida_existente.foto_odometro_salida = foto_archivo
            salida_existente.descripcion_servicio += f" | {detalle_evento}"
            salida_existente.save()
            logger.info(f"[WHATSAPP PC] Salida ya activa para {vehiculo.nombre_identificador}. Novedad anexada.")
            return {"status": "salida_updated", "unidad": vehiculo.numero_unidad}

        # Crear nuevo registro de salida
        nueva_salida = BitacoraSalidaVehiculo.objects.create(
            unidad=vehiculo,
            operador_nombre=push_name,
            descripcion_servicio=detalle_evento or "Salida operativa de comisión",
            fecha_salida=dt_evento,
            odometro_salida=vehiculo.odometro_actual or 0,
            gasolina_salida=vehiculo.nivel_gasolina_actual or 'Lleno',
            foto_odometro_salida=foto_archivo,
            completado=False
        )

        # Actualizar estado de la unidad a EN_SERVICIO
        vehiculo.estatus = 'EN_SERVICIO'
        vehiculo.save()

        logger.info(f"[WHATSAPP PC] 🚨 SALIDA REGISTRADA con éxito: {vehiculo.nombre_identificador} | Operador: {push_name} | Motivo: {detalle_evento}")
        return {
            "status": "salida_creada",
            "salida_id": nueva_salida.id,
            "unidad": vehiculo.numero_unidad,
            "operador": push_name
        }

    # =========================================================================
    # CASO 2: ENTRADA / LLEGADA A BASE (CERRAR SERVICIO)
    # =========================================================================
    elif tipo_evento == 'ENTRADA':
        # Buscar la salida abierta más reciente de esta unidad
        salida = BitacoraSalidaVehiculo.objects.filter(
            unidad=vehiculo,
            completado=False
        ).order_by('-fecha_salida').first()

        if salida:
            salida.fecha_llegada = dt_evento
            duracion = max(1, int((dt_evento - salida.fecha_salida).total_seconds() / 60))
            salida.duracion_minutos = duracion
            salida.completado = True
            if foto_archivo:
                salida.foto_odometro_llegada = foto_archivo
            salida.save()

            # Actualizar unidad a DISPONIBLE y registrar hora de retorno
            vehiculo.estatus = 'DISPONIBLE'
            vehiculo.ultima_salida_finalizada = dt_evento
            vehiculo.save()

            logger.info(f"[WHATSAPP PC] 🟢 RETORNO A BASE REGISTRADO: {vehiculo.nombre_identificador} | Duración: {duracion} min")
            return {
                "status": "entrada_registrada",
                "salida_id": salida.id,
                "unidad": vehiculo.numero_unidad,
                "duracion_min": duracion
            }
        else:
            # No había salida abierta registrada (quizás salieron antes de conectar el bot)
            # Creamos una salida ya concluida de cortesía para que quede registro
            salida_express = BitacoraSalidaVehiculo.objects.create(
                unidad=vehiculo,
                operador_nombre=push_name,
                descripcion_servicio="Retorno a base (Salida no registrada previamente)",
                fecha_salida=dt_evento - datetime.timedelta(minutes=30),
                fecha_llegada=dt_evento,
                duracion_minutos=30,
                foto_odometro_llegada=foto_archivo,
                odometro_salida=vehiculo.odometro_actual or 0,
                completado=True
            )
            vehiculo.estatus = 'DISPONIBLE'
            vehiculo.ultima_salida_finalizada = dt_evento
            vehiculo.save()

            logger.info(f"[WHATSAPP PC] Llegada sin salida previa registrada. Creada bitácora de cortesía.")
            return {"status": "entrada_sin_salida_registrada", "salida_id": salida_express.id}

    # =========================================================================
    # CASO 3: NOVEDAD O ACTUALIZACIÓN DURANTE EL SERVICIO
    # =========================================================================
    else:
        salida_activa = BitacoraSalidaVehiculo.objects.filter(
            unidad=vehiculo,
            completado=False
        ).order_by('-fecha_salida').first()

        if salida_activa:
            salida_activa.descripcion_servicio += f" | [{dt_evento.strftime('%H:%M')}]: {detalle_evento}"
            salida_activa.save()
            logger.info(f"[WHATSAPP PC] Novedad añadida a salida #{salida_activa.id}: {detalle_evento}")
            return {"status": "novedad_anexada", "salida_id": salida_activa.id}

        return {"status": "mensaje_ignorado"}
