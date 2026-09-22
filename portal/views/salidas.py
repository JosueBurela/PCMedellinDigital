# ==============================================================================
#  🚑 VISTAS DEL PANEL 'REGISTRO DE SALIDAS' (INTRANET PC MEDELLÍN)
#  Copyright (c) 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
# ==============================================================================

import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.contrib import messages
from django.db.models import Count, Avg, Q
from portal.models import VehiculoUnidad, BitacoraSalidaVehiculo
from portal.views.vehiculos import requiere_operador_aprobado


@requiere_operador_aprobado
def intranet_registro_salidas(request):
    """
    Panel de visualización y control diario del 'Registro de Salidas' de flotilla.
    Muestra las salidas sincronizadas automáticamente desde WhatsApp y permite
    filtrar por fecha, ver fotos del tablero, cerrar servicios y descargar el parte.
    """
    # 1. Filtro por fecha (default: Hoy)
    fecha_str = request.GET.get('fecha')
    hoy = timezone.localdate()
    
    if fecha_str:
        try:
            fecha_seleccionada = datetime.datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            fecha_seleccionada = hoy
    else:
        fecha_seleccionada = hoy

    # 2. Consultar salidas del día seleccionado
    salidas_dia = BitacoraSalidaVehiculo.objects.filter(
        fecha_salida__date=fecha_seleccionada
    ).select_related('unidad').order_by('-fecha_salida')

    # 3. Salidas actualmente activas / en curso (independiente de la fecha para el semáforo)
    salidas_activas = BitacoraSalidaVehiculo.objects.filter(
        completado=False
    ).select_related('unidad').order_by('-fecha_salida')

    # 4. Estado de todas las unidades de la flotilla
    unidades_flotilla = VehiculoUnidad.objects.all().order_by('numero_unidad')

    # 5. Métricas y estadísticas del día
    total_salidas = salidas_dia.count()
    completadas_dia = salidas_dia.filter(completado=True).count()
    activas_dia = salidas_dia.filter(completado=False).count()

    # Cálculo de duración promedio
    duraciones = [s.duracion_minutos for s in salidas_dia if s.duracion_minutos and s.duracion_minutos > 0]
    duracion_promedio = round(sum(duraciones) / len(duraciones)) if duraciones else 0

    # Unidades en servicio vs disponibles
    unidades_en_servicio_count = unidades_flotilla.filter(estatus='EN_SERVICIO').count()
    unidades_disponibles_count = unidades_flotilla.filter(estatus='DISPONIBLE').count()

    ayer = hoy - datetime.timedelta(days=1)

    context = {
        'fecha_seleccionada': fecha_seleccionada,
        'fecha_str': fecha_seleccionada.strftime('%Y-%m-%d'),
        'es_hoy': (fecha_seleccionada == hoy),
        'hoy_str': hoy.strftime('%Y-%m-%d'),
        'es_ayer': (fecha_seleccionada == ayer),
        'ayer_str': ayer.strftime('%Y-%m-%d'),
        'salidas': salidas_dia,
        'salidas_activas': salidas_activas,
        'unidades_flotilla': unidades_flotilla,
        'total_salidas': total_salidas,
        'completadas_dia': completadas_dia,
        'activas_dia': activas_dia,
        'duracion_promedio': duracion_promedio,
        'unidades_en_servicio_count': unidades_en_servicio_count,
        'unidades_disponibles_count': unidades_disponibles_count,
    }
    return render(request, 'portal/salidas_admin_dashboard.html', context)


@requiere_operador_aprobado
def api_cerrar_salida_manual(request, salida_id):
    """
    Permite cerrar manualmente una salida activa desde la web si el operador olvidó mandar el mensaje 'en base'.
    """
    salida = get_object_or_404(BitacoraSalidaVehiculo, id=salida_id)
    
    if request.method == 'POST':
        ahora = timezone.now()
        salida.fecha_llegada = ahora
        salida.duracion_minutos = max(1, int((ahora - salida.fecha_salida).total_seconds() / 60))
        salida.completado = True
        salida.save()

        # Liberar unidad
        unidad = salida.unidad
        unidad.estatus = 'DISPONIBLE'
        unidad.ultima_salida_finalizada = ahora
        unidad.save()

        messages.success(request, f"Se finalizó manualmente el servicio de la {unidad.nombre_identificador}.")
        return redirect(f"/intranet/salidas/?fecha={salida.fecha_salida.strftime('%Y-%m-%d')}")

    return redirect('intranet_registro_salidas')


@requiere_operador_aprobado
def api_crear_salida_manual(request):
    """
    Permite registrar una salida manualmente por si no había señal o el teléfono no envió el mensaje.
    """
    if request.method == 'POST':
        unidad_id = request.POST.get('unidad_id')
        operador = request.POST.get('operador_nombre', '').strip()
        motivo = request.POST.get('descripcion_servicio', '').strip()
        
        unidad = get_object_or_404(VehiculoUnidad, id=unidad_id)
        ahora = timezone.now()

        nueva_salida = BitacoraSalidaVehiculo.objects.create(
            unidad=unidad,
            operador_nombre=operador or "Registro Manual Intranet",
            descripcion_servicio=motivo or "Servicio operativo",
            fecha_salida=ahora,
            odometro_salida=unidad.odometro_actual or 0,
            gasolina_salida=unidad.nivel_gasolina_actual or 'Lleno',
            completado=False
        )

        unidad.estatus = 'EN_SERVICIO'
        unidad.save()

        messages.success(request, f"Salida de la {unidad.nombre_identificador} registrada correctamente.")
        return redirect('intranet_registro_salidas')

    return redirect('intranet_registro_salidas')


@requiere_operador_aprobado
def imprimir_reporte_salidas_pdf(request):
    """
    Genera una vista oficial imprimible (A4 / Carta) con formato institucional
    de Protección Civil Medellín de Bravo del 'Parte Diario de Salidas y Atenciones'.
    """
    fecha_str = request.GET.get('fecha')
    hoy = timezone.localdate()
    
    if fecha_str:
        try:
            fecha_obj = datetime.datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            fecha_obj = hoy
    else:
        fecha_obj = hoy

    salidas = BitacoraSalidaVehiculo.objects.filter(
        fecha_salida__date=fecha_obj
    ).select_related('unidad').order_by('fecha_salida')

    context = {
        'fecha': fecha_obj,
        'salidas': salidas,
        'total_servicios': salidas.count(),
        'hoy': hoy,
    }
    return render(request, 'portal/salidas_reporte_imprimible.html', context)
