# ==============================================================================
#  🏢 INTRANET ADMINISTRATIVA Y CONTROL DE FLOTILLA (ERP MUNICIPAL)
#  Secretaría de Protección Civil y Bomberos - Medellín de Bravo
#  Copyright (c) 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
# ==============================================================================

import json
import datetime
from datetime import timedelta
from functools import wraps

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Avg, Count
from django.http import JsonResponse, HttpResponse
from django.utils import timezone

from portal.models import (
    VehiculoUnidad,
    BitacoraSalidaVehiculo,
    RegistroCargaGasolina,
    Trabajador,
    ReporteRiesgo
)


# ==============================================================================
# 🔐 CONTROL DE ACCESO UNIFICADO DE INTRANET
# ==============================================================================

def requiere_intranet_admin(view_func):
    """
    Verifica que el usuario tenga sesión administrativa activa (Django Auth)
    o cuente con credenciales de Administrador / Validador en el sistema.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Por favor inicia sesión para acceder a la Intranet.")
            return redirect('login_unificado')

        # Si es staff o rol SUPER/VALIDADOR de PersonalAdministrativo
        rol_nivel = getattr(request.user, 'rol_nivel', '')
        if request.user.is_staff or rol_nivel in ['SUPER', 'VALIDADOR', 'DIRECTOR']:
            request.operador_actual = request.user
            return view_func(request, *args, **kwargs)

        # Si el usuario es un Trabajador con rol_vehicular de ADMIN o JEFE_GUARDIA
        if hasattr(request.user, 'rol_vehicular') and request.user.rol_vehicular in ['ADMIN', 'JEFE_GUARDIA']:
            request.operador_actual = request.user
            return view_func(request, *args, **kwargs)

        # Fallback a session si viene de operador móvil
        operador_id = request.session.get('operador_id')
        if operador_id:
            try:
                op = Trabajador.objects.get(id=operador_id, is_active=True)
                if op.rol_vehicular in ['ADMIN', 'JEFE_GUARDIA']:
                    request.operador_actual = op
                    return view_func(request, *args, **kwargs)
            except Trabajador.DoesNotExist:
                pass

        messages.error(request, "Acceso restringido: Se requieren permisos administrativos.")
        return redirect('intranet_hub')
    return _wrapped


# ==============================================================================
# 🏠 HUB PRINCIPAL DE LA INTRANET
# ==============================================================================

@login_required(login_url='login_unificado')
def intranet_hub(request):
    """
    Panel maestro (Hub) para administradores y personal de la intranet.
    Concentra accesos directos a todos los módulos y KPIs globales.
    """
    total_unidades = VehiculoUnidad.objects.count()
    unidades_disponibles = VehiculoUnidad.objects.filter(estatus='DISPONIBLE').count()
    unidades_en_servicio = VehiculoUnidad.objects.filter(estatus='EN_SERVICIO').count()

    return render(request, 'portal/intranet_hub.html', {
        'total_unidades': total_unidades,
        'unidades_disponibles': unidades_disponibles,
        'unidades_en_servicio': unidades_en_servicio,
    })


# ==============================================================================
# 🚑 CONTROL ADMINISTRATIVO DE FLOTILLA
# ==============================================================================

@requiere_intranet_admin
def intranet_flotilla_dashboard(request):
    """
    Panel unificado de Flotilla dentro de la Intranet.
    Gestión de unidades oficiales, bitácora de salidas, combustible y roles.
    """
    unidades = VehiculoUnidad.objects.all().order_by('numero_unidad', 'nombre_identificador')
    salidas_todas = BitacoraSalidaVehiculo.objects.all().select_related('unidad')
    cargas_todas = RegistroCargaGasolina.objects.all().select_related('unidad')

    usuarios_pendientes = Trabajador.objects.filter(rol_vehicular='NINGUNO')
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
        'usuarios_pendientes': usuarios_pendientes,
        'usuarios_activos': usuarios_activos,
        'usuarios_desactivados': usuarios_desactivados,
        'total_km': total_km,
        'total_litros': total_litros,
        'total_costo': total_costo,
        'rendimiento_promedio': rendimiento_promedio,
        'operador_actual': getattr(request, 'operador_actual', request.user),
    })


@requiere_intranet_admin
def intranet_crear_unidad(request):
    """
    Crea una nueva unidad de vehículo en la flotilla desde la Intranet.
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


@requiere_intranet_admin
def intranet_editar_unidad(request, unidad_id):
    """
    Edita una unidad existente o retorna sus datos en JSON para el modal.
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


@requiere_intranet_admin
def intranet_eliminar_unidad(request, unidad_id):
    """
    Elimina una unidad de la flotilla.
    """
    unidad = get_object_or_404(VehiculoUnidad, id=unidad_id)
    nombre = unidad.nombre_identificador
    unidad.delete()
    messages.success(request, f"Se eliminó la unidad '{nombre}' de la flotilla.")
    return redirect('admin_vehiculos_dashboard')


@requiere_intranet_admin
def intranet_historial_unidad(request, unidad_id):
    """
    Historial y antecedentes completos de una unidad específica.
    """
    unidad = get_object_or_404(VehiculoUnidad, id=unidad_id)
    salidas = BitacoraSalidaVehiculo.objects.filter(unidad=unidad).order_by('-fecha_salida')
    cargas = RegistroCargaGasolina.objects.filter(unidad=unidad).order_by('-fecha_carga')

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
        'operador_actual': getattr(request, 'operador_actual', request.user),
    })


@requiere_intranet_admin
def intranet_cambiar_estado_usuario(request, usuario_id, nuevo_estado):
    """
    Permite asignar un rol vehicular o desactivar a un Trabajador.
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


@requiere_intranet_admin
def intranet_reportes_jefe_selector(request):
    """
    Pantalla para configurar e imprimir el Reporte de Movimiento Vehicular (Jefe de Guardia).
    """
    unidades = VehiculoUnidad.objects.all().order_by('numero_unidad')
    return render(request, 'portal/vehiculos_reporte_selector.html', {
        'unidades': unidades,
        'operador_actual': getattr(request, 'operador_actual', request.user),
    })


@requiere_intranet_admin
def intranet_imprimir_reporte_movimiento(request):
    """
    Genera el formato HTML para el Reporte de Movimiento Vehicular (PDF).
    """
    unidad_id = request.GET.get('unidad_id')
    fecha_str = request.GET.get('fecha')
    turno = request.GET.get('turno', 'TURNO_1')
    formato = request.GET.get('formato', '1_turno')

    unidad = get_object_or_404(VehiculoUnidad, id=unidad_id)
    
    try:
        from datetime import datetime as dt_cls
        fecha_obj = dt_cls.strptime(fecha_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        fecha_obj = timezone.now().date()

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
        'operador_actual': getattr(request, 'operador_actual', request.user),
    }
    
    return render(request, 'portal/vehiculos_imprimir_reporte.html', context)


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


@requiere_intranet_admin
def intranet_historial_vehiculos(request):
    """
    Panel interactivo de consulta y filtro de bitácoras por fechas y unidades.
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
        'operador_actual': getattr(request, 'operador_actual', request.user),
        'fecha_emision': timezone.now()
    }

    return render(request, 'portal/vehiculos_historial_admin.html', context)


@requiere_intranet_admin
def intranet_imprimir_reporte_historial(request):
    """
    Renderiza la Hoja Oficial de Bitácora de Flotilla en orientación VERTICAL (Letter Portrait)
    con logos institucionales, metadatos, tablas de servicio y firmas oficiales.
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


# ==============================================================================
# 🔄 ALIASES DE RETROCOMPATIBILIDAD
# ==============================================================================
admin_vehiculos_dashboard = intranet_flotilla_dashboard
crear_unidad = intranet_crear_unidad
editar_unidad = intranet_editar_unidad
eliminar_unidad = intranet_eliminar_unidad
historial_unidad = intranet_historial_unidad
admin_historial_vehiculos = intranet_historial_vehiculos
imprimir_reporte_historial_vehicular = intranet_imprimir_reporte_historial
vista_impresion_reportes_jefe = intranet_reportes_jefe_selector
imprimir_reporte_movimiento_vehicular = intranet_imprimir_reporte_movimiento
cambiar_estado_usuario = intranet_cambiar_estado_usuario
