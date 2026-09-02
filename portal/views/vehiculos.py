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
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        operador = obtener_operador_actual(request)
        if not operador:
            messages.info(request, "Por favor inicia sesión para acceder al sistema de vehiculos.")
            return redirect('login_operador')
        if not operador.is_active:
            messages.error(request, "Tu cuenta de trabajador está desactivada.")
            return redirect('login_operador')
        if operador.rol_vehicular == 'NINGUNO':
            messages.error(request, "No tienes permisos de operador vehicular.")
            return redirect('login_operador')
        request.operador_actual = operador
        return view_func(request, *args, **kwargs)
    return _wrapped


def requiere_admin_flotilla(view_func):
    """
    Verifica que el usuario sea ADMINISTRADOR DE FLOTILLA o JEFE_GUARDIA.
    Los operadores normales NO pueden ingresar a las configuraciones maestras.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        operador = obtener_operador_actual(request)
        if not operador:
            messages.error(request, "Acceso denegado. Debes iniciar sesión.")
            return redirect('login_operador')
        if not operador.is_active:
            messages.error(request, "Tu cuenta está desactivada.")
            return redirect('login_operador')
        if operador.rol_vehicular not in ['ADMIN', 'JEFE_GUARDIA']:
            messages.error(request, "⛔ Acceso Denegado: Se requiere rol de Jefe de Guardia o Administrador.")
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
# 📊 PANEL DE ADMINISTRACIÓN Y GESTIÓN DE USUARIOS
# ==============================================================================

@requiere_admin_flotilla
def admin_vehiculos_dashboard(request):
    """
    Panel de Administrador de Flotilla.
    Incluye gestión de unidades, bitácora histórica, cargas de combustible y administración de usuarios.
    """
    unidades = VehiculoUnidad.objects.all()
    salidas_todas = BitacoraSalidaVehiculo.objects.all().select_related('unidad')
    cargas_todas = RegistroCargaGasolina.objects.all().select_related('unidad')

    # Clasificación de Usuarios Operadores en Trabajador
    usuarios_pendientes = Trabajador.objects.filter(rol_vehicular='NINGUNO') # O podemos ignorar esto
    usuarios_activos = Trabajador.objects.exclude(rol_vehicular='NINGUNO')
    usuarios_desactivados = Trabajador.objects.filter(is_active=False)

    total_km = salidas_todas.aggregate(Sum('km_recorridos'))['km_recorridos__sum'] or 0
    total_litros = cargas_todas.aggregate(Sum('litros_cargados'))['litros_cargados__sum'] or 0
    total_costo = cargas_todas.aggregate(Sum('costo_total'))['costo_total__sum'] or 0
    rendimiento_promedio = round(total_km / total_litros, 2) if total_litros > 0 else 0

    return render(request, 'portal/vehiculos_admin_dashboard.html', {
        'unidades': unidades,
        'salidas_todas': salidas_todas,
        'cargas_todas': cargas_todas,
        'usuarios_activos': usuarios_activos,
        'usuarios_desactivados': usuarios_desactivados,
        'total_km': total_km,
        'total_litros': total_litros,
        'total_costo': total_costo,
        'rendimiento_promedio': rendimiento_promedio,
        'operador_actual': request.operador_actual
    })

@requiere_admin_flotilla
def cambiar_estado_usuario(request, usuario_id, nuevo_estado):
    """
    Permite al Administrador asignar un rol vehicular o desactivar a un Trabajador.
    """
    usuario = get_object_or_404(Trabajador, id=usuario_id)
    
    if nuevo_estado in ['NINGUNO', 'OPERADOR', 'JEFE_GUARDIA', 'ADMIN']:
        usuario.rol_vehicular = nuevo_estado
        usuario.save(update_fields=['rol_vehicular'])
        messages.success(request, f"El rol vehicular de '{usuario.nombre}' fue cambiado a {nuevo_estado}.")
    elif nuevo_estado == 'DESACTIVAR':
        usuario.is_active = False
        usuario.save(update_fields=['is_active'])
        messages.success(request, f"La cuenta de '{usuario.nombre}' ha sido desactivada globalmente.")
    
    return redirect('admin_vehiculos_dashboard')


@requiere_admin_flotilla
def vista_impresion_reportes_jefe(request):
    """
    Pantalla intermedia donde el Jefe de Guardia / Admin selecciona
    qué unidad, fecha y turno desea exportar a PDF.
    """
    unidades = VehiculoUnidad.objects.all()
    return render(request, 'portal/vehiculos_reporte_selector.html', {
        'unidades': unidades,
        'operador_actual': request.operador_actual
    })


@requiere_admin_flotilla
def imprimir_reporte_movimiento_vehicular(request):
    """
    Genera el formato HTML para el Reporte de Movimiento Vehicular (PDF).
    """
    unidad_id = request.GET.get('unidad_id')
    fecha_str = request.GET.get('fecha') # YYYY-MM-DD
    turno = request.GET.get('turno', 'TURNO_1')
    formato = request.GET.get('formato', '1_turno') # '1_turno' o '2_turnos'

    unidad = get_object_or_404(VehiculoUnidad, id=unidad_id)
    
    try:
        from datetime import datetime, time
        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        fecha_obj = timezone.now().date()

    # Definir rango de horas según el turno
    # Turno 1 (00:00 - 12:00), Turno 2 (12:00 - 00:00)
    import datetime as dt
    if turno == 'TURNO_1':
        hora_inicio = timezone.make_aware(dt.datetime.combine(fecha_obj, dt.time.min))
        hora_fin = hora_inicio + dt.timedelta(hours=12)
    else:
        hora_inicio = timezone.make_aware(dt.datetime.combine(fecha_obj, dt.time.min)) + dt.timedelta(hours=12)
        hora_fin = hora_inicio + dt.timedelta(hours=12)

    salidas = BitacoraSalidaVehiculo.objects.filter(
        unidad=unidad,
        fecha_salida__gte=hora_inicio,
        fecha_salida__lt=hora_fin
    ).order_by('fecha_salida')

    cargas = RegistroCargaGasolina.objects.filter(
        unidad=unidad,
        fecha_carga__gte=hora_inicio,
        fecha_carga__lt=hora_fin
    ).order_by('fecha_carga')
    
    # Calcular promedios, tanque inicial/final
    tanque_inicial = salidas.first().gasolina_salida if salidas.exists() else unidad.nivel_gasolina_actual
    tanque_final = salidas.last().gasolina_llegada if salidas.exists() else unidad.nivel_gasolina_actual
    
    context = {
        'unidad': unidad,
        'fecha': fecha_obj,
        'hora_inicio': hora_inicio,
        'hora_fin': hora_fin,
        'turno': turno,
        'formato': formato,
        'salidas': salidas,
        'cargas': cargas,
        'tanque_inicial': tanque_inicial,
        'tanque_final': tanque_final,
        'operador_actual': request.operador_actual,
    }
    
    return render(request, 'portal/vehiculos_imprimir_reporte.html', context)

@requiere_admin_flotilla
def crear_unidad(request):
    """
    Crea una nueva unidad de vehículo en la flotilla.
    """
    if request.method == 'POST':
        numero_unidad = request.POST.get('numero_unidad', '').strip()
        nombre_identificador = request.POST.get('nombre_identificador', '').strip()
        tipo_vehiculo = request.POST.get('tipo_vehiculo', 'Ambulancia').strip()
        placas = request.POST.get('placas', '').strip()
        odometro_actual = request.POST.get('odometro_actual', '0')
        nivel_gasolina_actual = request.POST.get('nivel_gasolina_actual', 'Lleno').strip()
        foto_unidad = request.FILES.get('foto_unidad')

        try:
            odometro_val = int(odometro_actual)
        except ValueError:
            odometro_val = 0

        if numero_unidad and nombre_identificador:
            if VehiculoUnidad.objects.filter(numero_unidad=numero_unidad).exists():
                messages.error(request, f"Ya existe una unidad registrada con el número '{numero_unidad}'.")
            else:
                unidad = VehiculoUnidad.objects.create(
                    numero_unidad=numero_unidad,
                    nombre_identificador=nombre_identificador,
                    tipo_vehiculo=tipo_vehiculo,
                    placas=placas,
                    odometro_actual=odometro_val,
                    nivel_gasolina_actual=nivel_gasolina_actual,
                    foto_unidad=foto_unidad,
                    estatus='DISPONIBLE'
                )
                messages.success(request, f"Unidad '{unidad.nombre_identificador}' agregada con éxito a la flotilla.")
        else:
            messages.error(request, "Por favor completa los campos requeridos.")

    return redirect('admin_vehiculos_dashboard')


@requiere_admin_flotilla
def editar_unidad(request, unidad_id):
    """
    Edita una unidad existente o retorna sus datos en JSON.
    """
    unidad = get_object_or_404(VehiculoUnidad, id=unidad_id)

    if request.method == 'POST':
        unidad.numero_unidad = request.POST.get('numero_unidad', unidad.numero_unidad).strip()
        unidad.nombre_identificador = request.POST.get('nombre_identificador', unidad.nombre_identificador).strip()
        unidad.tipo_vehiculo = request.POST.get('tipo_vehiculo', unidad.tipo_vehiculo).strip()
        unidad.placas = request.POST.get('placas', '').strip()
        unidad.estatus = request.POST.get('estatus', unidad.estatus).strip()
        
        try:
            unidad.odometro_actual = int(request.POST.get('odometro_actual', unidad.odometro_actual))
        except ValueError:
            pass

        unidad.nivel_gasolina_actual = request.POST.get('nivel_gasolina_actual', unidad.nivel_gasolina_actual).strip()
        
        if request.FILES.get('foto_unidad'):
            unidad.foto_unidad = request.FILES.get('foto_unidad')

        unidad.save()
        messages.success(request, f"Unidad '{unidad.nombre_identificador}' actualizada con éxito.")
        return redirect('admin_vehiculos_dashboard')

    return JsonResponse({
        'id': unidad.id,
        'numero_unidad': unidad.numero_unidad,
        'nombre_identificador': unidad.nombre_identificador,
        'tipo_vehiculo': unidad.tipo_vehiculo,
        'placas': unidad.placas or '',
        'estatus': unidad.estatus,
        'odometro_actual': unidad.odometro_actual,
        'nivel_gasolina_actual': unidad.nivel_gasolina_actual,
        'foto_url': unidad.foto_unidad.url if unidad.foto_unidad else ''
    })


@requiere_admin_flotilla
def eliminar_unidad(request, unidad_id):
    """
    Elimina una unidad de la flotilla.
    """
    unidad = get_object_or_404(VehiculoUnidad, id=unidad_id)
    nombre = unidad.nombre_identificador
    unidad.delete()
    messages.success(request, f"Se eliminó la unidad '{nombre}' de la flotilla.")
    return redirect('admin_vehiculos_dashboard')


@requiere_admin_flotilla
def historial_unidad(request, unidad_id):
    """
    Muestra los antecedentes e historial completo de salidas y cargas de una unidad específica,
    ordenado del viaje más reciente al más antiguo.
    """
    unidad = get_object_or_404(VehiculoUnidad, id=unidad_id)
    
    # Salidas/viajes ordenados del último (más reciente) al primero
    salidas = BitacoraSalidaVehiculo.objects.filter(unidad=unidad).order_by('-fecha_salida')
    cargas = RegistroCargaGasolina.objects.filter(unidad=unidad).order_by('-fecha_carga')

    # Métricas específicas de la unidad
    total_km_unidad = salidas.aggregate(Sum('km_recorridos'))['km_recorridos__sum'] or 0
    total_viajes = salidas.count()
    total_litros_unidad = cargas.aggregate(Sum('litros_cargados'))['litros_cargados__sum'] or 0
    total_costo_gasolina = cargas.aggregate(Sum('costo_total'))['costo_total__sum'] or 0

    return render(request, 'portal/vehiculos_historial_unidad.html', {
        'unidad': unidad,
        'salidas': salidas,
        'cargas': cargas,
        'total_km_unidad': total_km_unidad,
        'total_viajes': total_viajes,
        'total_litros_unidad': total_litros_unidad,
        'total_costo_gasolina': total_costo_gasolina,
        'operador_actual': request.operador_actual
    })


# ==============================================================================
# 📋 HISTORIAL Y EXTRACTOR OFICIAL DE VEHÍCULOS (MODO ADMINISTRADOR)
# ==============================================================================

def calcular_rango_fechas_vehiculos(periodo, fecha_inicio_str=None, fecha_fin_str=None):
    ahora = timezone.now()
    hoy = ahora.date()

    if periodo == 'hoy':
        dt_inicio = datetime.datetime.combine(hoy, datetime.time.min, tzinfo=ahora.tzinfo)
        dt_fin = datetime.datetime.combine(hoy, datetime.time.max, tzinfo=ahora.tzinfo)
        texto_periodo = f"Hoy ({hoy.strftime('%d/%m/%Y')})"
    elif periodo == '2dias':
        hace_2_dias = hoy - timedelta(days=1)
        dt_inicio = datetime.datetime.combine(hace_2_dias, datetime.time.min, tzinfo=ahora.tzinfo)
        dt_fin = datetime.datetime.combine(hoy, datetime.time.max, tzinfo=ahora.tzinfo)
        texto_periodo = f"Últimos 2 Días ({hace_2_dias.strftime('%d/%m/%Y')} al {hoy.strftime('%d/%m/%Y')})"
    elif periodo == '7dias':
        hace_7_dias = hoy - timedelta(days=6)
        dt_inicio = datetime.datetime.combine(hace_7_dias, datetime.time.min, tzinfo=ahora.tzinfo)
        dt_fin = datetime.datetime.combine(hoy, datetime.time.max, tzinfo=ahora.tzinfo)
        texto_periodo = f"Últimos 7 Días ({hace_7_dias.strftime('%d/%m/%Y')} al {hoy.strftime('%d/%m/%Y')})"
    elif periodo == 'este_mes':
        inicio_mes = hoy.replace(day=1)
        dt_inicio = datetime.datetime.combine(inicio_mes, datetime.time.min, tzinfo=ahora.tzinfo)
        dt_fin = datetime.datetime.combine(hoy, datetime.time.max, tzinfo=ahora.tzinfo)
        texto_periodo = f"Este Mes ({inicio_mes.strftime('%d/%m/%Y')} al {hoy.strftime('%d/%m/%Y')})"
    elif periodo == 'mes_anterior':
        primer_dia_este_mes = hoy.replace(day=1)
        ultimo_dia_mes_ant = primer_dia_este_mes - timedelta(days=1)
        primer_dia_mes_ant = ultimo_dia_mes_ant.replace(day=1)
        dt_inicio = datetime.datetime.combine(primer_dia_mes_ant, datetime.time.min, tzinfo=ahora.tzinfo)
        dt_fin = datetime.datetime.combine(ultimo_dia_mes_ant, datetime.time.max, tzinfo=ahora.tzinfo)
        texto_periodo = f"Mes Anterior ({primer_dia_mes_ant.strftime('%d/%m/%Y')} al {ultimo_dia_mes_ant.strftime('%d/%m/%Y')})"
    elif periodo == 'este_ano':
        inicio_ano = hoy.replace(month=1, day=1)
        dt_inicio = datetime.datetime.combine(inicio_ano, datetime.time.min, tzinfo=ahora.tzinfo)
        dt_fin = datetime.datetime.combine(hoy, datetime.time.max, tzinfo=ahora.tzinfo)
        texto_periodo = f"Este Año ({inicio_ano.strftime('%d/%m/%Y')} al {hoy.strftime('%d/%m/%Y')})"
    elif periodo == 'personalizado' and fecha_inicio_str and fecha_fin_str:
        try:
            f_ini = datetime.datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            f_fin = datetime.datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            if f_ini > f_fin:
                f_ini, f_fin = f_fin, f_ini
            dt_inicio = datetime.datetime.combine(f_ini, datetime.time.min, tzinfo=ahora.tzinfo)
            dt_fin = datetime.datetime.combine(f_fin, datetime.time.max, tzinfo=ahora.tzinfo)
            texto_periodo = f"Del {f_ini.strftime('%d/%m/%Y')} al {f_fin.strftime('%d/%m/%Y')}"
        except ValueError:
            inicio_mes = hoy.replace(day=1)
            dt_inicio = datetime.datetime.combine(inicio_mes, datetime.time.min, tzinfo=ahora.tzinfo)
            dt_fin = datetime.datetime.combine(hoy, datetime.time.max, tzinfo=ahora.tzinfo)
            texto_periodo = f"Este Mes ({inicio_mes.strftime('%d/%m/%Y')} al {hoy.strftime('%d/%m/%Y')})"
            periodo = 'este_mes'
    else:
        periodo = 'este_mes'
        inicio_mes = hoy.replace(day=1)
        dt_inicio = datetime.datetime.combine(inicio_mes, datetime.time.min, tzinfo=ahora.tzinfo)
        dt_fin = datetime.datetime.combine(hoy, datetime.time.max, tzinfo=ahora.tzinfo)
        texto_periodo = f"Este Mes ({inicio_mes.strftime('%d/%m/%Y')} al {hoy.strftime('%d/%m/%Y')})"

    return dt_inicio, dt_fin, periodo, texto_periodo


@requiere_admin_flotilla
def admin_historial_vehiculos(request):
    """
    Panel interactivo de Administrador para consultar, filtrar y extraer el historial de vehículos
    por período dinámico (1 día, 2 días, 1 semana, 1 mes, 1 año o personalizado)
    y por unidad específica o flotilla completa.
    """
    periodo = request.GET.get('periodo', 'este_mes')
    fecha_inicio_str = request.GET.get('fecha_inicio', '')
    fecha_fin_str = request.GET.get('fecha_fin', '')
    unidad_id = request.GET.get('unidad_id', 'todas')

    dt_inicio, dt_fin, periodo, texto_periodo = calcular_rango_fechas_vehiculos(
        periodo, fecha_inicio_str, fecha_fin_str
    )

    unidades = VehiculoUnidad.objects.all().order_by('numero_unidad', 'nombre_identificador')
    unidad_seleccionada = None

    salidas_qs = BitacoraSalidaVehiculo.objects.filter(
        fecha_salida__gte=dt_inicio,
        fecha_salida__lte=dt_fin
    ).select_related('unidad').order_by('-fecha_salida')

    cargas_qs = RegistroCargaGasolina.objects.filter(
        fecha_carga__gte=dt_inicio,
        fecha_carga__lte=dt_fin
    ).select_related('unidad', 'operador').order_by('-fecha_carga')

    if unidad_id and unidad_id != 'todas':
        try:
            unidad_seleccionada = VehiculoUnidad.objects.get(id=int(unidad_id))
            salidas_qs = salidas_qs.filter(unidad=unidad_seleccionada)
            cargas_qs = cargas_qs.filter(unidad=unidad_seleccionada)
        except (ValueError, VehiculoUnidad.DoesNotExist):
            unidad_id = 'todas'
            unidad_seleccionada = None

    # Métricas agregadas en el período
    total_salidas = salidas_qs.count()
    total_km = salidas_qs.aggregate(Sum('km_recorridos'))['km_recorridos__sum'] or 0
    total_litros = cargas_qs.aggregate(Sum('litros_cargados'))['litros_cargados__sum'] or 0
    total_costo = cargas_qs.aggregate(Sum('costo_total'))['costo_total__sum'] or 0
    rendimiento_promedio = round(total_km / total_litros, 2) if total_litros > 0 else 0

    # Resumen por unidad
    resumen_unidades = []
    for u in unidades:
        u_salidas = salidas_qs.filter(unidad=u)
        u_cargas = cargas_qs.filter(unidad=u)
        u_km = u_salidas.aggregate(Sum('km_recorridos'))['km_recorridos__sum'] or 0
        u_litros = u_cargas.aggregate(Sum('litros_cargados'))['litros_cargados__sum'] or 0
        u_costo = u_cargas.aggregate(Sum('costo_total'))['costo_total__sum'] or 0
        
        if u_salidas.exists() or u_cargas.exists() or unidad_seleccionada == u:
            resumen_unidades.append({
                'unidad': u,
                'viajes': u_salidas.count(),
                'km': u_km,
                'litros': u_litros,
                'costo': u_costo,
                'rendimiento': round(u_km / u_litros, 2) if u_litros > 0 else 0
            })

    context = {
        'unidades': unidades,
        'unidad_seleccionada': unidad_seleccionada,
        'unidad_id_actual': str(unidad_id),
        'periodo': periodo,
        'texto_periodo': texto_periodo,
        'fecha_inicio_str': dt_inicio.strftime('%Y-%m-%d'),
        'fecha_fin_str': dt_fin.strftime('%Y-%m-%d'),
        'salidas': salidas_qs,
        'cargas': cargas_qs,
        'total_salidas': total_salidas,
        'total_km': total_km,
        'total_litros': total_litros,
        'total_costo': total_costo,
        'rendimiento_promedio': rendimiento_promedio,
        'resumen_unidades': resumen_unidades,
        'operador_actual': request.operador_actual,
        'fecha_emision': timezone.now()
    }

    return render(request, 'portal/vehiculos_historial_admin.html', context)


@requiere_admin_flotilla
def imprimir_reporte_historial_vehicular(request):
    """
    Renderiza la Hoja Oficial de Bitácora de Flotilla en orientación VERTICAL (Letter Portrait)
    con logos institucionales, metadatos, tablas de servicio y firmas oficiales (estilo Guardias).
    """
    periodo = request.GET.get('periodo', 'este_mes')
    fecha_inicio_str = request.GET.get('fecha_inicio', '')
    fecha_fin_str = request.GET.get('fecha_fin', '')
    unidad_id = request.GET.get('unidad_id', 'todas')

    dt_inicio, dt_fin, periodo, texto_periodo = calcular_rango_fechas_vehiculos(
        periodo, fecha_inicio_str, fecha_fin_str
    )

    unidades = VehiculoUnidad.objects.all().order_by('numero_unidad', 'nombre_identificador')
    unidad_seleccionada = None

    salidas_qs = BitacoraSalidaVehiculo.objects.filter(
        fecha_salida__gte=dt_inicio,
        fecha_salida__lte=dt_fin
    ).select_related('unidad').order_by('fecha_salida')

    cargas_qs = RegistroCargaGasolina.objects.filter(
        fecha_carga__gte=dt_inicio,
        fecha_carga__lte=dt_fin
    ).select_related('unidad', 'operador').order_by('fecha_carga')

    if unidad_id and unidad_id != 'todas':
        try:
            unidad_seleccionada = VehiculoUnidad.objects.get(id=int(unidad_id))
            salidas_qs = salidas_qs.filter(unidad=unidad_seleccionada)
            cargas_qs = cargas_qs.filter(unidad=unidad_seleccionada)
        except (ValueError, VehiculoUnidad.DoesNotExist):
            unidad_id = 'todas'
            unidad_seleccionada = None

    total_salidas = salidas_qs.count()
    total_km = salidas_qs.aggregate(Sum('km_recorridos'))['km_recorridos__sum'] or 0
    total_litros = cargas_qs.aggregate(Sum('litros_cargados'))['litros_cargados__sum'] or 0
    total_costo = cargas_qs.aggregate(Sum('costo_total'))['costo_total__sum'] or 0
    rendimiento_promedio = round(total_km / total_litros, 2) if total_litros > 0 else 0

    resumen_unidades = []
    for u in unidades:
        u_salidas = salidas_qs.filter(unidad=u)
        u_cargas = cargas_qs.filter(unidad=u)
        u_km = u_salidas.aggregate(Sum('km_recorridos'))['km_recorridos__sum'] or 0
        u_litros = u_cargas.aggregate(Sum('litros_cargados'))['litros_cargados__sum'] or 0
        u_costo = u_cargas.aggregate(Sum('costo_total'))['costo_total__sum'] or 0
        
        if u_salidas.exists() or u_cargas.exists() or unidad_seleccionada == u:
            resumen_unidades.append({
                'unidad': u,
                'viajes': u_salidas.count(),
                'km': u_km,
                'litros': u_litros,
                'costo': u_costo,
                'rendimiento': round(u_km / u_litros, 2) if u_litros > 0 else 0
            })

    context = {
        'unidades': unidades,
        'unidad_seleccionada': unidad_seleccionada,
        'unidad_id_actual': str(unidad_id),
        'periodo': periodo,
        'texto_periodo': texto_periodo,
        'fecha_inicio_str': dt_inicio.strftime('%d/%m/%Y'),
        'fecha_fin_str': dt_fin.strftime('%d/%m/%Y'),
        'salidas': salidas_qs,
        'cargas': cargas_qs,
        'total_salidas': total_salidas,
        'total_km': total_km,
        'total_litros': total_litros,
        'total_costo': total_costo,
        'rendimiento_promedio': rendimiento_promedio,
        'resumen_unidades': resumen_unidades,
        'fecha_emision': timezone.now()
    }

    return render(request, 'portal/vehiculos_reporte_imprimir.html', context)

