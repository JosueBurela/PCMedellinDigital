import urllib.request
import json
import base64
import time
import os
import webbrowser
import sys

BASE_URL = 'http://localhost:8080'
APIKEY = 'MedellinPCSecretToken2026'
INSTANCE = 'PCHistorico'

def get_connection_state():
    try:
        req = urllib.request.Request(
            f'{BASE_URL}/instance/connectionState/{INSTANCE}',
            headers={'apikey': APIKEY}
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            return data.get('instance', {}).get('state', 'unknown')
    except Exception:
        return 'offline'

def fetch_and_save_qr():
    try:
        req = urllib.request.Request(
            f'{BASE_URL}/instance/connect/{INSTANCE}',
            headers={'apikey': APIKEY}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            b64_full = data.get('base64', '')
            if not b64_full:
                return False
            
            b64_clean = b64_full.split(',', 1)[1] if ',' in b64_full else b64_full
            
            # Guardar imagen PNG
            with open('qr_code.png', 'wb') as f:
                f.write(base64.b64decode(b64_clean))
            
            # Guardar página HTML que se autorefresca cada 15s si está abierta
            html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Vincular WhatsApp - Proteccion Civil</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: #0f172a;
      color: #f8fafc;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      margin: 0;
    }}
    .card {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 1.5rem;
      padding: 2rem;
      text-align: center;
      max-width: 420px;
      box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
    }}
    .badge {{
      display: inline-block;
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      font-size: 0.8rem;
      font-weight: 700;
      padding: 0.35rem 0.85rem;
      border-radius: 9999px;
      margin-bottom: 1rem;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }}
    h1 {{
      font-size: 1.4rem;
      margin: 0 0 0.5rem 0;
      color: #ffffff;
    }}
    p {{
      color: #94a3b8;
      font-size: 0.85rem;
      margin: 0 0 1.25rem 0;
      line-height: 1.4;
    }}
    .qr-box {{
      background: #ffffff;
      padding: 1rem;
      border-radius: 1rem;
      display: inline-block;
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }}
    img {{
      width: 270px;
      height: 270px;
      display: block;
    }}
    .footer {{
      margin-top: 1.25rem;
      font-size: 0.75rem;
      color: #64748b;
    }}
  </style>
</head>
<body>
  <div class="card">
    <div class="badge">&#10003; syncFullHistory: ACTIVADO (DESDE ENERO)</div>
    <h1>Escanear Codigo QR</h1>
    <p>En el telefono con el historial:<br><strong>WhatsApp &gt; Dispositivos vinculados &gt; Vincular un dispositivo</strong></p>
    <div class="qr-box">
      <img src="{b64_full}" alt="Codigo QR WhatsApp" />
    </div>
    <div class="footer">
      Esta ventana actualiza el codigo automaticamente.<br>Escanealo con la camara de WhatsApp.
    </div>
  </div>
</body>
</html>"""
            with open('ver_qr.html', 'w', encoding='utf-8') as f_html:
                f_html.write(html)
            
            return True
    except Exception as e:
        print(f"Error al obtener QR: {e}")
        return False

def main():
    print("=" * 60)
    print("   CONECTOR AUTOMATICO WHATSAPP - EVOLUTION API LOCAL")
    print("   Instancia: PCHistorico (Sincronizacion Completa)")
    print("=" * 60)
    print()

    # 1. Verificar estado inicial
    state = get_connection_state()
    if state == 'open':
        print("[OK] ¡WhatsApp YA ESTA CONECTADO y activo en la instancia!")
        print("No necesitas escanear nada. Ya podemos extraer los mensajes.")
        print()
        input("Presiona ENTER para cerrar esta ventana...")
        return

    print("[*] Generando codigo QR nuevo con syncFullHistory...")
    if not fetch_and_save_qr():
        print("[!] No se pudo generar el QR. Asegurate de que Docker este corriendo.")
        input("Presiona ENTER para salir...")
        return

    # 2. Abrir en el navegador
    html_path = os.path.abspath('ver_qr.html')
    print(f"[OK] Codigo QR generado exitosamente.")
    print(f"[*] Abriendo en tu navegador web...")
    webbrowser.open(f'file:///{html_path}')
    print()
    print("-> Escanea el codigo con WhatsApp:")
    print("   (WhatsApp > Tres puntos > Dispositivos vinculados > Vincular un dispositivo)")
    print()
    print("[*] Esperando a que lo escanees con el telefono...")
    print("    (El codigo se refrescara automaticamente cada 25s si expira)")
    print()

    intentos = 0
    segundos_transcurridos = 0
    while True:
        time.sleep(3)
        segundos_transcurridos += 3
        state = get_connection_state()

        if state == 'open':
            print()
            print("=" * 60)
            print("   [EXITO] ¡WHATSAPP VINCULADO Y CONECTADO EXITOSAMENTE! 🎉")
            print("=" * 60)
            print("Tu sesion ya esta abierta en la laptop.")
            print("Ahora podemos comenzar a extraer todos los mensajes y fotos.")
            print()
            input("Presiona ENTER para finalizar...")
            break

        # Si pasaron 25 segundos y no ha conectado, refrescar QR
        if segundos_transcurridos >= 25:
            intentos += 1
            print(f"[*] Refrescando codigo QR (intento {intentos})...")
            fetch_and_save_qr()
            segundos_transcurridos = 0

if __name__ == '__main__':
    main()
