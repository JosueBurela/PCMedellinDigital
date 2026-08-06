# ==============================================================================
#  🛡️ SISTEMA DIGITAL DE PROTECCIÓN CIVIL Y BOMBEROS
#  Copyright (c) 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
#  Desarrollado y Diseñado por: Josué Jaziel Delgado Burela
#  Contacto y Soporte: jburela1@gmal.com
# ==============================================================================

from django.db.models import Count
from datetime import datetime, timedelta
import collections
from portal.models import ReporteRiesgo, PersonalAdministrativo

def obtener_datos_analiticas(request, contexto):
    reportes_qs = ReporteRiesgo.objects.all()
    contexto['total_reportes'] = reportes_qs.count()
    contexto['reportes_pendientes_count'] = reportes_qs.filter(estatus='PENDIENTE').count()
    contexto['reportes_en_proceso_count'] = reportes_qs.filter(estatus='EN_PROCESO').count()
    contexto['reportes_resueltos_count'] = reportes_qs.filter(estatus='RESUELTO').count()
    
    # Agrupaciones temporales para Gráfico de Tendencias (Diario, Semanal, Mensual)
    reportes_ordenados = reportes_qs.order_by('fecha_reporte')
    hoy = datetime.now().date()
    
    # 1. Diario (últimos 30 días)
    diario_counts = collections.OrderedDict()
    for i in range(29, -1, -1):
        d = hoy - timedelta(days=i)
        day_str = d.strftime('%d %b')
        diario_counts[day_str] = 0
        
    # 2. Semanal (últimas 8 semanas)
    semanal_counts = collections.OrderedDict()
    for i in range(7, -1, -1):
        start_date = hoy - timedelta(days=hoy.weekday(), weeks=i)
        sem_str = f"Sem {start_date.strftime('%W')}"
        semanal_counts[sem_str] = 0
        
    # 3. Mensual (últimos 6 meses)
    mensual_counts = collections.OrderedDict()
    meses_nombres = {
        1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
    }
    for i in range(5, -1, -1):
        m_year = hoy.year
        m_month = hoy.month - i
        while m_month <= 0:
            m_month += 12
            m_year -= 1
        mes_str = f"{meses_nombres[m_month]} {str(m_year)[2:]}"
        mensual_counts[mes_str] = 0
        
    for r in reportes_ordenados:
        r_date = r.fecha_reporte.date()
        
        # Clasificar Diario
        day_key = r_date.strftime('%d %b')
        if day_key in diario_counts:
            diario_counts[day_key] += 1
            
        # Clasificar Semanal
        sem_key = f"Sem {r_date.strftime('%W')}"
        if sem_key in semanal_counts:
            semanal_counts[sem_key] += 1
            
        # Clasificar Mensual
        mes_key = f"{meses_nombres[r_date.month]} {str(r_date.year)[2:]}"
        if mes_key in mensual_counts:
            mensual_counts[mes_key] += 1
            
    contexto['trend_diario_labels'] = list(diario_counts.keys())
    contexto['trend_diario_counts'] = list(diario_counts.values())
    
    contexto['trend_semanal_labels'] = list(semanal_counts.keys())
    contexto['trend_semanal_counts'] = list(semanal_counts.values())
    
    contexto['trend_mensual_labels'] = list(mensual_counts.keys())
    contexto['trend_mensual_counts'] = list(mensual_counts.values())

    # Agrupación por tipo de incidente
    tipos_incidente = reportes_qs.values('tipo_servicio').annotate(total=Count('id')).order_by('-total')
    choices_dict = dict(ReporteRiesgo.SERVICIO_CHOICES)
    contexto['chart_tipos_labels'] = [choices_dict.get(item['tipo_servicio'], item['tipo_servicio']) for item in tipos_incidente]
    contexto['chart_tipos_data'] = [item['total'] for item in tipos_incidente]
    
    # Agrupación por colonia (Hotspots)
    colonias_hotspots = reportes_qs.values('colonia').annotate(total=Count('id')).order_by('-total')[:10]
    contexto['chart_colonias_labels'] = [item['colonia'] or 'No especificada' for item in colonias_hotspots]
    contexto['chart_colonias_data'] = [item['total'] for item in colonias_hotspots]

    # Obtener la colonia con más reportes
    zona_mas_caliente = "Ninguna"
    max_reportes = 0
    if colonias_hotspots:
        zona_mas_caliente = colonias_hotspots[0]['colonia'] or 'No especificada'
        max_reportes = colonias_hotspots[0]['total']
    contexto['zona_mas_caliente'] = zona_mas_caliente
    contexto['max_reportes'] = max_reportes

