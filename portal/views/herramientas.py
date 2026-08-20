# ==============================================================================
#  🛡️ SUITE DE HERRAMIENTAS AUXILIARES Y APPS EXTERNAS
#  Copyright (c) 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
#  Desarrollado y Diseñado por: Josué Jaziel Delgado Burela
#  Contacto y Soporte: jburela1@gmail.com
# ==============================================================================

import json
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.utils import timezone

from portal.models import (
    ContactoDirectorio,
    OrdenInspeccion,
    ItemInspeccion,
    ConfiguracionInspeccion,
    FichaInformativa,
    VehiculoUnidad
)

def suite_herramientas_hub(request):
    """
    Menú principal / Hub de la Suite de Herramientas Auxiliares (Ruta Aislada).
    """
    herramientas = [
        {
            'id': 'directorio',
            'titulo': 'Directorio Telefónico y Tarjetas QR',
            'categoria': 'Comunicación y Contactos',
            'descripcion': 'Gestión de contactos oficiales, búsqueda rápida y generación de tarjetas digitales con código QR.',
            'icono': 'contact',
            'color': 'bg-blue-600',
            'badge': f"{ContactoDirectorio.objects.count()} Contactos",
            'url': '/herramientas-auxiliares/directorio/',
        },
        {
            'id': 'inspecciones',
            'titulo': 'Generador de Órdenes de Inspección',
            'categoria': 'Protección Civil & Comercio',
            'descripcion': 'Generación y control de órdenes de inspección por rutas, asignación de inspectores y exportación en PDF.',
            'icono': 'clipboard-check',
            'color': 'bg-purple-600',
            'badge': f"{OrdenInspeccion.objects.count()} Órdenes",
            'url': '/herramientas-auxiliares/inspecciones/',
        },
        {
            'id': 'fichas_informativas',
            'titulo': 'Generador de Fichas Informativas y Oficios',
            'categoria': 'Documentación & Administración',
            'descripcion': 'Redacción y emisión de oficios oficiales con membrete del Ayuntamiento 2026-2029 e impresión en PDF.',
            'icono': 'file-text',
            'color': 'bg-emerald-600',
            'badge': f"{FichaInformativa.objects.count()} Oficios",
            'url': '/herramientas-auxiliares/fichas-informativas/',
        },
        {
            'id': 'control_vehiculos',
            'titulo': 'Control de Vehículos y Bitácora Digital',
            'categoria': 'Operativo & Flotilla',
            'descripcion': 'Control de salidas de emergencias, registro de odómetro, tanque de gasolina, evidencia fotográfica y analítica de consumo.',
            'icono': 'truck',
            'color': 'bg-amber-600',
            'badge': f"{VehiculoUnidad.objects.count()} Unidades",
            'url': '/control-vehiculos/',
        }
    ]

    return render(request, 'portal/herramientas_hub.html', {
        'herramientas': herramientas
    })


def herramienta_directorio(request):
    """
    Vista del Módulo 1: Directorio Telefónico y Tarjetas de Contacto Digitales.
    """
    query = request.GET.get('q', '').strip()
    contactos = ContactoDirectorio.objects.all()

    if query:
        contactos = contactos.filter(
            Q(nombre__icontains=query) |
            Q(empresa__icontains=query) |
            Q(puesto__icontains=query) |
            Q(telefono__icontains=query) |
            Q(email__icontains=query)
        )

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        email = request.POST.get('email', '').strip()
        empresa = request.POST.get('empresa', '').strip()
        puesto = request.POST.get('puesto', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        web = request.POST.get('web', '').strip()
        foto = request.FILES.get('foto')

        if nombre and telefono:
            ContactoDirectorio.objects.create(
                nombre=nombre,
                telefono=telefono,
                email=email,
                empresa=empresa,
                puesto=puesto,
                direccion=direccion,
                web=web,
                foto=foto
            )
            messages.success(request, f"¡Contacto '{nombre}' agregado exitosamente al directorio!")
            return redirect('herramienta_directorio')
        else:
            messages.error(request, "El nombre y teléfono son obligatorios.")

    return render(request, 'portal/herramienta_directorio.html', {
        'contactos': contactos,
        'query': query,
    })


def eliminar_contacto_directorio(request, contacto_id):
    """
    Elimina un contacto del directorio.
    """
    contacto = get_object_or_404(ContactoDirectorio, id=contacto_id)
    nombre = contacto.nombre
    contacto.delete()
    messages.success(request, f"El contacto '{nombre}' fue eliminado del directorio.")
    return redirect('herramienta_directorio')


def herramienta_inspecciones(request):
    """
    Vista del Módulo 2: Generador de Órdenes de Inspección de Protección Civil.
    """
    tipo_filtro = request.GET.get('filtro', 'todas')
    hoy = datetime.date.today()
    
    ordenes = OrdenInspeccion.objects.all().prefetch_related('items')

    if tipo_filtro == 'hoy':
        ordenes = ordenes.filter(fecha_corta=hoy)
    elif tipo_filtro == 'semana':
        inicio_semana = hoy - datetime.timedelta(days=hoy.weekday())
        ordenes = ordenes.filter(fecha_corta__gte=inicio_semana)
    elif tipo_filtro == 'mes':
        inicio_mes = hoy.replace(day=1)
        ordenes = ordenes.filter(fecha_corta__gte=inicio_mes)
    elif tipo_filtro == 'bimestre':
        inicio_bimestre = hoy - datetime.timedelta(days=60)
        ordenes = ordenes.filter(fecha_corta__gte=inicio_bimestre)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'crear_orden':
            fecha_corta_str = request.POST.get('fecha_corta', hoy.strftime('%Y-%m-%d'))
            horario = request.POST.get('horario', 'De 10am A 2pm').strip()
            rutas_resumen = request.POST.get('rutas_resumen', '').strip()
            inspector = request.POST.get('inspector', '').strip()
            operador = request.POST.get('operador', '').strip()
            director = request.POST.get('director', 'L.E.D. DANIEL EDUARDO ROMERO PILAR').strip()

            # Formatear fecha_texto (ej. JUEVES 06/AGOSTO/26)
            try:
                fecha_obj = datetime.datetime.strptime(fecha_corta_str, '%Y-%m-%d').date()
            except ValueError:
                fecha_obj = hoy
            
            dias = ['LUNES', 'MARTES', 'MIÉRCOLES', 'JUEVES', 'VIERNES', 'SÁBADO', 'DOMINGO']
            meses = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']
            fecha_texto = f"{dias[fecha_obj.weekday()]} {fecha_obj.day:02d}/{meses[fecha_obj.month - 1]}/{str(fecha_obj.year)[-2:]}"

            if inspector and operador:
                orden = OrdenInspeccion.objects.create(
                    fecha_corta=fecha_obj,
                    fecha_texto=fecha_texto,
                    horario=horario,
                    rutas_resumen=rutas_resumen,
                    inspector=inspector,
                    operador=operador,
                    director=director,
                    estado='Pendiente'
                )

                # Procesar lista dinámica de ítems (rutas y establecimientos)
                rutas = request.POST.getlist('item_ruta')
                establecimientos = request.POST.getlist('item_establecimiento')
                meses_pago = request.POST.getlist('item_mes_pago')

                for idx, (rt, est, mp) in enumerate(zip(rutas, establecimientos, meses_pago), start=1):
                    if est.strip():
                        ItemInspeccion.objects.create(
                            orden=orden,
                            numero=idx,
                            ruta=rt.strip().upper(),
                            establecimiento=est.strip().upper(),
                            mes_pago=mp.strip().upper()
                        )

                messages.success(request, f"¡Orden de Inspección #{orden.id} creada con éxito con {orden.items.count()} establecimientos!")
                return redirect('herramienta_inspecciones')
            else:
                messages.error(request, "El Inspector y Operador son requeridos.")

        elif action == 'actualizar_estatus':
            item_id = request.POST.get('item_id')
            realizado = request.POST.get('realizado', '').strip()
            pendiente = request.POST.get('pendiente', '').strip()

            item = get_object_or_404(ItemInspeccion, id=item_id)
            item.realizado = realizado
            item.pendiente = pendiente
            item.save()

            # Si todos los ítems están marcados, cambiar estado de la orden
            orden = item.orden
            total_items = orden.items.count()
            completados = orden.items.exclude(realizado='').count()
            if completados == total_items and total_items > 0:
                orden.estado = 'Completado'
            elif completados > 0:
                orden.estado = 'En Proceso'
            orden.save()

            return JsonResponse({'status': 'ok', 'estado_orden': orden.estado})

    # Cargar catálogos por defecto para autocompletar
    config_dict = {cfg.key: cfg.value for cfg in ConfiguracionInspeccion.objects.all()}

    return render(request, 'portal/herramienta_inspecciones.html', {
        'ordenes': ordenes,
        'tipo_filtro': tipo_filtro,
        'hoy_str': hoy.strftime('%Y-%m-%d'),
        'config_dict': config_dict,
    })


def eliminar_orden_inspeccion(request, orden_id):
    """
    Elimina una orden de inspección.
    """
    orden = get_object_or_404(OrdenInspeccion, id=orden_id)
    orden.delete()
    messages.success(request, f"Se ha eliminado la Orden de Inspección #{orden_id}.")
    return redirect('herramienta_inspecciones')


def imprimir_orden_inspeccion(request, orden_id):
    """
    Renders la plantilla imprimible PDF oficial de la Orden de Inspección.
    """
    orden = get_object_or_404(OrdenInspeccion.objects.prefetch_related('items'), id=orden_id)
    return render(request, 'portal/imprimir_orden_inspeccion.html', {
        'orden': orden,
        'items': orden.items.all().order_by('numero')
    })


def herramienta_fichas_informativas(request):
    """
    Vista del Módulo 3: Generador de Fichas Informativas y Oficios Oficiales con Membrete.
    """
    fichas = FichaInformativa.objects.all()
    hoy = datetime.date.today()
    meses_es = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    lugar_fecha_defecto = f"{hoy.day} de {meses_es[hoy.month - 1]} de {hoy.year}"

    # Autogenerar correlativo de oficio
    count_hoy = FichaInformativa.objects.filter(creado_en__year=hoy.year).count() + 1
    num_oficio_defecto = f"MUNICIPIO MEDELLIN.PROCI.{count_hoy:04d}.{hoy.year}"

    if request.method == 'POST':
        tipo_documento = request.POST.get('tipo_documento', 'OFICIO').strip()
        num_oficio = request.POST.get('num_oficio', num_oficio_defecto).strip()
        asunto = request.POST.get('asunto', '').strip()
        lugar_fecha = request.POST.get('lugar_fecha', lugar_fecha_defecto).strip()
        
        hora_reporte = request.POST.get('hora_reporte', '').strip()
        hora_arribo = request.POST.get('hora_arribo', '').strip()
        lugar_hechos = request.POST.get('lugar_hechos', '').strip()

        destinatario_nombre = request.POST.get('destinatario_nombre', '').strip()
        destinatario_cargo = request.POST.get('destinatario_cargo', '').strip()
        destinatario_dependencia = request.POST.get('destinatario_dependencia', '').strip()
        atencion_nombre = request.POST.get('atencion_nombre', '').strip()
        atencion_cargo = request.POST.get('atencion_cargo', '').strip()
        
        cuerpo_texto = request.POST.get('cuerpo_texto', '').strip()
        firmante_nombre = request.POST.get('firmante_nombre', 'LIC. DANIEL EDUARDO ROMERO PILAR').strip()
        firmante_cargo = request.POST.get('firmante_cargo', 'TITULAR DE LA UNIDAD MUNICIPAL DE PROTECCIÓN CIVIL Y BOMBEROS DEL H. AYUNTAMIENTO MEDELLÍN DE BRAVO, VER.').strip()
        ccp_lineas = request.POST.get('ccp_lineas', '').strip()

        if asunto and cuerpo_texto:
            ficha = FichaInformativa.objects.create(
                tipo_documento=tipo_documento,
                num_oficio=num_oficio if tipo_documento == 'OFICIO' else '',
                asunto=asunto,
                lugar_fecha=lugar_fecha,
                hora_reporte=hora_reporte,
                hora_arribo=hora_arribo,
                lugar_hechos=lugar_hechos,
                destinatario_nombre=destinatario_nombre,
                destinatario_cargo=destinatario_cargo,
                destinatario_dependencia=destinatario_dependencia,
                atencion_nombre=atencion_nombre,
                atencion_cargo=atencion_cargo,
                cuerpo_texto=cuerpo_texto,
                firmante_nombre=firmante_nombre,
                firmante_cargo=firmante_cargo,
                ccp_lineas=ccp_lineas
            )
            doc_type_name = "Tarjeta Informativa" if tipo_documento == 'TARJETA_INFORMATIVA' else f"Oficio '{num_oficio}'"
            messages.success(request, f"¡{doc_type_name} generada y guardada exitosamente!")
            return redirect('imprimir_ficha_informativa', ficha_id=ficha.id)
        else:
            messages.error(request, "Por favor llena los campos requeridos (Asunto y Descripción de los Hechos / Cuerpo).")

    return render(request, 'portal/herramienta_fichas_informativas.html', {
        'fichas': fichas,
        'num_oficio_defecto': num_oficio_defecto,
        'lugar_fecha_defecto': lugar_fecha_defecto,
    })


def imprimir_ficha_informativa(request, ficha_id):
    """
    Renderiza la plantilla imprimible en PDF oficial de la Ficha Informativa / Oficio con Membrete.
    """
    ficha = get_object_or_404(FichaInformativa, id=ficha_id)
    ccp_list = [line.strip() for line in ficha.ccp_lineas.split('\n') if line.strip()]

    return render(request, 'portal/imprimir_ficha_informativa.html', {
        'ficha': ficha,
        'ccp_list': ccp_list
    })


def eliminar_ficha_informativa(request, ficha_id):
    """
    Elimina un registro de oficio / ficha informativa.
    """
    ficha = get_object_or_404(FichaInformativa, id=ficha_id)
    num_oficio = ficha.num_oficio or ficha.asunto
    ficha.delete()
    messages.success(request, f"Se eliminó el registro '{num_oficio}'.")
    return redirect('herramienta_fichas_informativas')


def editar_ficha_informativa(request, ficha_id):
    """
    Permite editar o actualizar una Ficha Informativa / Oficio existente.
    """
    ficha = get_object_or_404(FichaInformativa, id=ficha_id)

    if request.method == 'POST':
        ficha.tipo_documento = request.POST.get('tipo_documento', ficha.tipo_documento).strip()
        ficha.num_oficio = request.POST.get('num_oficio', ficha.num_oficio).strip()
        ficha.asunto = request.POST.get('asunto', ficha.asunto).strip()
        ficha.lugar_fecha = request.POST.get('lugar_fecha', ficha.lugar_fecha).strip()
        ficha.hora_reporte = request.POST.get('hora_reporte', '').strip()
        ficha.hora_arribo = request.POST.get('hora_arribo', '').strip()
        ficha.lugar_hechos = request.POST.get('lugar_hechos', '').strip()

        ficha.destinatario_nombre = request.POST.get('destinatario_nombre', '').strip()
        ficha.destinatario_cargo = request.POST.get('destinatario_cargo', '').strip()
        ficha.destinatario_dependencia = request.POST.get('destinatario_dependencia', '').strip()
        ficha.atencion_nombre = request.POST.get('atencion_nombre', '').strip()
        ficha.atencion_cargo = request.POST.get('atencion_cargo', '').strip()
        
        ficha.cuerpo_texto = request.POST.get('cuerpo_texto', '').strip()
        ficha.firmante_nombre = request.POST.get('firmante_nombre', 'LIC. DANIEL EDUARDO ROMERO PILAR').strip()
        ficha.firmante_cargo = request.POST.get('firmante_cargo', 'TITULAR DE LA UNIDAD MUNICIPAL DE PROTECCIÓN CIVIL Y BOMBEROS DEL H. AYUNTAMIENTO MEDELLÍN DE BRAVO, VER.').strip()
        ficha.ccp_lineas = request.POST.get('ccp_lineas', '').strip()

        ficha.save()

        messages.success(request, f"¡El documento '{ficha.asunto}' fue actualizado con éxito!")
        return redirect('imprimir_ficha_informativa', ficha_id=ficha.id)

    return JsonResponse({
        'id': ficha.id,
        'tipo_documento': ficha.tipo_documento,
        'num_oficio': ficha.num_oficio or '',
        'asunto': ficha.asunto or '',
        'lugar_fecha': ficha.lugar_fecha or '',
        'hora_reporte': ficha.hora_reporte or '',
        'hora_arribo': ficha.hora_arribo or '',
        'lugar_hechos': ficha.lugar_hechos or '',
        'destinatario_nombre': ficha.destinatario_nombre or '',
        'destinatario_cargo': ficha.destinatario_cargo or '',
        'destinatario_dependencia': ficha.destinatario_dependencia or '',
        'atencion_nombre': ficha.atencion_nombre or '',
        'atencion_cargo': ficha.atencion_cargo or '',
        'cuerpo_texto': ficha.cuerpo_texto or '',
        'firmante_nombre': ficha.firmante_nombre or '',
        'firmante_cargo': ficha.firmante_cargo or '',
        'ccp_lineas': ficha.ccp_lineas or '',
    })

