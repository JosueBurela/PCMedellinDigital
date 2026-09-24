import re

with open('portal/views/salidas.py', 'r', encoding='utf-8') as f:
    content = f.read()

tv_view = """
def intranet_registro_salidas_tv(request):
    # TV loop version
    fecha_str = request.GET.get('fecha')
    hoy = timezone.localdate()
    
    if fecha_str:
        try:
            fecha_seleccionada = datetime.datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            fecha_seleccionada = hoy
    else:
        fecha_seleccionada = hoy

    salidas = BitacoraSalidaVehiculo.objects.filter(
        fecha_salida__date=fecha_seleccionada
    ).order_by('-fecha_salida')

    unidades_flotilla = VehiculoUnidad.objects.exclude(estatus='TALLER').order_by('numero_unidad')
    unidades_disponibles_count = unidades_flotilla.filter(estatus='DISPONIBLE').count()
    unidades_en_servicio_count = unidades_flotilla.filter(estatus='EN_SERVICIO').count()

    total_salidas = salidas.count()
    activas_dia = salidas.filter(completado=False).count()
    completadas_dia = salidas.filter(completado=True).count()
    
    promedio_minutos = salidas.filter(completado=True).aggregate(Avg('duracion_minutos'))['duracion_minutos__avg'] or 0
    duracion_promedio = int(promedio_minutos)

    ayer = hoy - datetime.timedelta(days=1)

    context = {
        'fecha_seleccionada': fecha_seleccionada,
        'fecha_str': fecha_seleccionada.strftime('%Y-%m-%d'),
        'hoy_str': hoy.strftime('%Y-%m-%d'),
        'ayer_str': ayer.strftime('%Y-%m-%d'),
        'es_hoy': fecha_seleccionada == hoy,
        'es_ayer': fecha_seleccionada == ayer,

        'salidas': salidas,
        
        'unidades_flotilla': unidades_flotilla,
        'unidades_disponibles_count': unidades_disponibles_count,
        'unidades_en_servicio_count': unidades_en_servicio_count,

        'total_salidas': total_salidas,
        'activas_dia': activas_dia,
        'completadas_dia': completadas_dia,
        'duracion_promedio': duracion_promedio,
    }
    
    return render(request, 'portal/salidas_tv_dashboard.html', context)
"""

if "intranet_registro_salidas_tv" not in content:
    content += "\n" + tv_view
    with open('portal/views/salidas.py', 'w', encoding='utf-8') as f:
        f.write(content)
