# ==============================================================================
#  🛡️ SISTEMA DIGITAL DE PROTECCIÓN CIVIL Y BOMBEROS
#  Copyright (c) 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
#  Desarrollado y Diseñado por: Josué Jaziel Delgado Burela
#  Contacto y Soporte: jburela1@gmal.com
# ==============================================================================

from django.shortcuts import render
from portal.models import Tramite
from portal.utils.clima_utils import obtener_pronostico_veracruz

def seccion_tramites(request):
    """
    Retorna el fragmento HTML del catálogo de trámites bajo demanda (Lazy Loading).
    """
    tramites = Tramite.objects.filter(activo=True).order_by('id')
    return render(request, 'portal/partials/seccion_tramites.html', {
        'tramites': tramites
    })

def seccion_clima(request):
    """
    Retorna el fragmento HTML del informe meteorológico extendido bajo demanda (Lazy Loading).
    """
    pronostico_clima = obtener_pronostico_veracruz()
    return render(request, 'portal/partials/seccion_clima.html', {
        'pronostico_clima': pronostico_clima
    })
