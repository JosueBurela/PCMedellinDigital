# ==============================================================================
#  🛡️ SISTEMA DIGITAL DE PROTECCIÓN CIVIL Y BOMBEROS
#  Copyright (c) 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
#  Desarrollado y Diseñado por: Josué Jaziel Delgado Burela
#  Contacto y Soporte: jburela1@gmal.com
# ==============================================================================

import json
import logging
import urllib.request
import urllib.error
import datetime
import re

import os

logger = logging.getLogger(__name__)

# ── Configuración de Evolution API (Leída desde .env) ───────────────────────
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")
INSTANCE_NAME = os.getenv("INSTANCE_NAME", "PCMedellin")
GRUPO_ALERTAS_JID = os.getenv("GRUPO_ALERTAS_JID", "120363409447790752@g.us")

# ── Mapeo de emojis por tipo de servicio ────────────────────────────────────
EMOJI_TIPO_SERVICIO = {
    'GAS': '⛽ FUGA DE GAS',
    'FUEGO': '🔥 INCENDIO',
    'ARBOL': '🌳 CAÍDA DE ÁRBOL',
    'AGUA': '🌊 INUNDACIÓN',
    'CABLE': '⚡ CABLE CAÍDO',
    'ABEJAS': '🐝 ENJAMBRE DE ABEJAS',
    'CHOQUE': '🚗 ACCIDENTE VIAL',
    'OTRO': '📋 OTRO SERVICIO',
}

EMOJI_PRIORIDAD = {
    'BAJA': '🟢 BAJA',
    'MEDIA': '🟡 MEDIA',
    'ALTA': '🔴 ALTA',
}

EMOJI_ESTATUS = {
    'PENDIENTE': '⏳ PENDIENTE',
    'LEIDO': '👁️ LEÍDO',
    'EN_PROCESO': '🚑 EN CAMINO',
    'RESUELTO': '✅ RESUELTO',
}


def limpiar_numero_destino(remote_jid):
    """
    Limpia el sufijo @s.whatsapp.net si es un número individual para cumplir con el formato de Evolution API.
    Si es un grupo (@g.us), preserva el JID completo.
    """
    if not remote_jid:
        return ""
    str_jid = str(remote_jid).strip()
    if "@g.us" in str_jid:
        return str_jid
    return str_jid.replace("@s.whatsapp.net", "").strip()


def enviar_mensaje_whatsapp(remote_jid, texto):
    """
    Envía un mensaje de texto simple a través del API de WhatsApp (Evolution API).
    Retorna True si fue exitoso, False si falló.
    """
    url = f"{EVOLUTION_API_URL}/message/sendText/{INSTANCE_NAME}"
    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_API_KEY
    }
    payload = {
        "number": limpiar_numero_destino(remote_jid),
        "text": texto
    }

    req_data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=req_data, headers=headers, method='POST')

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return True
    except Exception as e:
        logger.error(f"Error al enviar mensaje de WhatsApp a {remote_jid}: {e}")
        return False


def enviar_botones_whatsapp(remote_jid, titulo, descripcion, footer, botones):
    """
    Envía un mensaje interactivo con botones de respuesta rápida (Quick Reply Buttons) por WhatsApp.
    Permite a los usuarios tocar un botón directamente en el chat para enviar una respuesta.
    """
    url = f"{EVOLUTION_API_URL}/message/sendButtons/{INSTANCE_NAME}"
    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_API_KEY
    }
    payload = {
        "number": limpiar_numero_destino(remote_jid),
        "title": titulo,
        "description": descripcion,
        "footer": footer,
        "buttons": [
            {
                "type": "reply",
                "displayText": b["displayText"],
                "id": b["id"]
            } for b in botones
        ]
    }

    req_data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=req_data, headers=headers, method='POST')

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return True
    except Exception as e:
        logger.error(f"Error al enviar botones de WhatsApp a {remote_jid}: {e}")
        return False


def enviar_encuesta_whatsapp(remote_jid, titulo_encuesta, opciones):
    """
    Envía un mensaje interactivo tipo Encuesta (Poll / Opciones clicables nativas) por WhatsApp.
    Permite a los usuarios seleccionar opciones con un solo toque.
    """
    url = f"{EVOLUTION_API_URL}/message/sendPoll/{INSTANCE_NAME}"
    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_API_KEY
    }
    payload = {
        "number": limpiar_numero_destino(remote_jid),
        "name": titulo_encuesta,
        "selectableCount": 1,
        "values": opciones
    }

    req_data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=req_data, headers=headers, method='POST')

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return True
    except Exception as e:
        logger.error(f"Error al enviar encuesta de WhatsApp a {remote_jid}: {e}")
        return False


def formatear_alerta_nueva(reporte):
    """
    Genera el mensaje descriptivo en texto para el grupo de WhatsApp.
    Muestra explícitamente que aún está SIN PERSONAL A CARGO (PENDIENTE).
    """
    tipo_display = EMOJI_TIPO_SERVICIO.get(reporte.tipo_servicio, f'📋 {reporte.tipo_servicio}')
    prioridad_display = EMOJI_PRIORIDAD.get(reporte.prioridad, reporte.prioridad)
    fecha = reporte.fecha_reporte.strftime('%d/%b/%Y %H:%M')

    encargado = "⚠️ *SIN PERSONAL A CARGO (PENDIENTE)*"
    if reporte.unidad_acudira:
        encargado = f"🚑 *Unidad:* {reporte.unidad_acudira}"
    elif reporte.responsables.exists():
        nombres = ", ".join([r.get_full_name() for r in reporte.responsables.all()])
        encargado = f"👷 *Personal:* {nombres}"

    mensaje = (
        f"🚨 *NUEVA ALERTA DE EMERGENCIA - PROTECCIÓN CIVIL* 🚨\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📋 *Folio:* {reporte.numero_reporte}\n"
        f"⚠️ *Tipo:* {tipo_display}\n"
        f"🔶 *Prioridad:* {prioridad_display}\n"
        f"👤 *Encargado:* {encargado}\n\n"
        f"📍 *Ubicación:*\n"
        f"   {reporte.direccion}\n"
        f"   Col. {reporte.colonia}, {reporte.localidad}\n\n"
        f"📝 *Descripción:*\n"
        f"   {reporte.descripcion}\n\n"
        f"👤 *Reportó:* {reporte.nombre_ciudadano}\n"
        f"📞 *Teléfono:* {reporte.telefono_ciudadano}\n"
        f"🕐 *Fecha:* {fecha}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 *Estatus:* {EMOJI_ESTATUS.get(reporte.estatus, reporte.estatus)}\n"
        f"🆔 Para actualizar bitácora:\n"
        f"_Bitacora {reporte.numero_reporte}: [tu actualización]_"
    )
    return mensaje


def formatear_actualizacion(reporte, cambios_texto):
    """
    Genera un mensaje formateado para notificar cambios en un reporte existente.
    """
    estatus_display = EMOJI_ESTATUS.get(reporte.estatus, reporte.estatus)

    partes = [
        f"📢 *ACTUALIZACIÓN DE REPORTE*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📋 *Folio:* {reporte.numero_reporte}\n"
        f"🔄 *Estatus:* {estatus_display}\n"
    ]

    if reporte.unidad_acudira:
        partes.append(f"🚑 *Unidad:* {reporte.unidad_acudira}\n")
    if reporte.tiempo_atencion:
        partes.append(f"⏱️ *Tiempo estimado:* {reporte.tiempo_atencion}\n")

    responsables = reporte.responsables.all()
    if responsables:
        nombres = ", ".join([r.get_full_name() for r in responsables])
        partes.append(f"👷 *Responsables:* {nombres}\n")

    if cambios_texto:
        partes.append(f"\n📝 *Cambios:*\n{cambios_texto}\n")

    partes.append(
        f"\n━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 {reporte.direccion}, Col. {reporte.colonia}"
    )

    return "".join(partes)


def normalizar_jids_whatsapp(telefono):
    """
    Normaliza un número de teléfono de México para generar los JIDs de WhatsApp válidos (con y sin el prefijo '1').
    """
    digits = re.sub(r'\D', '', str(telefono or ''))
    if not digits:
        return []
    
    jids = []
    if len(digits) == 10:
        jids = [f"521{digits}@s.whatsapp.net", f"52{digits}@s.whatsapp.net"]
    elif len(digits) == 13 and digits.startswith('521'):
        raw = digits[3:]
        jids = [f"521{raw}@s.whatsapp.net", f"52{raw}@s.whatsapp.net"]
    elif len(digits) == 12 and digits.startswith('52'):
        raw = digits[2:]
        jids = [f"521{raw}@s.whatsapp.net", f"52{raw}@s.whatsapp.net"]
    else:
        jids = [f"{digits}@s.whatsapp.net"]
    return list(dict.fromkeys(jids))


def notificar_trabajadores_turno_activo(reporte):
    """
    Envía la alerta individual y las opciones interactivas directamente al WhatsApp personal
    de los trabajadores de campo activos en el turno de hoy (con fallback a todos los trabajadores activos).
    """
    from portal.models import ProgramacionGuardia, Trabajador

    hoy = datetime.date.today()
    programacion = ProgramacionGuardia.objects.filter(fecha=hoy).select_related('plantilla').prefetch_related('plantilla__trabajadores').first()

    trabajadores = []
    nombre_guardia = "Guardia en Turno"
    if programacion and programacion.plantilla:
        nombre_guardia = programacion.plantilla.nombre
        trabajadores = list(programacion.plantilla.trabajadores.all())

    # Fallback: Si no hay guardia asignada o está vacía, notificar a todos los trabajadores registrados
    if not trabajadores:
        logger.info(f"No hay guardia activa asignada para hoy ({hoy}). Notificando a todos los trabajadores de campo registrados...")
        trabajadores = list(Trabajador.objects.all())
        nombre_guardia = "Personal Operativo General"

    if not trabajadores:
        logger.warning("No hay ningún trabajador de campo registrado en la base de datos para notificar.")
        return 0

    tipo_display = EMOJI_TIPO_SERVICIO.get(reporte.tipo_servicio, reporte.tipo_servicio)
    prioridad_display = EMOJI_PRIORIDAD.get(reporte.prioridad, reporte.prioridad)

    # 1. Texto descriptivo en formato oficial para WhatsApp personal
    mensaje_texto = (
        f"🚨 *ALERTA OPERATIVA DIRECTA — PROTECCIÓN CIVIL* 🚨\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🛡️ *Asignación:* {nombre_guardia}\n\n"
        f"📋 *Folio:* {reporte.numero_reporte}\n"
        f"⚠️ *Tipo:* {tipo_display}\n"
        f"🔶 *Prioridad:* {prioridad_display}\n"
        f"👤 *Encargado:* ⚠️ *SIN PERSONAL A CARGO (PENDIENTE)*\n\n"
        f"📍 *Ubicación:* {reporte.direccion}, Col. {reporte.colonia}, {reporte.localidad}\n"
        f"📝 *Descripción:* {reporte.descripcion}\n"
        f"👤 *Reportó:* {reporte.nombre_ciudadano} ({reporte.telefono_ciudadano})\n"
        f"🕐 *Fecha:* {reporte.fecha_reporte.strftime('%d/%b/%Y %H:%M')}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 *Responde a este mensaje o selecciona la opción del siguiente mensaje para tomar el reporte.*"
    )

    # 2. Opciones de respuesta interactiva (WhatsApp Native Poll)
    titulo_opciones = (
        f"🚨 *DISPONIBILIDAD DE ATENCIÓN ({reporte.numero_reporte})*\n\n"
        f"📍 {reporte.direccion}\n"
        f"⚠️ {tipo_display}\n\n"
        f"¿Aceptas ponerte a cargo y atender esta emergencia?"
    )
    opciones = [
        f"✋ Aceptar Atender ({reporte.numero_reporte})",
        f"❌ No Disponible / En Guardia"
    ]

    enviados_exitosos = 0
    trabajadores_procesados = set()

    for trabajador in trabajadores:
        if trabajador.telefono and trabajador.telefono not in trabajadores_procesados:
            trabajadores_procesados.add(trabajador.telefono)
            jids = normalizar_jids_whatsapp(trabajador.telefono)
            for target_jid in jids:
                # A) Enviar texto descriptivo personal
                enviar_mensaje_whatsapp(target_jid, mensaje_texto)
                
                # B) Enviar encuesta interactiva personal
                exito_opciones = enviar_encuesta_whatsapp(target_jid, titulo_opciones, opciones)
                
                if exito_opciones:
                    enviados_exitosos += 1
                    logger.info(f"Alerta interactiva individual enviada a {trabajador.nombre} ({target_jid})")
                else:
                    logger.warning(f"Error al enviar alerta individual a {trabajador.nombre} ({target_jid})")

    return enviados_exitosos


def enviar_alerta_grupo(reporte):
    """
    Envía la alerta de un nuevo reporte:
    1. Al grupo principal de WhatsApp (GRUPO_ALERTAS_JID): 
       - A) El mensaje de texto descriptivo oficial de la alerta.
       - B) La encuesta interactiva con botón clicable ('Aceptar Atender') directamente en el grupo.
    2. A los trabajadores del turno activo de forma individual.
    """
    try:
        # 1. Enviar el mensaje de texto al grupo principal
        mensaje_grupo = formatear_alerta_nueva(reporte)
        resultado_grupo = enviar_mensaje_whatsapp(GRUPO_ALERTAS_JID, mensaje_grupo)

        if resultado_grupo:
            logger.info(f"Alerta de texto enviada al grupo para reporte {reporte.numero_reporte}")
        else:
            logger.warning(f"No se pudo enviar alerta de texto al grupo para reporte {reporte.numero_reporte}")

        # 2. Enviar la encuesta interactiva clicable DIRECTAMENTE AL GRUPO para disponibilidad inmediata
        tipo_display = EMOJI_TIPO_SERVICIO.get(reporte.tipo_servicio, reporte.tipo_servicio)
        titulo_encuesta_grupo = f"🚨 DISPONIBILIDAD DE ATENCIÓN ({reporte.numero_reporte})\n\n📍 {reporte.direccion}, Col. {reporte.colonia}\n⚠️ {tipo_display}"
        opciones_grupo = [
            f"✋ Aceptar Atender ({reporte.numero_reporte})",
            f"❌ No Disponible / En Guardia"
        ]
        enviar_encuesta_whatsapp(GRUPO_ALERTAS_JID, titulo_encuesta_grupo, opciones_grupo)

        # 3. Notificar a los trabajadores individuales del turno activo
        notificados = notificar_trabajadores_turno_activo(reporte)
        logger.info(f"Reporte {reporte.numero_reporte} notificado individualmente a {notificados} trabajadores del turno activo.")

        return resultado_grupo
    except Exception as e:
        logger.error(f"Error inesperado al enviar alerta WhatsApp para {reporte.numero_reporte}: {e}")
        return False


def enviar_actualizacion_grupo(reporte, cambios_texto=""):
    """
    Envía una notificación de actualización de reporte al grupo de WhatsApp.
    No lanza excepciones si falla (fire-and-forget).
    """
    try:
        mensaje = formatear_actualizacion(reporte, cambios_texto)
        resultado = enviar_mensaje_whatsapp(GRUPO_ALERTAS_JID, mensaje)
        if resultado:
            logger.info(f"Actualización de WhatsApp enviada para reporte {reporte.numero_reporte}")
        return resultado
    except Exception as e:
        logger.error(f"Error inesperado al enviar actualización WhatsApp para {reporte.numero_reporte}: {e}")
        return False


