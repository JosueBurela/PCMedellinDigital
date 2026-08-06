# ==============================================================================
#  🛡️ SISTEMA DIGITAL DE PROTECCIÓN CIVIL Y BOMBEROS
#  Copyright (c) 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
#  Desarrollado y Diseñado por: Josué Jaziel Delgado Burela
#  Contacto y Soporte: jburela1@gmal.com
# ==============================================================================

import logging
from django.shortcuts import redirect
from django.contrib import messages

logger = logging.getLogger(__name__)

class FaultIsolationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        path = request.path
        
        # 1. Aislamiento del módulo de Chat
        if 'chat' in path:
            logger.error(f"[FaultIsolation] Error crítico en el módulo de chat: {exception}", exc_info=True)
            messages.error(request, "El módulo de chat de seguimiento está temporalmente fuera de servicio, pero el registro de tus expedientes y reportes sigue operativo.")
            return redirect(request.META.get('HTTP_REFERER', 'home'))
            
        # 2. Aislamiento del módulo de Generación de Documentos (PDF/LaTeX)
        if 'latex' in path or 'imprimir' in path:
            logger.error(f"[FaultIsolation] Error en la generación física del documento: {exception}", exc_info=True)
            messages.error(request, "El generador de oficios e impresión experimenta dificultades técnicas en este momento, pero el expediente sigue registrado en la base de datos.")
            return redirect(request.META.get('HTTP_REFERER', 'dashboard_admin'))
            
        # 3. Aislamiento del módulo de Trámites (Creación/Eliminación)
        if 'tramites' in path:
            logger.error(f"[FaultIsolation] Error en la configuración de trámites: {exception}", exc_info=True)
            messages.error(request, "No se pudo completar la acción en los trámites. El módulo se encuentra en mantenimiento temporal.")
            return redirect('/panel/?seccion=tramites')
            
        # Permitir que los errores críticos (como auth o creación de reportes urgentes) sigan su flujo normal para ser detectados
        return None
