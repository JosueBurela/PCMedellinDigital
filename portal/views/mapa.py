# ==============================================================================
#  📍 MAPA GIS INTERACTIVO DE EMERGENCIAS Y FLOTILLA EN TIEMPO REAL
#  Copyright (c) 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
# ==============================================================================

from django.shortcuts import render, redirect
from django.http import JsonResponse
from portal.models import ReporteRiesgo, VehiculoUnidad
from portal.views.vehiculos import requiere_operador_aprobado, requiere_admin_flotilla


@requiere_operador_aprobado
def mapa_emergencias_hub(request):
    """
    Panel Ejecutivo de Mapa GIS de Emergencias y Flotilla en Tiempo Real.
    """
    return render(request, 'portal/mapa_emergencias.html', {
        'operador_actual': request.operador_actual
    })


def api_mapa_datos(request):
    """
    Endpoint JSON que retorna reportes de riesgo activos y unidades de flotilla con coordenadas GPS.
    """
    reportes_qs = ReporteRiesgo.objects.all().order_by('-fecha_reporte')[:100]
    unidades_qs = VehiculoUnidad.objects.all()

    reportes_data = []
    for r in reportes_qs:
        reportes_data.append({
            'id': r.id,
            'numero_reporte': r.numero_reporte,
            'tipo_servicio': r.tipo_servicio,
            'tipo_display': r.get_tipo_servicio_display(),
            'nombre_ciudadano': r.nombre_ciudadano,
            'telefono_ciudadano': r.telefono_ciudadano,
            'latitud': float(r.latitud) if r.latitud else None,
            'longitud': float(r.longitud) if r.longitud else None,
            'direccion': r.direccion,
            'colonia': r.colonia,
            'localidad': r.localidad,
            'descripcion': r.descripcion,
            'prioridad': r.prioridad,
            'estatus': r.estatus,
            'estatus_display': r.get_estatus_display(),
            'evidencia_url': r.evidencia_foto.url if r.evidencia_foto else None,
            'fecha': r.fecha_reporte.strftime("%d/%m/%Y %H:%i hrs")
        })

    unidades_data = []
    for u in unidades_qs:
        unidades_data.append({
            'id': u.id,
            'numero_unidad': u.numero_unidad,
            'nombre_identificador': u.nombre_identificador,
            'tipo_vehiculo': u.tipo_vehiculo,
            'tipo_display': u.get_tipo_vehiculo_display(),
            'estatus': u.estatus,
            'estatus_display': u.get_estatus_display(),
            'latitud_base': float(u.latitud_base) if u.latitud_base else 19.0558,
            'longitud_base': float(u.longitud_base) if u.longitud_base else -96.1558,
            'odometro_actual': u.odometro_actual,
            'nivel_gasolina_actual': u.nivel_gasolina_actual,
            'foto_url': u.foto_unidad.url if u.foto_unidad else None
        })

    return JsonResponse({
        'reportes': reportes_data,
        'unidades': unidades_data
    })
