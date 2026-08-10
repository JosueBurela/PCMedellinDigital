# ==============================================================================
#  🛡️ SISTEMA DIGITAL DE PROTECCIÓN CIVIL Y BOMBEROS
#  Copyright (c) 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
#  Desarrollado y Diseñado por: Josué Jaziel Delgado Burela
#  Contacto y Soporte: jburela1@gmal.com
# ==============================================================================

import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from portal.models import Tramite, Ciudadano, SolicitudTramite, ReporteRiesgo, ActividadGiro
from portal.utils import parsear_curp
from portal.utils.clima_utils import obtener_pronostico_veracruz

from django.db import models

def home(request):
    # Cargar datos del ciudadano si tiene sesión activa
    ciudadano = None
    ciudadano_id = request.session.get('ciudadano_id')
    curp_sesion = request.session.get('ciudadano_curp')
    if ciudadano_id:
        ciudadano = Ciudadano.objects.filter(id=ciudadano_id).first()
    elif curp_sesion:
        ciudadano = Ciudadano.objects.filter(models.Q(curp=curp_sesion) | models.Q(correo=curp_sesion)).first()
        
    return render(request, 'portal/index.html', {
        'ciudadano': ciudadano,
    })

def iniciar_tramite(request, tramite_id):
    tramite = get_object_or_404(Tramite, id=tramite_id, activo=True)
    
    # Pre-llenar nombre del ciudadano si está logueado
    nombre_prellenado = ""
    correo_prellenado = ""
    tel_prellenado = ""
    ciudadano = None
    ciudadano_id = request.session.get('ciudadano_id')
    curp_sesion = request.session.get('ciudadano_curp')
    if ciudadano_id:
        ciudadano = Ciudadano.objects.filter(id=ciudadano_id).first()
    elif curp_sesion:
        ciudadano = Ciudadano.objects.filter(models.Q(curp=curp_sesion) | models.Q(correo=curp_sesion)).first()
        
    # Requisito Obligatorio: El usuario debe estar logueado para iniciar un trámite
    if not ciudadano and not request.user.is_authenticated:
        messages.warning(request, "🔒 Para iniciar la solicitud de un trámite digital es necesario registrarse e iniciar sesión en el portal.")
        return redirect('login_unificado')

    if ciudadano:
        nombre_prellenado = f"{ciudadano.nombre} {ciudadano.primer_apellido} {ciudadano.segundo_apellido or ''}".strip()
        correo_prellenado = ciudadano.correo
        tel_prellenado = ciudadano.telefono
            
    if request.method == 'POST':
        establecimiento = request.POST.get('establecimiento')
        rfc = request.POST.get('rfc')
        pdf = request.FILES.get('pdf_documento')
        
        # Validación de campos según form_type (Modular para los próximos formatos)
        if tramite.form_type == 'ANUENCIA_PC':
            tipo_anuencia = tramite.sub_tipo if tramite.sub_tipo else request.POST.get('tipo_anuencia')
            propietario = request.POST.get('propietario_representante')
            ui_nombre = request.POST.get('unidad_interna_nombre')
            ui_tel = request.POST.get('unidad_interna_tel')
            capacidad = request.POST.get('capacidad_fija')
            giro = request.POST.get('giro')
            calle = request.POST.get('domicilio_calle')
            no_ext = request.POST.get('no_ext')
            no_int = request.POST.get('no_int')
            entre = request.POST.get('entre_calles')
            colonia = request.POST.get('colonia')
            tel_contacto = request.POST.get('telefono_contacto')
            horario = request.POST.get('horario_funcionamiento')
            superficie = request.POST.get('superficie_m2')
            correo_c = request.POST.get('correo_contacto')
            
            # Archivos Físicos de Requisitos
            f_ine = request.FILES.get('file_ine')
            f_croquis = request.FILES.get('file_croquis')
            f_fotos = request.FILES.get('file_fotos')
            f_predial = request.FILES.get('file_predial')
            
            f_programa = request.FILES.get('file_programa')
            f_corresp = request.FILES.get('file_corresponsabilidad')
            f_capacitacion = request.FILES.get('file_capacitacion')
            f_gas = request.FILES.get('file_gas')
            f_electrico = request.FILES.get('file_electrico')
            f_estructural = request.FILES.get('file_estructural')
            f_seguro = request.FILES.get('file_seguro')
            f_pago = request.FILES.get('file_pago')

            # Booleans basados en existencia de archivo
            d_ine = f_ine is not None
            d_croquis = f_croquis is not None
            d_fotos = f_fotos is not None
            d_predial = f_predial is not None
            
            r_programa = f_programa is not None
            r_corresp = f_corresp is not None
            r_capacitacion = f_capacitacion is not None
            r_gas = f_gas is not None
            r_electrico = f_electrico is not None
            r_estructural = f_estructural is not None
            r_seguro = f_seguro is not None
            r_pago = f_pago is not None
            
            if establecimiento and rfc and propietario and giro:
                SolicitudTramite.objects.create(
                    tramite=tramite,
                    ciudadano=ciudadano,
                    establecimiento=establecimiento,
                    rfc=rfc.upper(),
                    pdf_documento=pdf,
                    tipo_anuencia=tipo_anuencia,
                    propietario_representante=propietario,
                    unidad_interna_nombre=ui_nombre,
                    unidad_interna_tel=ui_tel,
                    capacidad_fija=capacidad,
                    giro=giro,
                    domicilio_calle=calle,
                    no_ext=no_ext,
                    no_int=no_int,
                    entre_calles=entre,
                    colonia=colonia,
                    telefono_contacto=tel_contacto,
                    horario_funcionamiento=horario,
                    superficie_m2=superficie,
                    correo_contacto=correo_c,
                    doc_ine=d_ine,
                    doc_croquis=d_croquis,
                    doc_fotos=d_fotos,
                    doc_predial=d_predial,
                    req_programa=r_programa,
                    req_corresponsabilidad=r_corresp,
                    req_capacitacion=r_capacitacion,
                    req_gas=r_gas,
                    req_electrico=r_electrico,
                    req_estructural=r_estructural,
                    req_seguro=r_seguro,
                    req_pago=r_pago,
                    file_ine=f_ine,
                    file_croquis=f_croquis,
                    file_fotos=f_fotos,
                    file_predial=f_predial,
                    file_programa=f_programa,
                    file_corresponsabilidad=f_corresp,
                    file_capacitacion=f_capacitacion,
                    file_gas=f_gas,
                    file_electrico=f_electrico,
                    file_estructural=f_estructural,
                    file_seguro=f_seguro,
                    file_pago=f_pago
                )
                messages.success(request, f"¡Solicitud de Anuencia para '{establecimiento}' enviada con éxito!")
                return redirect('home')
            else:
                messages.error(request, "Por favor completa todos los campos obligatorios.")

        elif tramite.form_type == 'ANUNCIOS_PC':
            tipo_anuencia_anuncio = tramite.sub_tipo if tramite.sub_tipo else request.POST.get('tipo_anuencia_anuncio')
            inspeccion_atiende = request.POST.get('inspeccion_atiende')
            propietario = request.POST.get('propietario_representante')
            giro = request.POST.get('giro')
            calle = request.POST.get('domicilio_calle')
            no_ext = request.POST.get('no_ext')
            no_int = request.POST.get('no_int')
            entre = request.POST.get('entre_calles')
            colonia = request.POST.get('colonia')
            tel_contacto = request.POST.get('telefono_contacto')
            correo_c = request.POST.get('correo_contacto')

            # Archivos Físicos de Requisitos
            f_ine = request.FILES.get('file_ine')
            f_croquis = request.FILES.get('file_croquis')
            f_fotos = request.FILES.get('file_fotos')
            f_predial = request.FILES.get('file_predial')

            f_responsiva_estabilidad = request.FILES.get('file_responsiva_estabilidad')
            f_bitacora_anuncio = request.FILES.get('file_bitacora_anuncio')
            f_seguro = request.FILES.get('file_seguro')
            f_anuencia_vecinos = request.FILES.get('file_anuencia_vecinos')
            f_analisis_riesgo = request.FILES.get('file_analisis_riesgo')
            f_pago = request.FILES.get('file_pago')

            # Booleans basados en existencia
            d_ine = f_ine is not None
            d_croquis = f_croquis is not None
            d_fotos = f_fotos is not None
            d_predial = f_predial is not None

            r_responsiva = f_responsiva_estabilidad is not None
            r_bitacora = f_bitacora_anuncio is not None
            r_seguro = f_seguro is not None
            r_vecinos = f_anuencia_vecinos is not None
            r_analisis = f_analisis_riesgo is not None
            r_pago = f_pago is not None

            if establecimiento and rfc and propietario and giro:
                SolicitudTramite.objects.create(
                    tramite=tramite,
                    ciudadano=ciudadano,
                    establecimiento=establecimiento,
                    rfc=rfc.upper(),
                    pdf_documento=pdf,
                    tipo_anuencia_anuncio=tipo_anuencia_anuncio,
                    inspeccion_atiende=inspeccion_atiende,
                    propietario_representante=propietario,
                    giro=giro,
                    domicilio_calle=calle,
                    no_ext=no_ext,
                    no_int=no_int,
                    entre_calles=entre,
                    colonia=colonia,
                    telefono_contacto=tel_contacto,
                    correo_contacto=correo_c,
                    doc_ine=d_ine,
                    doc_croquis=d_croquis,
                    doc_fotos=d_fotos,
                    doc_predial=d_predial,
                    req_responsiva_estabilidad=r_responsiva,
                    req_bitacora_anuncio=r_bitacora,
                    req_seguro=r_seguro,
                    req_anuencia_vecinos=r_vecinos,
                    req_analisis_riesgo=r_analisis,
                    req_pago=r_pago,
                    file_ine=f_ine,
                    file_croquis=f_croquis,
                    file_fotos=f_fotos,
                    file_predial=f_predial,
                    file_responsiva_estabilidad=f_responsiva_estabilidad,
                    file_bitacora_anuncio=f_bitacora_anuncio,
                    file_seguro=f_seguro,
                    file_anuencia_vecinos=f_anuencia_vecinos,
                    file_analisis_riesgo=f_analisis_riesgo,
                    file_pago=f_pago
                )
                messages.success(request, f"¡Solicitud de Anuencia de Anuncios/Antenas para '{establecimiento}' enviada!")
                return redirect('home')
            else:
                messages.error(request, "Por favor completa todos los campos obligatorios.")
                
        elif tramite.form_type == 'CONSTRUCCION_PC':
            tipo_anuencia_construccion = tramite.sub_tipo if tramite.sub_tipo else request.POST.get('tipo_anuencia_construccion')
            propietario = request.POST.get('propietario_representante')
            giro = request.POST.get('giro')
            calle = request.POST.get('domicilio_calle')
            no_ext = request.POST.get('no_ext')
            no_int = request.POST.get('no_int')
            entre = request.POST.get('entre_calles')
            colonia = request.POST.get('colonia')
            tel_contacto = request.POST.get('telefono_contacto')
            correo_c = request.POST.get('correo_contacto')
            
            superficie_terreno = request.POST.get('superficie_terreno')
            superficie_construccion = request.POST.get('superficie_construccion')
            realiza_nombre = request.POST.get('realiza_nombre')
            realiza_telefono = request.POST.get('realiza_telefono')
            realiza_correo = request.POST.get('realiza_correo')

            # Archivos Físicos de Requisitos
            f_ine = request.FILES.get('file_ine')
            f_croquis = request.FILES.get('file_croquis')
            f_fotos = request.FILES.get('file_fotos')
            f_predial = request.FILES.get('file_predial')

            f_titulo_propiedad = request.FILES.get('file_titulo_propiedad')
            f_plano_arquitectonico = request.FILES.get('file_plano_arquitectonico')
            f_constancia_no_afectacion = request.FILES.get('file_constancia_no_afectacion')
            f_uso_suelo = request.FILES.get('file_uso_suelo')
            f_analisis_riesgo = request.FILES.get('file_analisis_riesgo')
            f_pago = request.FILES.get('file_pago')

            # Booleans basados en existencia
            d_ine = f_ine is not None
            d_croquis = f_croquis is not None
            d_fotos = f_fotos is not None
            d_predial = f_predial is not None

            d_titulo_propiedad = f_titulo_propiedad is not None
            r_plano = f_plano_arquitectonico is not None
            r_no_afectacion = f_constancia_no_afectacion is not None
            r_uso_suelo = f_uso_suelo is not None
            r_analisis = f_analisis_riesgo is not None
            r_pago = f_pago is not None

            rfc_val = rfc.upper() if rfc else "XAXX010101000"

            if establecimiento and propietario and giro:
                SolicitudTramite.objects.create(
                    tramite=tramite,
                    ciudadano=ciudadano,
                    establecimiento=establecimiento,
                    rfc=rfc_val,
                    pdf_documento=pdf,
                    tipo_anuencia_construccion=tipo_anuencia_construccion,
                    propietario_representante=propietario,
                    giro=giro,
                    domicilio_calle=calle,
                    no_ext=no_ext,
                    no_int=no_int,
                    entre_calles=entre,
                    colonia=colonia,
                    telefono_contacto=tel_contacto,
                    correo_contacto=correo_c,
                    superficie_terreno=superficie_terreno,
                    superficie_construccion=superficie_construccion,
                    realiza_nombre=realiza_nombre,
                    realiza_telefono=realiza_telefono,
                    realiza_correo=realiza_correo,
                    doc_ine=d_ine,
                    doc_croquis=d_croquis,
                    doc_fotos=d_fotos,
                    doc_predial=d_predial,
                    doc_titulo_propiedad=d_titulo_propiedad,
                    req_plano_arquitectonico=r_plano,
                    req_constancia_no_afectacion=r_no_afectacion,
                    req_uso_suelo=r_uso_suelo,
                    req_analisis_riesgo=r_analisis,
                    req_pago=r_pago,
                    file_ine=f_ine,
                    file_croquis=f_croquis,
                    file_fotos=f_fotos,
                    file_predial=f_predial,
                    file_titulo_propiedad=f_titulo_propiedad,
                    file_plano_arquitectonico=f_plano_arquitectonico,
                    file_constancia_no_afectacion=f_constancia_no_afectacion,
                    file_uso_suelo=f_uso_suelo,
                    file_analisis_riesgo=f_analisis_riesgo,
                    file_pago=f_pago
                )
                messages.success(request, f"¡Solicitud de Construcción/Remodelación para '{establecimiento}' enviada con éxito!")
                return redirect('home')
            else:
                messages.error(request, "Por favor completa todos los campos obligatorios.")
                
        elif tramite.form_type == 'TERCEROS_PC':
            tipo_anuencia_terceros = tramite.sub_tipo if tramite.sub_tipo else request.POST.get('tipo_anuencia_terceros')
            propietario = request.POST.get('propietario_representante')
            tel_contacto = request.POST.get('telefono_contacto')
            correo_c = request.POST.get('correo_contacto')
            realiza_nombre = request.POST.get('realiza_nombre')
            realiza_telefono = request.POST.get('realiza_telefono')
            realiza_correo = request.POST.get('realiza_correo')

            # Archivos Físicos
            f_ine = request.FILES.get('file_ine')
            f_cedula = request.FILES.get('file_cedula_estatal')
            f_cv = request.FILES.get('file_curriculum')
            f_pago = request.FILES.get('file_pago')

            # Booleans basados en existencia
            d_ine = f_ine is not None
            r_cedula = f_cedula is not None
            r_cv = f_cv is not None
            r_pago = f_pago is not None

            rfc_val = rfc.upper() if rfc else "XAXX010101000"

            if establecimiento and propietario:
                SolicitudTramite.objects.create(
                    tramite=tramite,
                    ciudadano=ciudadano,
                    establecimiento=establecimiento,
                    rfc=rfc_val,
                    pdf_documento=pdf,
                    tipo_anuencia_terceros=tipo_anuencia_terceros,
                    propietario_representante=propietario,
                    telefono_contacto=tel_contacto,
                    correo_contacto=correo_c,
                    realiza_nombre=realiza_nombre,
                    realiza_telefono=realiza_telefono,
                    realiza_correo=realiza_correo,
                    doc_ine=d_ine,
                    req_cedula_estatal=r_cedula,
                    req_curriculum=r_cv,
                    req_pago=r_pago,
                    file_ine=f_ine,
                    file_cedula_estatal=f_cedula,
                    file_curriculum=f_cv,
                    file_pago=f_pago
                )
                messages.success(request, f"¡Solicitud de Registro de Tercero Acreditado para '{establecimiento}' enviada con éxito!")
                return redirect('home')
            else:
                messages.error(request, "Por favor completa todos los campos obligatorios.")
                
        else:
            # Carga General Tradicional
            if establecimiento and rfc and pdf:
                SolicitudTramite.objects.create(
                    tramite=tramite,
                    ciudadano=ciudadano,
                    establecimiento=establecimiento,
                    rfc=rfc.upper(),
                    pdf_documento=pdf
                )
                messages.success(request, f"Tu solicitud para '{tramite.titulo}' ha sido enviada con éxito. Se iniciará la revisión técnica.")
                return redirect('home')
            else:
                messages.error(request, "Por favor, completa todos los campos y adjunta tu archivo PDF.")
            
    giros_pc = ActividadGiro.objects.all().order_by('numero')
    return render(request, 'portal/iniciar_tramite.html', {
        'tramite': tramite,
        'nombre_prellenado': nombre_prellenado,
        'correo_prellenado': correo_prellenado,
        'tel_prellenado': tel_prellenado,
        'giros_pc': giros_pc
    })

import random
from datetime import timedelta
from django.utils import timezone

def registro_ciudadano(request):
    if request.session.get('ciudadano_curp') or request.session.get('ciudadano_id'):
        return redirect('home')
        
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        primer_ap = request.POST.get('primer_apellido', '').strip()
        segundo_ap = request.POST.get('segundo_apellido', '').strip()
        correo = request.POST.get('correo', '').strip().lower()
        telefono = request.POST.get('telefono', '').strip()
        curp = request.POST.get('curp', '').strip().upper()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        if not nombre or not primer_ap or not correo or not telefono or not password:
            messages.error(request, "Por favor completa todos los campos obligatorios.")
        elif password != confirm_password:
            messages.error(request, "Las contraseñas no coinciden.")
        elif len(password) < 6:
            messages.error(request, "La contraseña debe tener al menos 6 caracteres por seguridad.")
        elif Ciudadano.objects.filter(correo=correo).exists():
            messages.error(request, "Este correo electrónico ya se encuentra registrado. Inicia sesión.")
        elif curp and Ciudadano.objects.filter(curp=curp).exists():
            messages.error(request, "Esta CURP ya cuenta con una cuenta registrada.")
        else:
            # Generar Código OTP de 2 Pasos
            codigo_2fa = str(random.randint(100000, 999999))
            
            # Crear ciudadano con contraseña cifrada (make_password)
            ciudadano = Ciudadano.objects.create(
                nombre=nombre,
                primer_apellido=primer_ap,
                segundo_apellido=segundo_ap if segundo_ap else None,
                correo=correo,
                telefono=telefono,
                curp=curp if curp else None,
                password=make_password(password),
                codigo_2fa=codigo_2fa,
                codigo_2fa_expiracion=timezone.now() + timedelta(minutes=5)
            )
            
            request.session['pending_2fa_ciudadano_id'] = ciudadano.id
            
            from portal.utils.email_utils import enviar_correo_2fa
            enviado_email = enviar_correo_2fa(ciudadano, codigo_2fa)
            if enviado_email:
                messages.success(request, f"¡Registro inicial exitoso! 🔒 Se ha enviado un código de verificación a tu correo: {ciudadano.correo}")
            else:
                messages.info(request, f"¡Registro inicial exitoso! 🔒 Tu código de verificación en 2 pasos es: {codigo_2fa}")
            return redirect('verificar_2fa')
    return render(request, 'portal/registro_ciudadano.html')

def perfil_ciudadano(request):
    ciudadano_id = request.session.get('ciudadano_id')
    curp_sesion = request.session.get('ciudadano_curp')
    if not ciudadano_id and not curp_sesion:
        messages.error(request, "Debes iniciar sesión como ciudadano para ver tu perfil.")
        return redirect('login_unificado')
        
    if ciudadano_id:
        ciudadano = get_object_or_404(Ciudadano, id=ciudadano_id)
    else:
        ciudadano = Ciudadano.objects.filter(models.Q(curp=curp_sesion) | models.Q(correo=curp_sesion)).first()
        if not ciudadano:
            messages.error(request, "Sesión no válida o expirada.")
            return redirect('login_unificado')
    
    # Obtener solicitudes (con select_related para evitar N+1 en tramite) y reportes
    solicitudes = SolicitudTramite.objects.filter(ciudadano=ciudadano).select_related('tramite').order_by('-creado_en')
    reportes = ReporteRiesgo.objects.filter(ciudadano=ciudadano).order_by('-fecha_reporte')
    
    # Obtener seleccionado
    sel_tipo = request.GET.get('tipo')
    sel_id = request.GET.get('id')
    selected_solicitud = None
    selected_reporte = None
    
    if sel_tipo == 'solicitud' and sel_id:
        selected_solicitud = solicitudes.filter(id=sel_id).first()
        if selected_solicitud:
            # Cargar chat solo del seleccionado (evita consultas en bucle)
            selected_solicitud.mensajes = selected_solicitud.mensajes_chat.all().select_related('remitente_admin').order_by('fecha_envio')
    elif sel_tipo == 'reporte' and sel_id:
        selected_reporte = reportes.filter(id=sel_id).first()
        if selected_reporte:
            # Cargar chat solo del seleccionado (evita consultas en bucle)
            selected_reporte.mensajes = selected_reporte.mensajes_chat.all().select_related('remitente_admin').order_by('fecha_envio')
        
    return render(request, 'portal/perfil_ciudadano.html', {
        'ciudadano': ciudadano,
        'solicitudes': solicitudes,
        'reportes': reportes,
        'selected_solicitud': selected_solicitud,
        'selected_reporte': selected_reporte
    })

def api_cintillo_clima(request):
    """API endpoint que proxy-obtiene los datos frescos de bannerAvisos.php del SMN CONAGUA en JSON."""
    from portal.utils.clima_utils import obtener_cintillo_smn_directo
    from django.http import JsonResponse
    avisos = obtener_cintillo_smn_directo()
    return JsonResponse({'status': 'ok', 'items': avisos})
