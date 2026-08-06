# ==============================================================================
#  🛡️ SISTEMA DIGITAL DE PROTECCIÓN CIVIL Y BOMBEROS
#  Copyright (c) 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
#  Desarrollado y Diseñado por: Josué Jaziel Delgado Burela
#  Contacto y Soporte: jburela1@gmal.com
# ==============================================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from portal.models import PersonalAdministrativo, Ciudadano

import random
from datetime import timedelta
from django.utils import timezone

def login_administrativo(request):
    return redirect('login_unificado')

def login_ciudadano(request):
    return redirect('login_unificado')

def acceso_unificado(request):
    if request.user.is_authenticated:
        return redirect('dashboard_admin')
    if request.session.get('ciudadano_curp') or request.session.get('ciudadano_id'):
        return redirect('home')
        
    # Rate Limiting / Protección Antifraude
    intentos_fallidos = request.session.get('intentos_login', 0)
    if intentos_fallidos >= 5:
        messages.error(request, "⚠️ Por seguridad, se ha bloqueado temporalmente el acceso por múltiples intentos fallidos. Inténtalo de nuevo en unos momentos.")
        if request.method == 'POST':
            return render(request, 'portal/login_unificado.html')

    if request.method == 'POST':
        identificador = request.POST.get('identificador', '').strip()
        clave = request.POST.get('password', '').strip()
        
        if not identificador or not clave:
            messages.error(request, "Por favor, completa todos los campos obligatorios.")
        else:
            # 1. Intentar validar como Ciudadano por Correo o CURP
            ciudadano = Ciudadano.objects.filter(correo__iexact=identificador).first()
            if not ciudadano and len(identificador) == 18:
                ciudadano = Ciudadano.objects.filter(curp__iexact=identificador).first()

            if ciudadano and check_password(clave, ciudadano.password):
                from portal.utils.email_utils import enviar_correo_2fa
                # Generar Código de Verificación en 2 Pasos (2FA) de 6 dígitos
                codigo_2fa = str(random.randint(100000, 999999))
                ciudadano.codigo_2fa = codigo_2fa
                ciudadano.codigo_2fa_expiracion = timezone.now() + timedelta(minutes=5)
                ciudadano.save()

                request.session['pending_2fa_ciudadano_id'] = ciudadano.id
                request.session['intentos_login'] = 0
                
                # Intentar enviar por Correo SMTP Real
                enviado_email = enviar_correo_2fa(ciudadano, codigo_2fa)
                if enviado_email:
                    messages.success(request, f"🔒 Se ha enviado un código de verificación de 6 dígitos a tu correo: {ciudadano.correo}")
                else:
                    messages.info(request, f"🔒 Se ha generado tu código de seguridad en 2 pasos: {codigo_2fa}")
                return redirect('verificar_2fa')
            
            # 2. Intentar validar como Personal Administrativo / Operativo
            user = authenticate(request, username=identificador, password=clave)
            if user is not None:
                if not user.is_active:
                    messages.error(request, "Tu cuenta institucional está en revisión o inactiva por el Administrador General.")
                else:
                    login(request, user)
                    request.session['intentos_login'] = 0
                    messages.success(request, f"Sesión de personal iniciada: {user.first_name or user.username}.")
                    return redirect('dashboard_admin')
            else:
                request.session['intentos_login'] = intentos_fallidos + 1
                intentos_restantes = 5 - (intentos_fallidos + 1)
                if intentos_restantes > 0:
                    messages.error(request, f"Credenciales incorrectas. Te quedan {intentos_restantes} intento(s) antes del bloqueo temporal.")
                else:
                    messages.error(request, "⚠️ Múltiples intentos fallidos registrados. Acceso bloqueado por seguridad.")
                
    return render(request, 'portal/login_unificado.html')


def verificar_2fa(request):
    ciudadano_id = request.session.get('pending_2fa_ciudadano_id')
    if not ciudadano_id:
        messages.error(request, "Sesión de verificación no válida o expirada.")
        return redirect('login_unificado')
        
    ciudadano = get_object_or_404(Ciudadano, id=ciudadano_id)

    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo_2fa', '').strip()
        
        if ciudadano.codigo_2fa and ciudadano.codigo_2fa == codigo_ingresado:
            if ciudadano.codigo_2fa_expiracion and timezone.now() <= ciudadano.codigo_2fa_expiracion:
                # Éxito: Establecer sesión activa
                request.session['ciudadano_id'] = ciudadano.id
                request.session['ciudadano_curp'] = ciudadano.curp or ciudadano.correo
                if 'pending_2fa_ciudadano_id' in request.session:
                    del request.session['pending_2fa_ciudadano_id']
                ciudadano.codigo_2fa = None
                ciudadano.codigo_2fa_expiracion = None
                ciudadano.save()

                messages.success(request, f"¡Autenticación en 2 pasos completada! Bienvenido, {ciudadano.nombre}.")
                return redirect('home')
            else:
                messages.error(request, "El código de seguridad ha expirado. Por favor solicita uno nuevo.")
        else:
            messages.error(request, "Código de seguridad de 6 dígitos incorrecto.")

    return render(request, 'portal/verificar_2fa.html', {'ciudadano': ciudadano})


def reenviar_codigo_2fa(request):
    ciudadano_id = request.session.get('pending_2fa_ciudadano_id')
    if ciudadano_id:
        ciudadano = Ciudadano.objects.filter(id=ciudadano_id).first()
        if ciudadano:
            nuevo_codigo = str(random.randint(100000, 999999))
            ciudadano.codigo_2fa = nuevo_codigo
            ciudadano.codigo_2fa_expiracion = timezone.now() + timedelta(minutes=5)
            ciudadano.save()
            messages.info(request, f"🔒 Nuevo código de seguridad de 2 pasos generado: {nuevo_codigo}")
    return redirect('verificar_2fa')

def registro_personal(request):
    if request.user.is_authenticated:
        return redirect('dashboard_admin')
        
    if request.method == 'POST':
        usuario = request.POST.get('username')
        nombre = request.POST.get('first_name')
        apellido = request.POST.get('last_name')
        correo = request.POST.get('email')
        clave = request.POST.get('password')
        area = request.POST.get('area')
        rol = request.POST.get('rol_nivel')
        telefono = request.POST.get('telefono')
        
        # Validar si el usuario ya existe
        if PersonalAdministrativo.objects.filter(username=usuario).exists():
            messages.error(request, "El nombre de usuario ya está registrado.")
        elif PersonalAdministrativo.objects.filter(email=correo).exists():
            messages.error(request, "El correo electrónico ya está registrado.")
        else:
            nuevo_user = PersonalAdministrativo.objects.create_user(
                username=usuario,
                email=correo,
                password=clave,
                first_name=nombre,
                last_name=apellido,
                area=area,
                rol_nivel=rol,
                telefono_institucional=telefono,
                is_active=False  # Requiere aprobación del admin general
            )
            messages.success(request, "Registro exitoso. Tu cuenta está pendiente de aprobación por el Administrador General.")
            return redirect('login_unificado')
            
    return render(request, 'portal/registro.html')

def salir_ciudadano(request):
    for key in ['ciudadano_id', 'ciudadano_curp', 'pending_2fa_ciudadano_id']:
        if key in request.session:
            del request.session[key]
    request.session.flush()
    messages.success(request, "Sesión de ciudadano finalizada con éxito.")
    return redirect('home')

def logout_vista(request):
    logout(request)
    for key in ['ciudadano_id', 'ciudadano_curp', 'pending_2fa_ciudadano_id']:
        if key in request.session:
            del request.session[key]
    request.session.flush()
    messages.success(request, "Sesión finalizada.")
    return redirect('home')

@login_required(login_url='login_unificado')
def aprobar_personal(request, usuario_id):
    if request.user.rol_nivel != 'SUPER':
        messages.error(request, "Acceso denegado.")
        return redirect('dashboard_admin')
        
    usuario = get_object_or_404(PersonalAdministrativo, id=usuario_id)
    usuario.is_active = True
    usuario.save()
    messages.success(request, f"Se ha aprobado al usuario {usuario.username}.")
    return redirect('/panel/?seccion=personal')

@login_required(login_url='login_unificado')
def desactivar_personal(request, usuario_id):
    if request.user.rol_nivel != 'SUPER':
        messages.error(request, "Acceso denegado.")
        return redirect('dashboard_admin')
        
    usuario = get_object_or_404(PersonalAdministrativo, id=usuario_id)
    if usuario == request.user:
        messages.error(request, "No puedes desactivarte a ti mismo.")
        return redirect('/panel/?seccion=personal')
        
    usuario.is_active = False
    usuario.save()
    messages.success(request, f"Se ha desactivado al usuario {usuario.username}.")
    return redirect('/panel/?seccion=personal')

@login_required(login_url='login_unificado')
def eliminar_personal(request, usuario_id):
    if request.user.rol_nivel != 'SUPER':
        messages.error(request, "Acceso denegado.")
        return redirect('dashboard_admin')
        
    usuario = get_object_or_404(PersonalAdministrativo, id=usuario_id)
    if usuario == request.user:
        messages.error(request, "No puedes eliminarte a ti mismo.")
        return redirect('/panel/?seccion=personal')
        
    usuario.delete()
    messages.success(request, f"Se ha eliminado el registro de {usuario.username}.")
    return redirect('/panel/?seccion=personal')
