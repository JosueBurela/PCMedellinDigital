# ==============================================================================
#  🛡️ SISTEMA DIGITAL DE PROTECCIÓN CIVIL Y BOMBEROS
#  Copyright (c) 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
#  Desarrollado y Diseñado por: Josué Jaziel Delgado Burela
#  Contacto y Soporte: jburela1@gmal.com
# ==============================================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import datetime

from portal.models import Trabajador, PlantillaGuardia, ProgramacionGuardia, PersonalAdministrativo

@login_required(login_url='login_unificado')
def crear_plantilla_guardia(request):
    if request.user.rol_nivel not in ['SUPER', 'VALIDADOR', 'CAPTURISTA']:
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('dashboard_admin')

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        jornada_tipo = request.POST.get('jornada_tipo', '24H').strip()
        color = request.POST.get('color', '#5A123E').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        trabajadores_ids = request.POST.getlist('trabajadores')

        if nombre:
            plantilla = PlantillaGuardia.objects.create(
                nombre=nombre,
                jornada_tipo=jornada_tipo,
                color=color,
                descripcion=descripcion
            )
            if trabajadores_ids:
                plantilla.trabajadores.set(trabajadores_ids)
            messages.success(request, f"¡Plantilla '{plantilla.nombre}' creada con éxito con {plantilla.trabajadores.count()} elementos!")
        else:
            messages.error(request, "El nombre de la plantilla es obligatorio.")

    return redirect('/panel/?seccion=trabajadores')


@login_required(login_url='login_unificado')
def editar_plantilla_guardia(request, plantilla_id):
    if request.user.rol_nivel not in ['SUPER', 'VALIDADOR', 'CAPTURISTA']:
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('dashboard_admin')

    plantilla = get_object_or_404(PlantillaGuardia, id=plantilla_id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        jornada_tipo = request.POST.get('jornada_tipo', '24H').strip()
        color = request.POST.get('color', '#5A123E').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        trabajadores_ids = request.POST.getlist('trabajadores')

        if nombre:
            plantilla.nombre = nombre
            plantilla.jornada_tipo = jornada_tipo
            plantilla.color = color
            plantilla.descripcion = descripcion
            plantilla.save()

            plantilla.trabajadores.set(trabajadores_ids)
            messages.success(request, f"¡Plantilla '{plantilla.nombre}' actualizada exitosamente!")
        else:
            messages.error(request, "El nombre de la plantilla no puede estar vacío.")

    return redirect('/panel/?seccion=trabajadores')


@login_required(login_url='login_unificado')
def eliminar_plantilla_guardia(request, plantilla_id):
    if request.user.rol_nivel not in ['SUPER', 'VALIDADOR']:
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('dashboard_admin')

    plantilla = get_object_or_404(PlantillaGuardia, id=plantilla_id)
    nombre = plantilla.nombre
    plantilla.delete()
    messages.success(request, f"La plantilla '{nombre}' ha sido eliminada.")
    return redirect('/panel/?seccion=trabajadores')


@login_required(login_url='login_unificado')
def programar_guardia_calendario(request):
    if request.user.rol_nivel not in ['SUPER', 'VALIDADOR', 'CAPTURISTA']:
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('dashboard_admin')

    if request.method == 'POST':
        fecha_str = request.POST.get('fecha', '').strip()
        plantilla_id = request.POST.get('plantilla_id')
        notas = request.POST.get('notas', '').strip()

        if fecha_str and plantilla_id:
            try:
                fecha_obj = datetime.datetime.strptime(fecha_str, '%Y-%m-%d').date()
                plantilla = get_object_or_404(PlantillaGuardia, id=plantilla_id)

                programacion, created = ProgramacionGuardia.objects.update_or_create(
                    fecha=fecha_obj,
                    defaults={
                        'plantilla': plantilla,
                        'notas': notas,
                        'creado_por': request.user
                    }
                )
                action_text = "programada" if created else "actualizada"
                messages.success(request, f"¡Guardia {action_text} para el {fecha_obj.strftime('%d/%m/%Y')}: {plantilla.nombre}!")
            except Exception as e:
                messages.error(request, f"Error al programar la fecha: {e}")
        else:
            messages.error(request, "Debes seleccionar una fecha y una plantilla de guardia.")

    return redirect('/panel/?seccion=trabajadores')


@login_required(login_url='login_unificado')
def eliminar_programacion_guardia(request, programacion_id):
    if request.user.rol_nivel not in ['SUPER', 'VALIDADOR']:
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('dashboard_admin')

    prog = get_object_or_404(ProgramacionGuardia, id=programacion_id)
    fecha_text = prog.fecha.strftime('%d/%m/%Y')
    prog.delete()
    messages.success(request, f"Se ha removido la guardia programada para el {fecha_text}.")
    return redirect('/panel/?seccion=trabajadores')


@login_required(login_url='login_unificado')
def api_programacion_calendario(request):
    """
    Retorna en JSON todas las guardias programadas para el mes y año solicitado.
    """
    hoy = datetime.date.today()
    anio = int(request.GET.get('anio', hoy.year))
    mes = int(request.GET.get('mes', hoy.month))

    programaciones = ProgramacionGuardia.objects.filter(
        fecha__year=anio,
        fecha__month=mes
    ).select_related('plantilla').prefetch_related('plantilla__trabajadores')

    eventos = []
    for p in programaciones:
        trabajadores_list = [
            {
                'id': t.id,
                'nombre': t.nombre,
                'categoria': t.get_categoria_display(),
                'telefono': t.telefono
            }
            for t in p.plantilla.trabajadores.all()
        ]
        eventos.append({
            'id': p.id,
            'fecha': p.fecha.strftime('%Y-%m-%d'),
            'plantilla_id': p.plantilla.id,
            'plantilla_nombre': p.plantilla.nombre,
            'jornada_tipo': p.plantilla.get_jornada_tipo_display(),
            'color': p.plantilla.color,
            'notas': p.notas or '',
            'trabajadores': trabajadores_list,
            'total_elementos': len(trabajadores_list)
        })

    return JsonResponse({
        'anio': anio,
        'mes': mes,
        'programaciones': eventos
    })


from portal.models import RolGuardiaFirmado

import json

def control_operativo_guardias(request):
    """
    Vista aislada / secundaria para el Rol Operativo de Guardias:
    - Generador de hoja interactiva e imprimible PDF.
    - Calendario interactivo con visor de documento firmado y formato original.
    - Carga de imágenes/PDFs de la hoja firmada.
    """
    roles_firmados = RolGuardiaFirmado.objects.all().order_by('-fecha_periodo', '-creado_en')
    hoy = datetime.date.today()
    hoy_str = hoy.strftime('%Y-%m-%d')

    roles_list = []
    for r in roles_firmados:
        roles_list.append({
            'id': r.id,
            'fecha': r.fecha_periodo.strftime('%Y-%m-%d'),
            'guardia_tipo': r.guardia_tipo,
            'guardia_tipo_display': r.get_guardia_tipo_display(),
            'comandante': r.comandante_nombre or '',
            'observaciones': r.observaciones_novedades or '',
            'url': r.imagen_documento_firmado.url if r.imagen_documento_firmado else '',
        })

    return render(request, 'portal/imprimir_rol_guardia.html', {
        'roles_firmados': roles_firmados,
        'roles_json': json.dumps(roles_list),
        'hoy_str': hoy_str,
    })


def subir_rol_guardia_firmado(request):
    """
    Procesa la subida de una hoja de rol de guardia firmada (imágen o PDF).
    """
    if request.method == 'POST':
        fecha = request.POST.get('fecha_periodo')
        guardia_tipo = request.POST.get('guardia_tipo', 'GENERAL')
        comandante = request.POST.get('comandante_nombre', '').strip()
        observaciones = request.POST.get('observaciones_novedades', '').strip()
        archivo = request.FILES.get('imagen_documento_firmado')

        if fecha and archivo:
            usuario_staff = request.user if request.user.is_authenticated else None
            RolGuardiaFirmado.objects.create(
                fecha_periodo=fecha,
                guardia_tipo=guardia_tipo,
                comandante_nombre=comandante,
                observaciones_novedades=observaciones,
                imagen_documento_firmado=archivo,
                subido_por=usuario_staff
            )
            messages.success(request, f"¡Hoja de Rol Firmada registrada exitosamente para la fecha {fecha}!")
        else:
            messages.error(request, "Por favor selecciona la fecha y adjunta la imagen o PDF firmado.")

    return redirect('control_operativo_guardias')


def eliminar_rol_guardia_firmado(request, rol_id):
    """
    Elimina un registro de rol de guardia firmado.
    """
    rol = get_object_or_404(RolGuardiaFirmado, id=rol_id)
    fecha_text = rol.fecha_periodo.strftime('%d/%m/%Y')
    rol.delete()
    messages.success(request, f"Se eliminó el registro de rol firmado del {fecha_text}.")
    return redirect('control_operativo_guardias')

