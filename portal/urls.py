# ==============================================================================
#  🛡️ SISTEMA DIGITAL DE PROTECCIÓN CIVIL Y BOMBEROS
#  Copyright (c) 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
#  Desarrollado y Diseñado por: Josué Jaziel Delgado Burela
#  Contacto y Soporte: jburela1@gmal.com
# ==============================================================================

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin-login/', views.login_administrativo, name='login_admin'),
    path('acceso-ciudadano/', views.login_ciudadano, name='login_ciudadano'),
    path('login/', views.acceso_unificado, name='login_unificado'),
    path('verificar-2fa/', views.verificar_2fa, name='verificar_2fa'),
    path('reenviar-2fa/', views.reenviar_codigo_2fa, name='reenviar_codigo_2fa'),
    path('panel/', views.dashboard_admin, name='dashboard_admin'),
    path('logout/', views.logout_vista, name='logout'),
    
    # Registro de personal
    path('registro-personal/', views.registro_personal, name='registro_personal'),
    
    # Acceso ciudadano (Correo, Contraseña Cifrada y 2FA)
    path('registro-ciudadano/', views.registro_ciudadano, name='registro_ciudadano'),
    path('salir-ciudadano/', views.salir_ciudadano, name='salir_ciudadano'),
    
    # Solicitudes de Trámites (Ciudadanos)
    path('iniciar-tramite/<int:tramite_id>/', views.iniciar_tramite, name='iniciar_tramite'),
    
    # Acciones de Validación de Expedientes (Solo SUPER / VALIDADOR)
    path('panel/solicitud/aprobar/<int:solicitud_id>/', views.aprobar_solicitud, name='aprobar_solicitud'),
    path('panel/solicitud/rechazar/<int:solicitud_id>/', views.rechazar_solicitud, name='rechazar_solicitud'),
    path('panel/solicitud/<int:solicitud_id>/latex/', views.descargar_solicitud_latex, name='descargar_solicitud_latex'),
    path('panel/solicitud/<int:solicitud_id>/imprimir/', views.imprimir_solicitud_oficio, name='imprimir_solicitud_oficio'),
    
    # Reportes de Riesgo (Ciudadanos)
    path('crear-reporte/', views.crear_reporte, name='crear_reporte'),
    path('consultar-reporte/', views.consultar_reporte, name='consultar_reporte'),
    
    # Gestión de Reportes de Emergencia (Solo SUPER / VALIDADOR / CAPTURISTA)
    path('panel/reporte/asignar/<int:reporte_id>/', views.asignar_reporte, name='asignar_reporte'),
    path('panel/reporte/bitacora/<int:reporte_id>/', views.agregar_bitacora, name='agregar_bitacora'),
    
    # Gestión de Personal (Solo SUPER)
    path('panel/personal/aprobar/<int:usuario_id>/', views.aprobar_personal, name='aprobar_personal'),
    path('panel/personal/desactivar/<int:usuario_id>/', views.desactivar_personal, name='desactivar_personal'),
    path('panel/personal/eliminar/<int:usuario_id>/', views.eliminar_personal, name='eliminar_personal'),
    
    # Gestión de Trabajadores de Emergencia (SUPER / VALIDADOR / CAPTURISTA)
    path('panel/trabajadores/crear/', views.crear_trabajador, name='crear_trabajador'),
    path('panel/trabajadores/eliminar/<int:trabajador_id>/', views.eliminar_trabajador, name='eliminar_trabajador'),
    path('panel/trabajadores/asignar-turno/<int:trabajador_id>/<str:turno>/', views.asignar_turno, name='asignar_turno'),

    # Gestión de Plantillas de Guardia (24 Horas) y Calendario Mensual
    path('panel/plantillas/crear/', views.crear_plantilla_guardia, name='crear_plantilla_guardia'),
    path('panel/plantillas/editar/<int:plantilla_id>/', views.editar_plantilla_guardia, name='editar_plantilla_guardia'),
    path('panel/plantillas/eliminar/<int:plantilla_id>/', views.eliminar_plantilla_guardia, name='eliminar_plantilla_guardia'),
    path('panel/guardia/programar/', views.programar_guardia_calendario, name='programar_guardia_calendario'),
    path('panel/guardia/eliminar/<int:programacion_id>/', views.eliminar_programacion_guardia, name='eliminar_programacion_guardia'),
    path('api/trabajadores/calendario/', views.api_programacion_calendario, name='api_programacion_calendario'),

    # Módulo Aislado / Secundario: Rol Operativo de Guardias y Almacenamiento de Hojas Firmadas
    path('control-operativo-guardias/', views.control_operativo_guardias, name='control_operativo_guardias'),
    path('control-operativo-guardias/guardar-configuracion/', views.guardar_configuracion_guardia, name='guardar_configuracion_guardia'),
    path('control-operativo-guardias/imprimir-pdf/', views.imprimir_rol_guardia_pdf, name='imprimir_rol_guardia_pdf'),
    path('control-operativo-guardias/subir/', views.subir_rol_guardia_firmado, name='subir_rol_guardia_firmado'),
    path('control-operativo-guardias/eliminar/<int:rol_id>/', views.eliminar_rol_guardia_firmado, name='eliminar_rol_guardia_firmado'),

    # Módulo Aislado / Secundario: Suite de Herramientas Auxiliares y Apps Externas
    path('herramientas-auxiliares/', views.suite_herramientas_hub, name='suite_herramientas_hub'),
    path('herramientas-auxiliares/directorio/', views.herramienta_directorio, name='herramienta_directorio'),
    path('herramientas-auxiliares/directorio/eliminar/<int:contacto_id>/', views.eliminar_contacto_directorio, name='eliminar_contacto_directorio'),
    path('herramientas-auxiliares/inspecciones/', views.herramienta_inspecciones, name='herramienta_inspecciones'),
    path('herramientas-auxiliares/inspecciones/eliminar/<int:orden_id>/', views.eliminar_orden_inspeccion, name='eliminar_orden_inspeccion'),
    path('herramientas-auxiliares/inspecciones/imprimir/<int:orden_id>/', views.imprimir_orden_inspeccion, name='imprimir_orden_inspeccion'),

    # Módulo 3: Generador de Fichas Informativas y Oficios Oficiales con Membrete
    path('herramientas-auxiliares/fichas-informativas/', views.herramienta_fichas_informativas, name='herramienta_fichas_informativas'),
    path('herramientas-auxiliares/fichas-informativas/imprimir/<int:ficha_id>/', views.imprimir_ficha_informativa, name='imprimir_ficha_informativa'),
    path('herramientas-auxiliares/fichas-informativas/editar/<int:ficha_id>/', views.editar_ficha_informativa, name='editar_ficha_informativa'),
    path('herramientas-auxiliares/fichas-informativas/eliminar/<int:ficha_id>/', views.eliminar_ficha_informativa, name='eliminar_ficha_informativa'),

    # Módulo 4: Control Operativo de Vehículos y Bitácora Digital de Emergencias
    path('control-vehiculos/', views.flotilla_vehiculos_hub, name='flotilla_vehiculos_hub'),
    path('control-vehiculos/registro/', views.registro_operador, name='registro_operador'),
    path('control-vehiculos/login/', views.login_operador, name='login_operador'),
    path('control-vehiculos/logout/', views.logout_operador, name='logout_operador'),
    path('control-vehiculos/salida/<int:unidad_id>/', views.dar_salida_unidad, name='dar_salida_unidad'),
    path('control-vehiculos/retorno/<int:bitacora_id>/', views.registrar_retorno_unidad, name='registrar_retorno_unidad'),
    path('control-vehiculos/gasolina/<int:unidad_id>/', views.registrar_carga_gasolina, name='registrar_carga_gasolina'),
    path('control-vehiculos/admin/', views.admin_vehiculos_dashboard, name='admin_vehiculos_dashboard'),
    path('control-vehiculos/admin/unidad/crear/', views.crear_unidad, name='crear_unidad'),
    path('control-vehiculos/admin/unidad/editar/<int:unidad_id>/', views.editar_unidad, name='editar_unidad'),
    path('control-vehiculos/admin/unidad/eliminar/<int:unidad_id>/', views.eliminar_unidad, name='eliminar_unidad'),
    path('control-vehiculos/admin/unidad/historial/<int:unidad_id>/', views.historial_unidad, name='historial_unidad'),
    path('control-vehiculos/mapa/', views.mapa_emergencias_hub, name='mapa_emergencias_hub'),
    path('control-vehiculos/reporte/estado/<int:reporte_id>/<str:nuevo_estatus>/', views.cambiar_estado_reporte_operativo, name='cambiar_estado_reporte_operativo'),
    path('control-vehiculos/reportes/importar-chat/', views.importar_chat_whatsapp_web, name='importar_chat_whatsapp_web'),
    path('api/mapa-datos/', views.api_mapa_datos, name='api_mapa_datos'),
    path('control-vehiculos/admin/usuario/estado/<int:usuario_id>/<str:nuevo_estado>/', views.cambiar_estado_usuario, name='cambiar_estado_usuario'),

    # Módulo de Capacitaciones y Emisión Automatizada de Constancias
    path('capacitaciones/', views.registro_capacitacion_publico, name='registro_capacitacion_publico'),
    path('capacitaciones/mis-constancias/', views.buscar_mis_constancias, name='buscar_mis_constancias'),
    path('capacitaciones/qr-registro/', views.generar_qr_registro_con_logo, name='generar_qr_registro_con_logo'),
    path('capacitaciones/admin/', views.admin_capacitaciones_dashboard, name='admin_capacitaciones_dashboard'),
    path('capacitaciones/admin/curso/crear/', views.crear_curso_admin, name='crear_curso_admin'),
    path('capacitaciones/admin/asistencia/<int:inscripcion_id>/', views.marcar_asistencia_capacitacion, name='marcar_asistencia_capacitacion'),
    path('capacitaciones/admin/exportar/<int:curso_id>/', views.exportar_capacitados_excel, name='exportar_capacitados_excel'),
    path('capacitaciones/constancia/<str:folio>/', views.imprimir_constancia_pdf, name='imprimir_constancia_pdf'),
    path('capacitaciones/validar/<uuid:token>/', views.validar_constancia_qr, name='validar_constancia_qr'),

    # Perfil Ciudadano e Historial
    path('perfil/', views.perfil_ciudadano, name='perfil_ciudadano'),
    path('chat/enviar/', views.enviar_mensaje_chat, name='enviar_mensaje_chat'),
    
    # Webhook de WhatsApp
    path('api/whatsapp/webhook/', views.whatsapp_webhook, name='whatsapp_webhook'),
    
    # API de Cintillo de Avisos SMN CONAGUA
    path('api/clima/cintillo/', views.api_cintillo_clima, name='api_cintillo_clima'),
    
    # Endpoints Lazy Loading para Secciones Asíncronas
    path('api/seccion/tramites/', views.seccion_tramites, name='seccion_tramites'),
    path('api/seccion/clima/', views.seccion_clima, name='seccion_clima'),
]
