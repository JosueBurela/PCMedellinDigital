# ==============================================================================
#  🛡️ SISTEMA DIGITAL DE PROTECCIÓN CIVIL Y BOMBEROS
#  Copyright (c) 2026 Josué Jaziel Delgado Burela. Todos los derechos reservados.
#  Desarrollado y Diseñado por: Josué Jaziel Delgado Burela
#  Contacto y Soporte: jburela1@gmal.com
# ==============================================================================

import logging
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

logger = logging.getLogger(__name__)

def enviar_correo_2fa(ciudadano, codigo_2fa):
    """
    Envía el código de verificación OTP de 2 Pasos al correo electrónico del ciudadano.
    Envía versión HTML institucional y texto plano de respaldo.
    Retorna True si el correo se envió correctamente vía SMTP, o False si falla o no está configurado.
    """
    asunto = f"🔒 {codigo_2fa} es tu código de verificación - Protección Civil Medellín"
    
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

    mensaje_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Código de Verificación - Protección Civil Medellín</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #334155;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #f1f5f9; padding: 30px 10px;">
        <tr>
            <td align="center">
                <table role="presentation" width="100%" max-width="520" cellspacing="0" cellpadding="0" border="0" style="max-width: 520px; background-color: #ffffff; border-radius: 20px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                    <!-- Cabecera Institucional Vino/Oro -->
                    <tr>
                        <td style="background-color: #5A123E; padding: 28px 24px; text-align: center; border-bottom: 4px solid #E59E27;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 18px; font-weight: 800; letter-spacing: 0.5px; text-transform: uppercase;">
                                Protección Civil y Bomberos
                            </h1>
                            <p style="color: #fbcfe8; margin: 6px 0 0 0; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
                                Medellín de Bravo, Veracruz
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Cuerpo del Correo -->
                    <tr>
                        <td style="padding: 32px 28px;">
                            <h2 style="color: #0f172a; font-size: 18px; font-weight: 800; margin: 0 0 12px 0;">
                                Verificación de Seguridad en 2 Pasos
                            </h2>
                            <p style="font-size: 13px; line-height: 1.6; color: #475569; margin: 0 0 24px 0;">
                                Hola <strong>{ciudadano.nombre}</strong>,<br>
                                Se ha solicitado una acción de acceso o registro en el <strong>Portal Digital de Trámites</strong>. Para autenticar tu identidad, ingresa el siguiente código de 6 dígitos:
                            </p>
                            
                            <!-- Caja del Código OTP -->
                            <div style="background-color: #f8fafc; border: 2px dashed #cbd5e1; border-radius: 14px; padding: 20px; text-align: center; margin-bottom: 24px;">
                                <span style="display: block; font-size: 11px; font-weight: 800; color: #64748b; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px;">
                                    Código de Verificación Temporal
                                </span>
                                <div style="font-size: 36px; font-weight: 900; color: #5A123E; letter-spacing: 10px; font-family: monospace;">
                                    {codigo_2fa}
                                </div>
                                <span style="display: block; font-size: 11px; color: #dc2626; font-weight: 600; margin-top: 8px;">
                                    ⏱ Válido únicamente por 5 minutos
                                </span>
                            </div>
                            
                            <!-- Nota de Seguridad -->
                            <div style="background-color: #fffbeb; border-left: 4px solid #f59e0b; padding: 12px 14px; border-radius: 8px; margin-bottom: 24px;">
                                <p style="margin: 0; font-size: 11px; color: #92400e; line-height: 1.5;">
                                    <strong>Aviso de Confidencialidad:</strong> Ningún funcionario o elemento operativo de Protección Civil te solicitará este código. Es estrictamente personal.
                                </p>
                            </div>
                            
                            <p style="font-size: 12px; color: #94a3b8; margin: 0; line-height: 1.5;">
                                Si tú no iniciaste este trámite o no solicitaste este código, puedes hacer caso omiso de este mensaje; tu cuenta permanecerá segura.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Pie de Página Oficial -->
                    <tr>
                        <td style="background-color: #f8fafc; padding: 18px 24px; text-align: center; border-top: 1px solid #e2e8f0;">
                            <p style="margin: 0; font-size: 10px; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                H. Ayuntamiento de Medellín de Bravo • Ejercicio Fiscal 2026
                            </p>
                            <p style="margin: 4px 0 0 0; font-size: 10px; color: #94a3b8;">
                                Sistema Digital de Gestión Integral de Riesgos y Protección Civil
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

    try:
        email_user = getattr(settings, 'EMAIL_HOST_USER', None)
        email_pass = getattr(settings, 'EMAIL_HOST_PASSWORD', None)

        if not email_user or not email_pass:
            logger.warning("EMAIL_HOST_USER o EMAIL_HOST_PASSWORD no están configurados en settings.")
            print("⚠️ [EMAIL 2FA] SMTP no configurado (EMAIL_HOST_USER vacío). Mostrando código en pantalla de respaldo.")
            return False

        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', email_user)

        email = EmailMultiAlternatives(
            subject=asunto,
            body=mensaje_texto,
            from_email=from_email,
            to=[ciudadano.correo]
        )
        email.attach_alternative(mensaje_html, "text/html")
        sent_count = email.send(fail_silently=False)
        logger.info(f"Correo 2FA enviado exitosamente a {ciudadano.correo}")
        return sent_count > 0

    except Exception as e:
        logger.error(f"Error enviando correo SMTP a {ciudadano.correo}: {e}", exc_info=True)
        print(f"⚠️ [EMAIL 2FA] Error enviando correo SMTP a {ciudadano.correo}: {e}")
        return False
