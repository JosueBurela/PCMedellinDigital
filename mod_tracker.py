import re, codecs

file_path = 'c:/Users/burel/OneDrive/Documentos/PCivil Digital/portal/utils/whatsapp_salidas_tracker.py'
with codecs.open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_idx = content.find('def procesar_mensaje_grupo_salidas(data):')

new_function = '''def procesar_mensaje_grupo_salidas(data):
    """
    Procesador maestro para los mensajes del grupo. Extrae unidades, fotos del tablero (odómetro/gasolina), horarios y actualiza la bitácora.
    """
    key = data.get("key", {})
    remote_jid = key.get("remoteJid", "") or data.get("remoteJid", "")
    participant_jid = key.get("participant", "") or data.get("participant", "")
    
    # REGLA DE ORO: Filtrar EXCLUSIVAMENTE el grupo de Protección Civil Medellín
    if remote_jid != GRUPO_SALIDAS_JID:
        return {"status": "ignored_different_group"}

    push_name = data.get("pushName", "") or "Personal Operativo"
    
    # Si no hay participant_jid (ej. en pruebas locales de Evolution API), usar el push_name como identificador
    if not participant_jid:
        participant_jid = push_name

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

    logger.info(f"[WHATSAPP PC] Mensaje recibido de {push_name} ({participant_jid}): '{texto_limpio}' (Tiene foto: {bool(image_msg)})")

    # 1. Identificar la unidad en el texto si la menciona
    num_unidad = extraer_unidad(texto_limpio)
    vehiculo = None
    if num_unidad:
        vehiculo = buscar_vehiculo(num_unidad)

    # 2. Buscar si ESTE OPERADOR ya tiene una salida activa (para inferencias y cierres automáticos)
    salida_activa_usuario = BitacoraSalidaVehiculo.objects.filter(
        operador_telefono=participant_jid,
        completado=False,
        fecha_salida__gte=dt_evento - datetime.timedelta(hours=14)
    ).order_by('-fecha_salida').first()

    # Clasificar el tipo de evento: SALIDA vs ENTRADA vs NOVEDAD
    tipo_evento, detalle_evento = clasificar_mensaje_operativo(texto_limpio)

    # Si no mencionó la unidad explícitamente, intentar inferirla basándonos en su estado
    if not vehiculo:
        if salida_activa_usuario:
            # Si el usuario tiene una salida, asumimos que todos sus mensajes siguientes son para ESA unidad
            vehiculo = salida_activa_usuario.unidad
            logger.info(f"[WHATSAPP PC] Unidad {vehiculo.numero_unidad} inferida por salida activa del operador {push_name}")
        elif tipo_evento == 'ENTRADA':
            # Buscar la salida activa más reciente de CUALQUIERA si dice 'llegando a base' y no tiene nada asignado
            salida_pendiente = BitacoraSalidaVehiculo.objects.filter(
                completado=False,
                fecha_salida__gte=dt_evento - datetime.timedelta(hours=14)
            ).order_by('-fecha_salida').first()
            if salida_pendiente:
                vehiculo = salida_pendiente.unidad
                logger.info(f"[WHATSAPP PC] Unidad {vehiculo.numero_unidad} inferida por salida pendiente global")

    if not vehiculo:
        logger.info(f"[WHATSAPP PC] No se detectó ni se pudo inferir unidad vehicular: '{texto_limpio}'")
        return {"status": "no_unit_detected", "text": texto_limpio}

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
        # Si el usuario ya tenía una salida activa
        if salida_activa_usuario:
            minutos_dif = (dt_evento - salida_activa_usuario.fecha_salida).total_seconds() / 60
            if salida_activa_usuario.unidad == vehiculo and minutos_dif < 60:
                # Es la misma unidad y pasó poco tiempo (doble mensaje de salida), anexamos
                if foto_archivo and not salida_activa_usuario.foto_odometro_salida:
                    salida_activa_usuario.foto_odometro_salida = foto_archivo
                salida_activa_usuario.descripcion_servicio += f" | {detalle_evento}"
                salida_activa_usuario.save()
                return {"status": "salida_updated", "unidad": vehiculo.numero_unidad}
            else:
                # El usuario sacó OTRA unidad, o pasó mucho tiempo con la misma. Auto-cerramos la anterior.
                salida_activa_usuario.completado = True
                salida_activa_usuario.fecha_llegada = dt_evento
                salida_activa_usuario.descripcion_servicio += " | [Cierre automático por nueva salida del operador]"
                salida_activa_usuario.save()
                
                # Actualizar estatus del vehículo que se auto-cerró
                u_cerrada = salida_activa_usuario.unidad
                u_cerrada.estatus = 'DISPONIBLE'
                u_cerrada.ultima_salida_finalizada = dt_evento
                u_cerrada.save()
                
                logger.info(f"[WHATSAPP PC] Cierre automático de {u_cerrada.numero_unidad} porque {push_name} sacó una nueva unidad.")

        # Verificar si ESTA unidad ya estaba fuera por ALGUIEN MÁS
        salida_existente = BitacoraSalidaVehiculo.objects.filter(
            unidad=vehiculo,
            completado=False,
            fecha_salida__gte=dt_evento - datetime.timedelta(hours=14)
        ).first()

        if salida_existente:
            if foto_archivo and not salida_existente.foto_odometro_salida:
                salida_existente.foto_odometro_salida = foto_archivo
            salida_existente.descripcion_servicio += f" | [Asume {push_name}] {detalle_evento}"
            salida_existente.operador_nombre = push_name
            salida_existente.operador_telefono = participant_jid  # Toma el control el nuevo número
            salida_existente.save()
            return {"status": "salida_updated_taken_over", "unidad": vehiculo.numero_unidad}

        # Crear nuevo registro de salida
        nueva_salida = BitacoraSalidaVehiculo.objects.create(
            unidad=vehiculo,
            operador_nombre=push_name,
            operador_telefono=participant_jid,
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

        logger.info(f"[WHATSAPP PC] ?? SALIDA REGISTRADA con éxito: {vehiculo.nombre_identificador} | Operador: {push_name} | Motivo: {detalle_evento}")
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
        # Buscar la salida abierta más reciente de esta unidad (la inferida o la explícita)
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

            logger.info(f"[WHATSAPP PC] ?? RETORNO A BASE REGISTRADO: {vehiculo.nombre_identificador} | Duración: {duracion} min")
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
                operador_telefono=participant_jid,
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
            salida_activa.descripcion_servicio += f" \\n[{dt_evento.strftime('%H:%M')}]: {detalle_evento}"
            if foto_archivo and not salida_activa.foto_odometro_salida:
                salida_activa.foto_odometro_salida = foto_archivo
            salida_activa.save()
            logger.info(f"[WHATSAPP PC] Novedad añadida a salida #{salida_activa.id}: {detalle_evento}")
            return {"status": "novedad_anexada", "salida_id": salida_activa.id}

        return {"status": "mensaje_ignorado"}
'''

new_content = content[:start_idx] + new_function
with codecs.open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print('File written successfully')
