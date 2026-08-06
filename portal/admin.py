# ==============================================================================
#  🛡️ SISTEMA DIGITAL DE PROTECCIÓN CIVIL Y BOMBEROS
#  Copyright (c) 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
#  Desarrollado y Diseñado por: Josué Jaziel Delgado Burela
#  Contacto y Soporte: jburela1@gmal.com
# ==============================================================================

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import PersonalAdministrativo, Tramite, SolicitudTramite, ReporteRiesgo, Ciudadano, HistorialReporte, Localidad, ActividadGiro, Trabajador

# Registrar Trabajador
class TrabajadorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'categoria', 'creado_en')
    list_filter = ('categoria',)
    search_fields = ('nombre', 'telefono')

admin.site.register(Trabajador, TrabajadorAdmin)

admin.site.register(Localidad)

class ActividadGiroAdmin(admin.ModelAdmin):
    list_display = ('numero', 'actividad', 'riesgo')
    list_filter = ('riesgo',)
    search_fields = ('numero', 'actividad')

admin.site.register(ActividadGiro, ActividadGiroAdmin)

class PersonalAdministrativoAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Información Institucional', {'fields': ('area', 'rol_nivel', 'telefono_institucional')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Institucional', {
            'fields': ('area', 'rol_nivel', 'telefono_institucional'),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'area', 'rol_nivel', 'is_staff')
    list_filter = ('area', 'rol_nivel', 'is_staff', 'is_superuser', 'is_active')

admin.site.register(PersonalAdministrativo, PersonalAdministrativoAdmin)

class TramiteAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'area', 'icono', 'form_type', 'activo', 'creado_en')
    list_filter = ('area', 'form_type', 'activo')
    search_fields = ('titulo', 'descripcion')

admin.site.register(Tramite, TramiteAdmin)

class SolicitudTramiteAdmin(admin.ModelAdmin):
    list_display = ('establecimiento', 'tramite', 'rfc', 'estatus', 'creado_en')
    list_filter = ('estatus', 'tramite__area')
    search_fields = ('establecimiento', 'rfc')

admin.site.register(SolicitudTramite, SolicitudTramiteAdmin)

class ReporteRiesgoAdmin(admin.ModelAdmin):
    list_display = ('numero_reporte', 'nombre_ciudadano', 'tipo_servicio', 'prioridad', 'estatus', 'fecha_reporte')
    list_filter = ('estatus', 'tipo_servicio', 'prioridad')
    search_fields = ('numero_reporte', 'nombre_ciudadano', 'colonia')

admin.site.register(ReporteRiesgo, ReporteRiesgoAdmin)

class CiudadanoAdmin(admin.ModelAdmin):
    list_display = ('curp', 'nombre', 'primer_apellido', 'genero', 'estado_nacimiento', 'correo', 'telefono', 'creado_en')
    search_fields = ('curp', 'nombre', 'primer_apellido', 'correo')

admin.site.register(Ciudadano, CiudadanoAdmin)

class HistorialReporteAdmin(admin.ModelAdmin):
    list_display = ('reporte', 'creado_por', 'fecha_registro')
    search_fields = ('reporte__numero_reporte', 'comentario')

admin.site.register(HistorialReporte, HistorialReporteAdmin)
