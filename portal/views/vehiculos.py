# ==============================================================================
#  🚑 CONTROL DE VEHÍCULOS Y BITÁCORA DIGITAL DE EMERGENCIAS
#  Copyright (c) 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
# ==============================================================================

import json
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum, Avg, Count
from django.http import JsonResponse, HttpResponse
from django.utils import timezone

from portal.models import (
    VehiculoUnidad,
    BitacoraSalidaVehiculo,
    RegistroCargaGasolina
)

def flotilla_vehiculos_hub(request):
    """
    Panel Principal de Flotilla y Bitácora Digital para Operadores.
    Muestra la lista de unidades con su estatus, fotos, odómetro y horas sin uso.
    """
    unidades = VehiculoUnidad.objects.all()
    salidas_activas = BitacoraSalidaVehiculo.objects.filter(completado=False).select_related('unidad')
    salidas_recientes = BitacoraSalidaVehiculo.objects.filter(completado=True).select_related('unidad')[:15]

    return render(request, 'portal/vehiculos_flotilla.html', {
        'unidades': unidades,
        'salidas_activas': salidas_activas,
        'salidas_recientes': salidas_recientes,
    })


def dar_salida_unidad(request, unidad_id):
    """
    Registra la SALIDA de un vehículo de emergencia (Odómetro inicial, Gasolina, Servicio, Foto).
    Cambia el estatus de la unidad a EN_SERVICIO (No disponible).
    """
    unidad = get_object_or_404(VehiculoUnidad, id=unidad_id)

    if unidad.estatus == 'EN_SERVICIO':
        messages.error(request, f"La unidad {unidad.nombre_identificador} ya se encuentra en servicio.")
        return redirect('flotilla_vehiculos_hub')

    if request.method == 'POST':
        operador_nombre = request.POST.get('operador_nombre', '').strip()
        guardia_turno = request.POST.get('guardia_turno', '').strip()
        descripcion_servicio = request.POST.get('descripcion_servicio', '').strip()
        odometro_salida = request.POST.get('odometro_salida', unidad.odometro_actual)
        gasolina_salida = request.POST.get('gasolina_salida', unidad.nivel_gasolina_actual)
        foto_odometro = request.FILES.get('foto_odometro_salida')

        try:
            odometro_salida_val = int(odometro_salida)
        except (ValueError, TypeError):
            odometro_salida_val = unidad.odometro_actual

        if operador_nombre and descripcion_servicio:
            salida = BitacoraSalidaVehiculo.objects.create(
                unidad=unidad,
                operador_nombre=operador_nombre,
                guardia_turno=guardia_turno,
                descripcion_servicio=descripcion_servicio,
                fecha_salida=timezone.now(),
                odometro_salida=odometro_salida_val,
                gasolina_salida=gasolina_salida,
                foto_odometro_salida=foto_odometro,
                completado=False
            )

            # Actualizar estado de la unidad a EN_SERVICIO
            unidad.estatus = 'EN_SERVICIO'
            unidad.odometro_actual = odometro_salida_val
            unidad.nivel_gasolina_actual = gasolina_salida
            unidad.save()

            messages.success(request, f"🚀 ¡Salida registrada para {unidad.nombre_identificador}! Estatus cambiado a EN SERVICIO.")
            return redirect('flotilla_vehiculos_hub')
        else:
            messages.error(request, "Por favor llena los campos requeridos (Operador y Descripción del Servicio).")

    return render(request, 'portal/vehiculos_dar_salida.html', {
        'unidad': unidad
    })


def registrar_retorno_unidad(request, bitacora_id):
    """
    Registra el RETORNO a base de una unidad en servicio.
    Calcula Kilómetros recorridos y cambia el estatus a DISPONIBLE.
    """
    bitacora = get_object_or_404(BitacoraSalidaVehiculo.objects.select_related('unidad'), id=bitacora_id)
    unidad = bitacora.unidad

    if request.method == 'POST':
        odometro_llegada = request.POST.get('odometro_llegada', unidad.odometro_actual)
        gasolina_llegada = request.POST.get('gasolina_llegada', unidad.nivel_gasolina_actual)
        foto_llegada = request.FILES.get('foto_odometro_llegada')

        try:
            odometro_llegada_val = int(odometro_llegada)
        except (ValueError, TypeError):
            odometro_llegada_val = bitacora.odometro_salida

        # Calcular Km Recorridos
        km_recorridos = max(0, odometro_llegada_val - bitacora.odometro_salida)
        
        # Calcular Duración en Minutos
        ahora = timezone.now()
        duracion_min = int((ahora - bitacora.fecha_salida).total_seconds() / 60)

        bitacora.fecha_llegada = ahora
        bitacora.odometro_llegada = odometro_llegada_val
        bitacora.gasolina_llegada = gasolina_llegada
        bitacora.foto_odometro_llegada = foto_llegada
        bitacora.km_recorridos = km_recorridos
        bitacora.duracion_minutos = duracion_min
        bitacora.completado = True
        bitacora.save()

        # Actualizar unidad a DISPONIBLE
        unidad.estatus = 'DISPONIBLE'
        unidad.odometro_actual = odometro_llegada_val
        unidad.nivel_gasolina_actual = gasolina_llegada
        unidad.ultima_salida_finalizada = ahora
        unidad.save()

        messages.success(request, f"🏁 ¡Retorno de {unidad.nombre_identificador} registrado con éxito! Recorrió {km_recorridos} km.")
        return redirect('flotilla_vehiculos_hub')

    return render(request, 'portal/vehiculos_registrar_retorno.html', {
        'bitacora': bitacora,
        'unidad': unidad
    })


def registrar_carga_gasolina(request, unidad_id):
    """
    Registra un ticket/recibo de carga de gasolina o diésel para una unidad.
    """
    unidad = get_object_or_404(VehiculoUnidad, id=unidad_id)

    if request.method == 'POST':
        operador = request.POST.get('operador', '').strip()
        litros = request.POST.get('litros_cargados', '0')
        costo = request.POST.get('costo_total', '0')
        odometro = request.POST.get('odometro_al_cargar', unidad.odometro_actual)
        foto_ticket = request.FILES.get('foto_ticket_o_bomba')
        notas = request.POST.get('notas', '').strip()

        try:
            litros_val = float(litros)
            costo_val = float(costo)
            odometro_val = int(odometro)
        except ValueError:
            litros_val = 0.0
            costo_val = 0.0
            odometro_val = unidad.odometro_actual

        if operador and litros_val > 0:
            RegistroCargaGasolina.objects.create(
                unidad=unidad,
                operador=operador,
                fecha_carga=timezone.now(),
                litros_cargados=litros_val,
                costo_total=costo_val,
                odometro_al_cargar=odometro_val,
                foto_ticket_o_bomba=foto_ticket,
                notas=notas
            )

            # Actualizar nivel de gasolina de la unidad a Lleno
            unidad.nivel_gasolina_actual = 'Lleno'
            unidad.odometro_actual = max(unidad.odometro_actual, odometro_val)
            unidad.save()

            messages.success(request, f"⛽ Carga de combustible registrada para {unidad.nombre_identificador}: {litros_val}L (${costo_val} MXN).")
            return redirect('flotilla_vehiculos_hub')
        else:
            messages.error(request, "Por favor ingresa los datos válidos de litros e importe.")

    return render(request, 'portal/vehiculos_carga_gasolina.html', {
        'unidad': unidad
    })


def admin_vehiculos_dashboard(request):
    """
    Panel de Administrador y Análisis Operativo de Flotilla.
    Bitácora digital histórica, consumo de gasolina y reportes.
    """
    unidades = VehiculoUnidad.objects.all()
    salidas_todas = BitacoraSalidaVehiculo.objects.all().select_related('unidad')
    cargas_todas = RegistroCargaGasolina.objects.all().select_related('unidad')

    # Métricas generales
    total_km = salidas_todas.aggregate(Sum('km_recorridos'))['km_recorridos__sum'] or 0
    total_litros = cargas_todas.aggregate(Sum('litros_cargados'))['litros_cargados__sum'] or 0
    total_costo = cargas_todas.aggregate(Sum('costo_total'))['costo_total__sum'] or 0
    rendimiento_promedio = round(total_km / total_litros, 2) if total_litros > 0 else 0

    return render(request, 'portal/vehiculos_admin_dashboard.html', {
        'unidades': unidades,
        'salidas_todas': salidas_todas,
        'cargas_todas': cargas_todas,
        'total_km': total_km,
        'total_litros': total_litros,
        'total_costo': total_costo,
        'rendimiento_promedio': rendimiento_promedio,
    })


def crear_unidad(request):
    """
    Crea una nueva unidad de vehículo en la flotilla.
    """
    if request.method == 'POST':
        numero_unidad = request.POST.get('numero_unidad', '').strip()
        nombre_identificador = request.POST.get('nombre_identificador', '').strip()
        tipo_vehiculo = request.POST.get('tipo_vehiculo', 'Ambulancia').strip()
        placas = request.POST.get('placas', '').strip()
        odometro_actual = request.POST.get('odometro_actual', '0')
        nivel_gasolina_actual = request.POST.get('nivel_gasolina_actual', 'Lleno').strip()
        foto_unidad = request.FILES.get('foto_unidad')

        try:
            odometro_val = int(odometro_actual)
        except ValueError:
            odometro_val = 0

        if numero_unidad and nombre_identificador:
            if VehiculoUnidad.objects.filter(numero_unidad=numero_unidad).exists():
                messages.error(request, f"Ya existe una unidad registrada con el número '{numero_unidad}'.")
            else:
                unidad = VehiculoUnidad.objects.create(
                    numero_unidad=numero_unidad,
                    nombre_identificador=nombre_identificador,
                    tipo_vehiculo=tipo_vehiculo,
                    placas=placas,
                    odometro_actual=odometro_val,
                    nivel_gasolina_actual=nivel_gasolina_actual,
                    foto_unidad=foto_unidad,
                    estatus='DISPONIBLE'
                )
                messages.success(request, f"¡Unidad '{unidad.nombre_identificador}' agregada con éxito a la flotilla!")
        else:
            messages.error(request, "Por favor completa el número de unidad y el nombre identificador.")

    return redirect('admin_vehiculos_dashboard')


def editar_unidad(request, unidad_id):
    """
    Edita una unidad existente o retorna sus datos en JSON.
    """
    unidad = get_object_or_404(VehiculoUnidad, id=unidad_id)

    if request.method == 'POST':
        unidad.numero_unidad = request.POST.get('numero_unidad', unidad.numero_unidad).strip()
        unidad.nombre_identificador = request.POST.get('nombre_identificador', unidad.nombre_identificador).strip()
        unidad.tipo_vehiculo = request.POST.get('tipo_vehiculo', unidad.tipo_vehiculo).strip()
        unidad.placas = request.POST.get('placas', '').strip()
        unidad.estatus = request.POST.get('estatus', unidad.estatus).strip()
        
        try:
            unidad.odometro_actual = int(request.POST.get('odometro_actual', unidad.odometro_actual))
        except ValueError:
            pass

        unidad.nivel_gasolina_actual = request.POST.get('nivel_gasolina_actual', unidad.nivel_gasolina_actual).strip()
        
        if request.FILES.get('foto_unidad'):
            unidad.foto_unidad = request.FILES.get('foto_unidad')

        unidad.save()
        messages.success(request, f"¡Unidad '{unidad.nombre_identificador}' actualizada con éxito!")
        return redirect('admin_vehiculos_dashboard')

    return JsonResponse({
        'id': unidad.id,
        'numero_unidad': unidad.numero_unidad,
        'nombre_identificador': unidad.nombre_identificador,
        'tipo_vehiculo': unidad.tipo_vehiculo,
        'placas': unidad.placas or '',
        'estatus': unidad.estatus,
        'odometro_actual': unidad.odometro_actual,
        'nivel_gasolina_actual': unidad.nivel_gasolina_actual,
        'foto_url': unidad.foto_unidad.url if unidad.foto_unidad else ''
    })


def eliminar_unidad(request, unidad_id):
    """
    Elimina una unidad de la flotilla.
    """
    unidad = get_object_or_404(VehiculoUnidad, id=unidad_id)
    nombre = unidad.nombre_identificador
    unidad.delete()
    messages.success(request, f"Se eliminó la unidad '{nombre}' de la flotilla.")
    return redirect('admin_vehiculos_dashboard')
