# ==============================================================================
#  🛡️ SISTEMA DIGITAL DE PROTECCIÓN CIVIL Y BOMBEROS
#  Copyright (c) 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
#  Desarrollado y Diseñado por: Josué Jaziel Delgado Burela
#  Contacto y Soporte: jburela1@gmal.com
# ==============================================================================

from django.core.mail import send_mail
from django.conf import settings

def enviar_correo_2fa(ciudadano, codigo_2fa):
    """
    Envía el código de verificación OTP de 2 Pasos al correo electrónico del ciudadano.
    Retorna True si el correo se envió correctamente vía SMTP, o False si no está configurado SMTP.
    """
    asunto = "🔒 Código de Verificación de Seguridad - Protección Civil Medellín"
    
    mensaje_texto = f"""Hola {ciudadano.nombre},

Bienvenido al Portal Digital de Protección Civil y Bomberos del Municipio de Medellín de Bravo, Veracruz.

Tu código de verificación de 2 Pasos (2FA) para autenticar tu correo electrónico es:

   ▶  {codigo_2fa}  ◀

Este código es estrictamente personal y confidencial. Expira en 5 minutos.
Si no solicitaste este acceso, por favor ignora este mensaje.

Atentamente,
Dirección Municipal de Protección Civil y Bomberos
H. Ayuntamiento de Medellín de Bravo, Veracruz.
"""

    try:
        email_user = getattr(settings, 'EMAIL_HOST_USER', None)
        if email_user:
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', email_user)
            sent_count = send_mail(
                subject=asunto,
                message=mensaje_texto,
                from_email=from_email,
                recipient_list=[ciudadano.correo],
                fail_silently=True
            )
            return sent_count > 0
    except Exception as e:
        print(f"⚠️ Error enviando correo SMTP a {ciudadano.correo}: {e}")
    
    return False
