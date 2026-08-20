# ==============================================================================
#  🚑 CONTROL DE VEHÍCULOS Y BITÁCORA DIGITAL DE EMERGENCIAS
#  Copyright (c) 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
# ==============================================================================

import json
import datetime
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
    UsuarioOperadorVehiculo
)

# ==============================================================================
# 🔐 DECORADORES Y AUXILIARES DE AUTENTICACIÓN E INTERCEPTACIÓN DE ROLES
# ==============================================================================

def obtener_operador_actual(request):
    operador_id = request.session.get('operador_id')
    if not operador_id:
        return None
    try:
        return UsuarioOperadorVehiculo.objects.get(id=operador_id)
    except UsuarioOperadorVehiculo.DoesNotExist:
        return None


def requiere_operador_aprobado(view_func):
    """
    Verifica que el operador haya iniciado sesión y su cuenta esté APROBADA.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        operador = obtener_operador_actual(request)
        if not operador:
            messages.info(request, "Por favor inicia sesión o regístrate para acceder al sistema de vehiculos.")
            return redirect('login_operador')
        if operador.estado != 'APROBADO':
            messages.error(request, "Tu cuenta aún se encuentra pendiente de aprobación por el Administrador.")
            return redirect('login_operador')
        request.operador_actual = operador
        return view_func(request, *args, **kwargs)
    return _wrapped


def requiere_admin_flotilla(view_func):
    """
    Verifica que el usuario sea exclusivamente ADMINISTRADOR DE FLOTILLA.
    Los operadores normales NO pueden ingresar.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        operador = obtener_operador_actual(request)
        if not operador:
            messages.error(request, "Acceso denegado. Debes iniciar sesión como Administrador.")
            return redirect('login_operador')
        if operador.estado != 'APROBADO':
            messages.error(request, "Tu cuenta de Administrador está desactivada o pendiente.")
            return redirect('login_operador')
        if operador.rol != 'ADMIN':
            messages.error(request, "⛔ Acceso Denegado: Tu usuario de Operador NO tiene permisos para ingresar al Panel de Administración.")
            return redirect('flotilla_vehiculos_hub')
        request.operador_actual = operador
        return view_func(request, *args, **kwargs)
    return _wrapped


# ==============================================================================
# 🔑 REGISTRO, LOGIN Y LOGOUT DE OPERADORES Y ADMINISTRADORES
# ==============================================================================

def registro_operador(request):
    """
    Registro por primera vez de un operador.
    Transforma el nombre a MAYÚSCULAS obligatoriamente y guarda la cuenta como PENDIENTE.
    """
    if request.method == 'POST':
        nombre_input = request.POST.get('nombre_completo', '').strip()
        password = request.POST.get('password', '').strip()

        nombre_mayus = nombre_input.upper()

        if len(nombre_mayus) < 3 or len(password) < 4:
            messages.error(request, "Por favor ingresa un nombre completo válido y una contraseña de al menos 4 caracteres.")
            return render(request, 'portal/vehiculos_registro.html', {'nombre_input': nombre_input})

        if UsuarioOperadorVehiculo.objects.filter(nombre_completo=nombre_mayus).exists():
            messages.error(request, f"Ya existe un operador registrado con el nombre '{nombre_mayus}'. Por favor inicia sesión.")
            return redirect('login_operador')

        # Crear cuenta pendiente de aprobación
        usuario = UsuarioOperadorVehiculo.objects.create(
            nombre_completo=nombre_mayus,
            password_hash=make_password(password),
            rol='OPERADOR',
            estado='PENDIENTE'
        )

        messages.success(request, f"¡Registro completado para {usuario.nombre_completo}! Tu cuenta está en espera de aprobación por el Administrador.")
        return redirect('login_operador')

    return render(request, 'portal/vehiculos_registro.html')


def login_operador(request):
    """
    Inicio de sesión para operadores y administradores de flotilla.
    """
    if request.method == 'POST':
        nombre_input = request.POST.get('nombre_completo', '').strip().upper()
        password = request.POST.get('password', '').strip()

        try:
            user = UsuarioOperadorVehiculo.objects.get(nombre_completo=nombre_input)
            if check_password(password, user.password_hash):
                if user.estado == 'PENDIENTE':
                    messages.warning(request, "🕒 Tu solicitud de registro aún está pendiente de aprobación por el Administrador.")
                    return render(request, 'portal/vehiculos_login.html', {'nombre_input': nombre_input})
                elif user.estado in ('DESACTIVADO', 'RECHAZADO'):
                    messages.error(request, "🔴 Tu cuenta ha sido desactivada o rechazada por el Administrador. Contacta a la dirección.")
                    return render(request, 'portal/vehiculos_login.html', {'nombre_input': nombre_input})
                elif user.estado == 'APROBADO':
                    user.ultimo_acceso = timezone.now()
                    user.save()

                    request.session['operador_id'] = user.id
                    request.session['operador_nombre'] = user.nombre_completo
                    request.session['operador_rol'] = user.rol

                    messages.success(request, f"Bienvenido/a {user.nombre_completo}")
                    if user.rol == 'ADMIN':
                        return redirect('admin_vehiculos_dashboard')
                    else:
                        return redirect('flotilla_vehiculos_hub')
            else:
                messages.error(request, "Contraseña incorrecta. Por favor verifica tus datos.")
        except UsuarioOperadorVehiculo.DoesNotExist:
            messages.error(request, f"No existe ninguna cuenta registrada con el nombre '{nombre_input}'. Te invitamos a registrarte.")

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
    Panel Principal de Flotilla y Bitácora Digital para Operadores Aprobados.
    """
    unidades = VehiculoUnidad.objects.all()
    salidas_activas = BitacoraSalidaVehiculo.objects.filter(completado=False).select_related('unidad')
    salidas_recientes = BitacoraSalidaVehiculo.objects.filter(completado=True).select_related('unidad')[:15]

    return render(request, 'portal/vehiculos_flotilla.html', {
        'unidades': unidades,
        'salidas_activas': salidas_activas,
        'salidas_recientes': salidas_recientes,
        'operador_actual': request.operador_actual
    })


@requiere_operador_aprobado
def dar_salida_unidad(request, unidad_id):
    """
    Registra la SALIDA de un vehículo de emergencia.
    """
    unidad = get_object_or_404(VehiculoUnidad, id=unidad_id)

    if unidad.estatus == 'EN_SERVICIO':
        messages.error(request, f"La unidad {unidad.nombre_identificador} ya se encuentra en servicio.")
        return redirect('flotilla_vehiculos_hub')

    if request.method == 'POST':
        operador_nombre = request.POST.get('operador_nombre', request.operador_actual.nombre_completo).strip().upper()
        guardia_turno = request.POST.get('guardia_turno', '').strip()
        descripcion_servicio = request.POST.get('descripcion_servicio', '').strip()
        odometro_salida = request.POST.get('odometro_salida', unidad.odometro_actual)
        gasolina_salida = request.POST.get('gasolina_salida', unidad.nivel_gasolina_actual)
        foto_odometro = request.FILES.get('foto_odometro_salida')

        try:
            odometro_salida_val = int(odometro_salida)
        except (ValueError, TypeError):
            odometro_salida_val = unidad.odometro_actual

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
                completado=False
            )

            unidad.estatus = 'EN_SERVICIO'
            unidad.odometro_actual = odometro_salida_val
            unidad.nivel_gasolina_actual = gasolina_salida
            unidad.save()

            messages.success(request, f"Salida registrada para {unidad.nombre_identificador}. Estatus cambiado a En Servicio.")
            return redirect('flotilla_vehiculos_hub')
        else:
            messages.error(request, "Por favor llena los campos requeridos.")

    return render(request, 'portal/vehiculos_dar_salida.html', {
        'unidad': unidad,
        'operador_actual': request.operador_actual
    })


@requiere_operador_aprobado
def registrar_retorno_unidad(request, bitacora_id):
    """
    Registra el RETORNO a base de una unidad.
    """
    bitacora = get_object_or_404(BitacoraSalidaVehiculo.objects.select_related('unidad'), id=bitacora_id)
    unidad = bitacora.unidad

    if request.method == 'POST':
        odometro_llegada = request.POST.get('odometro_llegada', unidad.odometro_actual)
        gasolina_llegada = request.POST.get('gasolina_llegada', unidad.nivel_gasolina_actual)
        foto_llegada = request.FILES.get('foto_odometro_llegada')

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

    # Clasificación de Usuarios Operadores
    usuarios_pendientes = UsuarioOperadorVehiculo.objects.filter(estado='PENDIENTE')
    usuarios_activos = UsuarioOperadorVehiculo.objects.filter(estado='APROBADO')
    usuarios_desactivados = UsuarioOperadorVehiculo.objects.filter(estado__in=['DESACTIVADO', 'RECHAZADO'])

    total_km = salidas_todas.aggregate(Sum('km_recorridos'))['km_recorridos__sum'] or 0
    total_litros = cargas_todas.aggregate(Sum('litros_cargados'))['litros_cargados__sum'] or 0
    total_costo = cargas_todas.aggregate(Sum('costo_total'))['costo_total__sum'] or 0
    rendimiento_promedio = round(total_km / total_litros, 2) if total_litros > 0 else 0

    return render(request, 'portal/vehiculos_admin_dashboard.html', {
        'unidades': unidades,
        'salidas_todas': salidas_todas,
        'cargas_todas': cargas_todas,
        'usuarios_pendientes': usuarios_pendientes,
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
    Permite al Administrador aprobar, desactivar o reactivar cuentas de usuario.
    """
    usuario = get_object_or_404(UsuarioOperadorVehiculo, id=usuario_id)
    
    if nuevo_estado in ['APROBADO', 'DESACTIVADO', 'RECHAZADO', 'PENDIENTE']:
        usuario.estado = nuevo_estado
        usuario.save()
        
        nombres_estado = {
            'APROBADO': '🟢 Aprobado / Activado',
            'DESACTIVADO': '🔴 Desactivado / Suspendido',
            'RECHAZADO': '❌ Rechazado',
            'PENDIENTE': '🕒 Pendiente'
        }
        messages.success(request, f"La cuenta de '{usuario.nombre_completo}' fue cambiada a {nombres_estado.get(nuevo_estado)}.")
    
    return redirect('admin_vehiculos_dashboard')


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
