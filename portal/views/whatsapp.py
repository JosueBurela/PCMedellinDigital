# ==============================================================================
#  🛡️ SISTEMA DIGITAL DE PROTECCIÓN CIVIL Y BOMBEROS
#  Copyright (c) 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
#  Desarrollado y Diseñado por: Josué Jaziel Delgado Burela
#  Contacto y Soporte: jburela1@gmal.com
# ==============================================================================

import json
import re
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from portal.models import ReporteRiesgo, HistorialReporte, Trabajador, SesionAtencionWhatsApp
from portal.utils.whatsapp_utils import enviar_mensaje_whatsapp, GRUPO_ALERTAS_JID

logger = logging.getLogger(__name__)

@csrf_exempt
def whatsapp_webhook(request):
    """
    Webhook para recibir eventos y mensajes entrantes de WhatsApp desde Evolution API:
    1. Aceptación / Rechazo de emergencia por Encuestas (Poll) / Botones / Texto.
    2. Flujo conversacional interactivo privado (Unidad + Tiempo Estimado) para el primer respondedor.
    3. Registro de bitácoras por comando ("Bitacora REP-XXXX: comentario") o auto-bitácora.
    """
    if request.method != 'POST':
        return JsonResponse({"status": "method_not_allowed"}, status=405)
        
    try:
        payload = json.loads(request.body)
        data = payload.get("data", {})
        if not isinstance(data, dict):
            data = payload
            
        key = data.get("key", {}) if isinstance(data.get("key"), dict) else {}
        if key.get("fromMe", False):
            return JsonResponse({"status": "ignored_from_me"})
            
        raw_remote_jid = key.get("remoteJid", "") or data.get("remoteJid", "") or data.get("from", "")
        raw_participant = key.get("participant", "") or data.get("participant", "") or data.get("voter", "") or raw_remote_jid
        push_name = data.get("pushName", "") or data.get("voterName", "Personal Operativo")

        # ── Determinación de JIDs (Grupo vs Chat Privado del Trabajador) ───────
        chat_jid = raw_remote_jid
        
        # Extraer dígitos telefónicos para resolver el JID individual del trabajador (@s.whatsapp.net)
        participant_digits = re.sub(r'\D', '', raw_participant or raw_remote_jid)
        if len(participant_digits) >= 10:
            target_jid = f"{participant_digits}@s.whatsapp.net"
        else:
            target_jid = raw_remote_jid

        # ── 1. Extraer texto o respuesta de encuestas / botones ────────────────
        texto = ""
        message = data.get("message", {}) if isinstance(data.get("message"), dict) else {}
        
        def _obtener_nombre_opcion(opt):
            if isinstance(opt, str):
                return opt
            if isinstance(opt, dict):
                return opt.get("optionName") or opt.get("name") or opt.get("text") or opt.get("value") or ""
            return ""

        if message:
            if "conversation" in message:
                texto = message["conversation"]
            elif "extendedTextMessage" in message:
                texto = message["extendedTextMessage"].get("text", "")
            elif "pollUpdateMessage" in message:
                poll_msg = message.get("pollUpdateMessage", {})
                vote = poll_msg.get("vote", {}) or poll_msg.get("pollCreationMessageKey", {}) or poll_msg
                opts = vote.get("selectedOptions", []) or vote.get("options", []) or vote.get("selectedOption", [])
                if opts:
                    texto = _obtener_nombre_opcion(opts[0] if isinstance(opts, list) else opts)
            elif "buttonsResponseMessage" in message:
                btn_msg = message.get("buttonsResponseMessage", {})
                texto = btn_msg.get("selectedDisplayText", "") or btn_msg.get("selectedButtonId", "")

        if not texto:
            for field in ["selectedOptions", "options", "pollUpdateMessage", "selectedOption", "selectedAnswer"]:
                val = data.get(field) or (message.get(field) if isinstance(message, dict) else None)
                if val:
                    if isinstance(val, list) and len(val) > 0:
                        texto = _obtener_nombre_opcion(val[0])
                    elif isinstance(val, (dict, str)):
                        texto = _obtener_nombre_opcion(val)
                    if texto:
                        break

        if not texto and isinstance(data.get("body"), str):
            texto = data.get("body", "")

        texto_clean = texto.strip()
        logger.info(f"Webhook WhatsApp de {target_jid} (Chat: {chat_jid}, Nombre: {push_name}): '{texto_clean}'")

        if not texto_clean:
            return JsonResponse({"status": "no_text"})

        # Identificar al trabajador por número telefónico
        trabajador = None
        if len(participant_digits) >= 10:
            telefono_10 = participant_digits[-10:]
            trabajador = Trabajador.objects.filter(telefono__icontains=telefono_10).first()

        nombre_respondedor = trabajador.nombre if trabajador else push_name

        # ── 2. Revisar si el remitente tiene una sesión conversacional activa ───
        sesion = SesionAtencionWhatsApp.objects.filter(
            Q(phone_number=target_jid) | Q(phone_number=chat_jid) | 
            Q(phone_number__icontains=participant_digits[-10:] if len(participant_digits) >= 10 else 'NOMATCH')
        ).select_related('reporte').first()

        if sesion:
            reporte = sesion.reporte

            if sesion.paso == 1:
                # Paso 1: Recibir Unidad / Vehículo
                sesion.unidad_acudira = texto_clean
                sesion.paso = 2
                sesion.save()

                pregunta2 = (
                    f"👍 *Unidad registrada:* {texto_clean}\n\n"
                    f"2️⃣ *¿Cuál es tu Tiempo Estimado de Arribo / Atención al punto?*\n"
                    f"_(Escribe el tiempo estimado, ej: 10 minutos, 15 min, etc.)_"
                )
                enviar_mensaje_whatsapp(target_jid, pregunta2)
                return JsonResponse({"status": "unit_saved_asked_time"})

            elif sesion.paso == 2:
                # Paso 2: Recibir Tiempo Estimado -> COMPLETAR DESPACHO
                tiempo_est = texto_clean
                unidad_def = sesion.unidad_acudira or "Unidad de Respuesta"

                # Actualizar reporte oficialmente en la Base de Datos
                reporte.estatus = 'EN_PROCESO'
                reporte.unidad_acudira = unidad_def
                reporte.tiempo_atencion = tiempo_est
                reporte.save()

                # Añadir al historial oficial / bitácora
                HistorialReporte.objects.create(
                    reporte=reporte,
                    comentario=f"✅ [Despacho WhatsApp]: Tomado a cargo por {nombre_respondedor} en unidad {unidad_def} (Tiempo estimado de arribo: {tiempo_est})."
                )

                # Eliminar sesión conversacional
                SesionAtencionWhatsApp.objects.filter(
                    Q(phone_number=target_jid) | Q(phone_number=chat_jid)
                ).delete()

                # A) Confirmación privada al trabajador
                confirmacion_privada = (
                    f"🚀 *¡DESPACHO COMPLETADO Y REGISTRADO!* 🚀\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📋 *Folio:* {reporte.numero_reporte}\n"
                    f"👷 *Encargado:* {nombre_respondedor}\n"
                    f"🚑 *Unidad:* {unidad_def}\n"
                    f"⏱️ *Tiempo Estimado:* {tiempo_est}\n\n"
                    f"📌 *Estatus Actualizado:* 🚑 EN CAMINO\n\n"
                    f"¡Procede con precaución! Puedes enviar avances a la bitácora escribiendo:\n"
                    f"_Bitacora {reporte.numero_reporte}: Arribando al punto_"
                )
                enviar_mensaje_whatsapp(target_jid, confirmacion_privada)

                # B) Notificación oficial al Grupo de Alertas de Medellín
                aviso_grupo = (
                    f"📢 *ALERTA EN CAMINO — UNIDAD Y PERSONAL ASIGNADO* 📢\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📋 *Folio:* {reporte.numero_reporte}\n"
                    f"⚠️ *Tipo:* {reporte.get_tipo_servicio_display()}\n"
                    f"📍 *Ubicación:* {reporte.direccion}, Col. {reporte.colonia}\n\n"
                    f"👷 *Encargado a Cargo:* *{nombre_respondedor}*\n"
                    f"🚑 *Unidad Despachada:* *{unidad_def}*\n"
                    f"⏱️ *Tiempo Estimado de Arribo:* *{tiempo_est}*\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔄 *Estatus:* 🚑 EN CAMINO"
                )
                enviar_mensaje_whatsapp(GRUPO_ALERTAS_JID, aviso_grupo)

                logger.info(f"Despacho completado para {reporte.numero_reporte}: {nombre_respondedor} en {unidad_def}")
                return JsonResponse({"status": "dispatch_completed"})

        # ── 3. PROCESAR RESPUESTA DE "NO DISPONIBLE" ─────────────────────────────
        es_no_disponible = any(k in texto_clean.lower() for k in [
            'no disponible', 'no puedo', 'ocupado', 'en otra emergencia', 'fuera de servicio', 'rechazar', '❌'
        ])

        if es_no_disponible:
            match_folio_nodisp = re.search(r'(?i)(REP-\d{4})', texto_clean)
            reporte_nodisp = None
            if match_folio_nodisp:
                reporte_nodisp = ReporteRiesgo.objects.filter(numero_reporte=match_folio_nodisp.group(1).upper()).first()
            if not reporte_nodisp:
                reporte_nodisp = ReporteRiesgo.objects.filter(estatus='PENDIENTE').order_by('-id').first()

            respuesta_agradecimiento = (
                f"👍 *Estatus Registrado*\n\n"
                f"Muchas gracias por contestar, *{nombre_respondedor}*.\n"
                f"Entendido que no estás disponible en este momento. La atención de la alerta queda pendiente para los demás integrantes de la guardia."
            )
            enviar_mensaje_whatsapp(target_jid, respuesta_agradecimiento)

            if reporte_nodisp:
                HistorialReporte.objects.create(
                    reporte=reporte_nodisp,
                    comentario=f"ℹ️ [WhatsApp]: {nombre_respondedor} notificó no estar disponible para este llamado."
                )

            logger.info(f"Respuesta No Disponible registrada para {nombre_respondedor}")
            return JsonResponse({"status": "not_available_acknowledged"})

        # ── 4. PROCESAR ACEPTACIÓN INICIAL ("Aceptar Atender (REP-XXXX)") ────────
        es_aceptar = any(k in texto_clean.lower() for k in [
            'aceptar', 'atender', 'acepto', 'si', 'sí', 'voy', 'disponible', '✋'
        ])

        folio_encontrado = None
        match_aceptar = re.search(r'(?i)(?:aceptar|atender|acepto).*?(REP-\d{4})|(REP-\d{4}).*?(?:aceptar|atender|acepto)', texto_clean)
        
        if match_aceptar:
            folio_encontrado = (match_aceptar.group(1) or match_aceptar.group(2)).upper()
        else:
            match_folio = re.search(r'(?i)(REP-\d{4})', texto_clean)
            if match_folio:
                folio_encontrado = match_folio.group(1).upper()
            elif es_aceptar:
                reporte_pend = ReporteRiesgo.objects.filter(estatus='PENDIENTE').order_by('-id').first()
                if reporte_pend:
                    folio_encontrado = reporte_pend.numero_reporte

        if folio_encontrado:
            reporte = ReporteRiesgo.objects.filter(numero_reporte=folio_encontrado).first()

            if not reporte:
                enviar_mensaje_whatsapp(target_jid, f"❌ No se encontró ningún reporte activo con el folio *{folio_encontrado}*.")
                return JsonResponse({"status": "report_not_found"})

            # VERIFICAR SI EL REPORTE YA FUE ASIGNADO PREVIAMENTE
            if reporte.estatus != 'PENDIENTE' and reporte.unidad_acudira:
                ya_asignado = (
                    f"ℹ️ *Aviso de Disponibilidad*\n\n"
                    f"El reporte *{reporte.numero_reporte}* ya fue tomado a cargo previamente por *{reporte.unidad_acudira}*.\n\n"
                    f"¡Muchas gracias por tu rápida respuesta!"
                )
                enviar_mensaje_whatsapp(target_jid, ya_asignado)
                return JsonResponse({"status": "already_assigned"})

            # ¡PRIMERO EN RESPONDER! INICIAR SESIÓN CONVERSACIONAL EN EL CHAT PRIVADO DEL TRABAJADOR
            SesionAtencionWhatsApp.objects.filter(
                Q(phone_number=target_jid) | Q(phone_number=chat_jid)
            ).delete()

            SesionAtencionWhatsApp.objects.create(
                phone_number=target_jid,
                reporte=reporte,
                paso=1
            )
            if chat_jid != target_jid:
                SesionAtencionWhatsApp.objects.create(
                    phone_number=chat_jid,
                    reporte=reporte,
                    paso=1
                )

            # Enviar pregunta 1 al chat PRIVADO del trabajador
            pregunta1 = (
                f"✅ *¡HAS SIDO SELECCIONADO PARA ATENDER EL REPORTE {reporte.numero_reporte}!*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Hola *{nombre_respondedor}*, para completar el despacho y notificar al grupo de alertas, responde las siguientes 2 preguntas:\n\n"
                f"1️⃣ *¿En qué unidad o vehículo acudirás a la emergencia?*\n"
                f"_(Escribe el nombre o número de unidad, ej: Ambulancia 02, PC-01, Pick-up Rescate, etc.)_"
            )
            enviar_mensaje_whatsapp(target_jid, pregunta1)
            logger.info(f"Trabajador {nombre_respondedor} ({target_jid}) aceptó {folio_encontrado}. Pregunta 1 enviada a su chat privado.")
            return JsonResponse({"status": "selected_asked_unit"})

        # ── 5. Procesar FINALIZACIÓN DE ALERTA ("ALERTA FINALIZADA CON EXITO") ──
        if re.search(r'(?i)alerta\s+finalizada|finalizada\s+con\s+exito|finalizada\s+con\s+éxito|finalizar\s+alerta|finalizar\s+reporte', texto_clean):
            reporte_activo = ReporteRiesgo.objects.exclude(estatus='RESUELTO').order_by('-id').first()

            if reporte_activo:
                from django.utils import timezone
                reporte_activo.estatus = 'RESUELTO'
                reporte_activo.fecha_resolucion = timezone.now()
                if not reporte_activo.unidad_acudira:
                    reporte_activo.unidad_acudira = f"{nombre_respondedor}"
                reporte_activo.save()

                SesionAtencionWhatsApp.objects.filter(
                    Q(phone_number=target_jid) | Q(phone_number=chat_jid)
                ).delete()

                HistorialReporte.objects.create(
                    reporte=reporte_activo,
                    comentario=f"🎉 [WhatsApp]: Emergencia marcada como FINALIZADA CON ÉXITO por {nombre_respondedor}."
                )

                tiempo_res = reporte_activo.tiempo_resolucion_calculado or "Completado"

                # A) Confirmación privada al trabajador
                confirmacion = (
                    f"🎉 *¡ALERTA FINALIZADA CON ÉXITO!* 🎉\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📋 *Folio:* {reporte_activo.numero_reporte}\n"
                    f"👷 *Atendido por:* {nombre_respondedor}\n"
                    f"⏱️ *Tiempo de Atención:* {tiempo_res}\n\n"
                    f"📌 *Estatus:* ✅ RESUELTO Y CERRADO\n"
                    f"¡Excelente trabajo operativa!"
                )
                enviar_mensaje_whatsapp(target_jid, confirmacion)

                # B) Notificación oficial al Grupo de Alertas de Medellín
                aviso_grupo = (
                    f"✅ *EMERGENCIA FINALIZADA Y CONCLUIDA* ✅\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📋 *Folio:* {reporte_activo.numero_reporte}\n"
                    f"⚠️ *Tipo:* {reporte_activo.get_tipo_servicio_display()}\n"
                    f"📍 *Ubicación:* {reporte_activo.direccion}, Col. {reporte_activo.colonia}\n\n"
                    f"👷 *Responsable a Cargo:* *{nombre_respondedor}*\n"
                    f"🚑 *Unidad:* *{reporte_activo.unidad_acudira}*\n"
                    f"⏱️ *Tiempo Total de Atención:* *{tiempo_res}*\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📌 *Estatus Final:* ✅ RESUELTO / CONCLUIDO"
                )
                enviar_mensaje_whatsapp(GRUPO_ALERTAS_JID, aviso_grupo)

                logger.info(f"Reporte {reporte_activo.numero_reporte} finalizado con éxito por {nombre_respondedor}")
                return JsonResponse({"status": "alert_finalized_success"})
            else:
                enviar_mensaje_whatsapp(target_jid, "ℹ️ No tienes ningún reporte activo en proceso asignado para finalizar.")
                return JsonResponse({"status": "no_active_report_to_finalize"})

        # ── 6. Procesar COMANDO DE BITÁCORA EXPLÍCITO ("Bitacora REP-XXXX: comentario") ──
        match_bitacora = re.match(r'(?i)^bitacora\s*([a-zA-Z0-9\-]+)\s*:\s*(.*)', texto_clean)
        if match_bitacora:
            reporte_num = match_bitacora.group(1).upper()
            comentario = match_bitacora.group(2).strip()
            
            reporte = ReporteRiesgo.objects.filter(
                Q(numero_reporte=reporte_num) |
                Q(numero_reporte=f"REP-{reporte_num}") |
                Q(id=int(reporte_num) if reporte_num.isdigit() else -1)
            ).first()
            
            if reporte:
                HistorialReporte.objects.create(
                    reporte=reporte,
                    comentario=f"[WhatsApp - {push_name}]: {comentario}"
                )
                
                confirmacion = (
                    f"✅ *Bitácora Registrada*\n\n"
                    f"Se añadió al historial del reporte *{reporte.numero_reporte}*:\n"
                    f"_\"{comentario}\"_"
                )
                enviar_mensaje_whatsapp(target_jid, confirmacion)
                return JsonResponse({"status": "bitacora_added"})

        # ── 7. AUTO-BITÁCORA: Cualquier otro mensaje durante una alerta activa ──
        reporte_en_curso = ReporteRiesgo.objects.filter(estatus='EN_PROCESO').order_by('-id').first()

        if reporte_en_curso:
            HistorialReporte.objects.create(
                reporte=reporte_en_curso,
                comentario=f"[WhatsApp - {nombre_respondedor}]: {texto_clean}"
            )
            confirmacion_auto = (
                f"📝 *Bitácora Actualizada ({reporte_en_curso.numero_reporte})*\n\n"
                f"Se añadió a la bitácora:\n"
                f"_\"{texto_clean}\"_"
            )
            enviar_mensaje_whatsapp(target_jid, confirmacion_auto)
            logger.info(f"Auto-bitácora registrada para {reporte_en_curso.numero_reporte}: '{texto_clean}'")
            return JsonResponse({"status": "auto_bitacora_saved"})

        return JsonResponse({"status": "ignored"})
        
    except Exception as e:
        logger.error(f"Error en whatsapp_webhook: {e}")
        return JsonResponse({"status": "error", "message": str(e)}, status=400)
