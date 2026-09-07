# ==============================================================================
#  🚑 CONTROL DE VEHÍCULOS Y BITÁCORA DIGITAL DE EMERGENCIAS
#  Copyright (c) 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
# ==============================================================================

import json
import datetime
from datetime import timedelta
from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q, Sum, Avg, Count
from django.http import JsonResponse, HttpResponse
from django.utils import timezone

from portal.models import (
    VehiculoUnidad,
    BitacoraSalidaVehiculo,
    RegistroCargaGasolina,
    RegistroCargaGasolina,
    Trabajador,
    ReporteRiesgo
)

# ==============================================================================
# 🔐 DECORADORES Y AUXILIARES DE AUTENTICACIÓN E INTERCEPTACIÓN DE ROLES
# ==============================================================================

def obtener_operador_actual(request):
    operador_id = request.session.get('operador_id')
    if not operador_id:
        return None
    try:
        return Trabajador.objects.get(id=operador_id)
    except Trabajador.DoesNotExist:
        return None


def requiere_operador_aprobado(view_func):
    """
    Verifica que el trabajador haya iniciado sesión y su cuenta esté ACTIVA con algún rol_vehicular.
    O que sea un administrador de sistema de la Intranet (Django Auth).
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        # 1. Checar si es Admin de Sistema (Intranet)
        if request.user.is_authenticated and (request.user.is_staff or getattr(request.user, 'rol_nivel', '') in ['SUPER', 'VALIDADOR']):
            request.operador_actual = request.user
            return view_func(request, *args, **kwargs)
            
        # 2. Flujo normal Operadores
        operador = obtener_operador_actual(request)
        if not operador:
            messages.info(request, "Por favor inicia sesión para acceder a este módulo.")
            return redirect('login_operador')
        if not operador.is_active:
            messages.error(request, "Tu cuenta de trabajador está desactivada.")
            return redirect('login_operador')
        if getattr(operador, 'rol_vehicular', 'NINGUNO') == 'NINGUNO':
            messages.error(request, "No tienes permisos operativos.")
            return redirect('login_operador')
        request.operador_actual = operador
        return view_func(request, *args, **kwargs)
    return _wrapped


def requiere_admin_flotilla(view_func):
    """
    Verifica que el usuario sea ADMINISTRADOR DE FLOTILLA o JEFE_GUARDIA,
    o que sea un administrador de sistema (Django Auth).
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        # 1. Checar si es Admin de Sistema (Intranet)
        if request.user.is_authenticated and (request.user.is_staff or getattr(request.user, 'rol_nivel', '') in ['SUPER', 'VALIDADOR']):
            request.operador_actual = request.user # Falso operador_actual para que no truene si lo busca
            return view_func(request, *args, **kwargs)
            
        # 2. Flujo normal para Trabajadores (Operadores de campo)
        operador = obtener_operador_actual(request)
        if not operador:
            messages.error(request, "Acceso denegado. Debes iniciar sesión.")
            return redirect('login_operador')
        if not operador.is_active:
            messages.error(request, "Tu cuenta está desactivada.")
            return redirect('login_operador')
        if getattr(operador, 'rol_vehicular', 'NINGUNO') not in ['ADMIN', 'JEFE_GUARDIA']:
            messages.error(request, "🚨 Acceso Denegado: Se requiere rol de Jefe de Guardia o Administrador.")
            return redirect('flotilla_vehiculos_hub')
        request.operador_actual = operador
        return view_func(request, *args, **kwargs)
    return _wrapped


# ==============================================================================
# 🔑 REGISTRO, LOGIN Y LOGOUT DE OPERADORES Y ADMINISTRADORES
# ==============================================================================

def registro_operador(request):
    """
    Deshabilitado temporalmente o modificado: ahora el registro se hace desde 
    el panel de administración principal /panel/crear_trabajador.
    """
    messages.error(request, "El registro de operadores vehiculares ahora se realiza desde el Panel Principal de Trabajadores.")
    return redirect('login_operador')


def login_operador(request):
    """
    Inicio de sesión unificado usando Trabajador para operadores y administradores de flotilla.
    """
    if request.method == 'POST':
        nombre_input = request.POST.get('nombre_completo', '').strip()
        password = request.POST.get('password', '').strip()

        try:
            # Buscar al trabajador de manera case-insensitive
            user = Trabajador.objects.filter(nombre__iexact=nombre_input).first()
            if not user:
                # Caso de contingencia para admins maestros si escriben "ADMIN"
                if nombre_input.upper() in ('ADMIN', 'ADMINISTRADOR', 'ADMINISTRADOR GENERAL'):
                    user = Trabajador.objects.filter(rol_vehicular='ADMIN').first()

            if user and check_password(password, user.password):
                if not user.is_active:
                    messages.error(request, "🔴 Tu cuenta ha sido desactivada. Contacta a la dirección.")
                    return render(request, 'portal/vehiculos_login.html', {'nombre_input': nombre_input})
                elif user.rol_vehicular == 'NINGUNO':
                    messages.error(request, "🚫 No tienes permisos asignados para acceder a Control Vehicular.")
                    return render(request, 'portal/vehiculos_login.html', {'nombre_input': nombre_input})
                
                user.ultimo_acceso_vehicular = timezone.now()
                user.save(update_fields=['ultimo_acceso_vehicular'])
                
                # Iniciar sesión unificada en session dict
                request.session['operador_id'] = user.id
                request.session['is_admin_flotilla'] = user.rol_vehicular == 'ADMIN'
                messages.success(request, f"¡Bienvenido, {user.nombre}!")
                
                if user.rol_vehicular == 'ADMIN':
                    return redirect('admin_vehiculos_dashboard')
                return redirect('flotilla_vehiculos_hub')
            else:
                messages.error(request, "Nombre o contraseña incorrectos.")
        except Exception as e:
            messages.error(request, "Nombre o contraseña incorrectos.")

    return render(request, 'portal/vehiculos_login.html')


def logout_operador(request):
    """
    Cierra la sesión del operador/administrador actual.
    """
    request.session.pop('operador_id', None)
    request.session.pop('operador_nombre', None)
    request.session.pop('operador_rol', None)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect('login_operador')


# ==============================================================================
# 🚜 HUB OPERATIVO Y REGISTROS EN CAMPO
# ==============================================================================

@requiere_operador_aprobado
def flotilla_vehiculos_hub(request):
    """
    Menú Operativo Unificado (App PWA): Alertas de Emergencia + Flotilla Vehicular.
    """
    unidades = VehiculoUnidad.objects.all()
    salidas_activas = BitacoraSalidaVehiculo.objects.filter(completado=False).select_related('unidad')
    salidas_recientes = BitacoraSalidaVehiculo.objects.filter(completado=True).select_related('unidad')[:15]

    reportes_pendientes = ReporteRiesgo.objects.filter(estatus='PENDIENTE').order_by('-fecha_reporte')
    reportes_en_proceso = ReporteRiesgo.objects.filter(estatus__in=['LEIDO', 'EN_PROCESO']).order_by('-fecha_reporte')

    return render(request, 'portal/vehiculos_flotilla.html', {
        'unidades': unidades,
        'salidas_activas': salidas_activas,
        'salidas_recientes': salidas_recientes,
        'reportes_pendientes': reportes_pendientes,
        'reportes_en_proceso': reportes_en_proceso,
        'operador_actual': request.operador_actual
    })


@requiere_operador_aprobado
def cambiar_estado_reporte_operativo(request, reporte_id, nuevo_estatus):
    """
    Permite a los brigadistas en campo cambiar el estado de un reporte de emergencia.
    """
    reporte = get_object_or_404(ReporteRiesgo, id=reporte_id)
    if nuevo_estatus in ['PENDIENTE', 'LEIDO', 'EN_PROCESO', 'RESUELTO']:
        reporte.estatus = nuevo_estatus
        if nuevo_estatus == 'RESUELTO':
            reporte.fecha_resolucion = timezone.now()
        reporte.save()
        messages.success(request, f"Estatus del reporte {reporte.numero_reporte} actualizado a '{reporte.get_estatus_display()}'.")
    else:
        messages.error(request, "Estatus no válido.")
    
    return redirect('flotilla_vehiculos_hub')


@requiere_operador_aprobado
def dar_salida_unidad(request, unidad_id):
    """
    Registra la SALIDA de un vehículo de emergencia.
    - El nombre del operador se auto-llena con el usuario autenticado.
    - Acepta asociar una alerta/reporte previa para auto-llenar la descripción del servicio.
    """
    unidad = get_object_or_404(VehiculoUnidad, id=unidad_id)

    if unidad.estatus == 'EN_SERVICIO':
        messages.error(request, f"La unidad {unidad.nombre_identificador} ya se encuentra en servicio.")
        return redirect('flotilla_vehiculos_hub')

    reporte_id = request.GET.get('reporte_id')
    reporte_asociado = None
    descripcion_prellenada = ""

    if reporte_id:
        try:
            reporte_asociado = ReporteRiesgo.objects.get(id=reporte_id)
            descripcion_prellenada = f"Atención a Incidente {reporte_asociado.numero_reporte} ({reporte_asociado.get_tipo_servicio_display()}) en {reporte_asociado.direccion}, {reporte_asociado.colonia}."
        except ReporteRiesgo.DoesNotExist:
            pass

    if request.method == 'POST':
        # El nombre del operador se auto-llena con el usuario en sesión
        operador_nombre = request.operador_actual.nombre_completo.strip().upper()
        guardia_turno = request.POST.get('guardia_turno', '').strip()
        descripcion_servicio = request.POST.get('descripcion_servicio', '').strip()
        odometro_salida = request.POST.get('odometro_salida', unidad.odometro_actual)
        gasolina_salida = request.POST.get('gasolina_salida', unidad.nivel_gasolina_actual)
        
        foto_odometro = request.FILES.get('foto_odometro_salida')
        foto_gasolina = request.FILES.get('foto_gasolina_salida')

        # Fotos obligatorias al dar salida
        if not foto_odometro or not foto_gasolina:
            messages.error(request, "⚠️ Es obligatorio subir ambas fotografías de evidencia: Foto del Odómetro y Foto del Nivel de Gasolina.")
            return render(request, 'portal/vehiculos_dar_salida.html', {
                'unidad': unidad,
                'operador_actual': request.operador_actual,
                'descripcion_prellenada': descripcion_prellenada,
                'reporte_asociado': reporte_asociado
            })

        try:
            odometro_salida_val = int(odometro_salida)
        except (ValueError, TypeError):
            odometro_salida_val = unidad.odometro_actual

        # Comparación de Odómetro para Incongruencias
        incongruencia = False
        detalle_incongruencia = ""
        odometro_anterior = unidad.odometro_actual

        if odometro_salida_val != odometro_anterior:
            incongruencia = True
            diff = odometro_salida_val - odometro_anterior
            signo = "+" if diff > 0 else ""
            detalle_incongruencia = f"Incongruencia: El sistema registraba {odometro_anterior} km y el operador ingresó {odometro_salida_val} km ({signo}{diff} km)."

        if operador_nombre and descripcion_servicio:
            salida = BitacoraSalidaVehiculo.objects.create(
                unidad=unidad,
                operador_nombre=operador_nombre,
                guardia_turno=guardia_turno,
                descripcion_servicio=descripcion_servicio,
                fecha_salida=timezone.now(),
                odometro_salida=odometro_salida_val,
                gasolina_salida=gasolina_salida,
                foto_odometro_salida=foto_odometro,
                foto_gasolina_salida=foto_gasolina,
                incongruencia_salida=incongruencia,
                detalle_incongruencia_salida=detalle_incongruencia,
                completado=False
            )

            unidad.estatus = 'EN_SERVICIO'
            unidad.odometro_actual = odometro_salida_val
            unidad.nivel_gasolina_actual = gasolina_salida
            unidad.save()

            if incongruencia:
                messages.warning(request, f"Salida registrada con ALERTA DE INCONGRUENCIA en Kilometraje para {unidad.nombre_identificador}. ({detalle_incongruencia})")
            else:
                messages.success(request, f"Salida registrada con éxito para {unidad.nombre_identificador}. Estatus cambiado a En Servicio.")
            return redirect('flotilla_vehiculos_hub')
        else:
            messages.error(request, "Por favor llena los campos requeridos.")

    return render(request, 'portal/vehiculos_dar_salida.html', {
        'unidad': unidad,
        'operador_actual': request.operador_actual,
        'descripcion_prellenada': descripcion_prellenada,
        'reporte_asociado': reporte_asociado
    })


@requiere_operador_aprobado
def registrar_retorno_unidad(request, bitacora_id):
    """
    Registra el RETORNO a base de una unidad.
    - Exige subir de manera obligatoria la Foto del Odómetro y la Foto de la Gasolina al llegar.
    """
    bitacora = get_object_or_404(BitacoraSalidaVehiculo.objects.select_related('unidad'), id=bitacora_id)
    unidad = bitacora.unidad

    if request.method == 'POST':
        odometro_llegada = request.POST.get('odometro_llegada', unidad.odometro_actual)
        gasolina_llegada = request.POST.get('gasolina_llegada', unidad.nivel_gasolina_actual)
        foto_llegada = request.FILES.get('foto_odometro_llegada')
        foto_gasolina_llegada = request.FILES.get('foto_gasolina_llegada')

        # Fotos obligatorias al registrar retorno
        if not foto_llegada or not foto_gasolina_llegada:
            messages.error(request, "⚠️ Es obligatorio subir ambas fotografías de evidencia al retornar: Foto del Odómetro y Foto del Nivel de Gasolina.")
            return render(request, 'portal/vehiculos_registrar_retorno.html', {
                'bitacora': bitacora,
                'unidad': unidad
            })

        try:
            odometro_llegada_val = int(odometro_llegada)
        except (ValueError, TypeError):
            odometro_llegada_val = bitacora.odometro_salida

        km_recorridos = max(0, odometro_llegada_val - bitacora.odometro_salida)
        ahora = timezone.now()
        duracion_min = int((ahora - bitacora.fecha_salida).total_seconds() / 60)

        bitacora.fecha_llegada = ahora
        bitacora.odometro_llegada = odometro_llegada_val
        bitacora.gasolina_llegada = gasolina_llegada
        bitacora.foto_odometro_llegada = foto_llegada
        bitacora.foto_gasolina_llegada = foto_gasolina_llegada
        bitacora.km_recorridos = km_recorridos
        bitacora.duracion_minutos = duracion_min
        bitacora.completado = True
        bitacora.save()

        unidad.estatus = 'DISPONIBLE'
        unidad.odometro_actual = odometro_llegada_val
        unidad.nivel_gasolina_actual = gasolina_llegada
        unidad.ultima_salida_finalizada = ahora
        unidad.save()

        messages.success(request, f"Retorno de {unidad.nombre_identificador} registrado con éxito. Recorrió {km_recorridos} km.")
        return redirect('flotilla_vehiculos_hub')

    return render(request, 'portal/vehiculos_registrar_retorno.html', {
        'bitacora': bitacora,
        'unidad': unidad
    })


@requiere_operador_aprobado
def registrar_carga_gasolina(request, unidad_id):
    """
    Registra una carga de combustible para una unidad.
    """
    unidad = get_object_or_404(VehiculoUnidad, id=unidad_id)

    if request.method == 'POST':
        operador = request.POST.get('operador', request.operador_actual.nombre_completo).strip().upper()
        litros = request.POST.get('litros_cargados', '0')
        costo = request.POST.get('costo_total', '0')
        odometro = request.POST.get('odometro_al_cargar', unidad.odometro_actual)
        foto_ticket = request.FILES.get('foto_ticket_o_bomba')
        notas = request.POST.get('notas', '').strip()

        try:
            litros_val = float(litros)
            costo_val = float(costo)
            odometro_val = int(odometro)
        except ValueError:
            litros_val = 0.0
            costo_val = 0.0
            odometro_val = unidad.odometro_actual

        if operador and litros_val > 0:
            RegistroCargaGasolina.objects.create(
                unidad=unidad,
                operador=operador,
                fecha_carga=timezone.now(),
                litros_cargados=litros_val,
                costo_total=costo_val,
                odometro_al_cargar=odometro_val,
                foto_ticket_o_bomba=foto_ticket,
                notas=notas
            )

            unidad.nivel_gasolina_actual = 'Lleno'
            unidad.odometro_actual = max(unidad.odometro_actual, odometro_val)
            unidad.save()

            messages.success(request, f"Carga de combustible registrada para {unidad.nombre_identificador}.")
            return redirect('flotilla_vehiculos_hub')

    return render(request, 'portal/vehiculos_carga_gasolina.html', {
        'unidad': unidad,
        'operador_actual': request.operador_actual
    })


# ==============================================================================
# 📊 MIGRACIÓN: VISTAS ADMINISTRATIVAS DE FLOTILLA INTEGRADAS EN INTRANET
# ==============================================================================
from portal.views.intranet import (
    intranet_flotilla_dashboard as admin_vehiculos_dashboard,
    intranet_crear_unidad as crear_unidad,
    intranet_editar_unidad as editar_unidad,
    intranet_eliminar_unidad as eliminar_unidad,
    intranet_historial_unidad as historial_unidad,
    intranet_historial_vehiculos as admin_historial_vehiculos,
    intranet_imprimir_reporte_historial as imprimir_reporte_historial_vehicular,
    intranet_reportes_jefe_selector as vista_impresion_reportes_jefe,
    intranet_imprimir_reporte_movimiento as imprimir_reporte_movimiento_vehicular,
    intranet_cambiar_estado_usuario as cambiar_estado_usuario,
    calcular_rango_fechas_vehiculos,
)
