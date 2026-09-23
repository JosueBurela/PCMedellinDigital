import urllib.request
import json
import time

BASE_URL = 'http://localhost:8080'
APIKEY = 'MedellinPCSecretToken2026'

# 1. Update settings to syncFullHistory: true
try:
    req = urllib.request.Request(
        f'{BASE_URL}/settings/set/PCMedellin',
        headers={'apikey': APIKEY, 'Content-Type': 'application/json'},
        data=json.dumps({'syncFullHistory': True}).encode(),
        method='POST'
    )
    with urllib.request.urlopen(req) as resp:
        print('Settings updated:', resp.read().decode())
except Exception as e:
    print('Error setting settings:', e)

# 2. Logout old session
try:
    req = urllib.request.Request(
        f'{BASE_URL}/instance/logout/PCMedellin',
        headers={'apikey': APIKEY},
        method='DELETE'
    )
    with urllib.request.urlopen(req) as resp:
        print('Logout response:', resp.read().decode())
except Exception as e:
    print('Logout info:', e)

time.sleep(2)

# 3. Connect to get QR code
try:
    req = urllib.request.Request(
        f'{BASE_URL}/instance/connect/PCMedellin',
        headers={'apikey': APIKEY}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print('Connect response received!')
        with open('qr_response.json', 'w') as f:
            json.dump(data, f)
        
        base64_str = data.get('base64', '')
        
        html = """<!DOCTYPE html>
<html>
<head>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
</head>
<body class="bg-transparent text-[var(--foreground)] antialiased p-5 flex justify-center">
  <div class="bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)] rounded-xl p-6 shadow-md text-center max-w-sm">
    <h2 class="text-[var(--foreground)] font-bold text-lg mb-1">Conectar WhatsApp - Historial Completo</h2>
    <p class="text-[var(--muted-foreground)] text-xs mb-4">Abre WhatsApp > Dispositivos vinculados > Vincular un dispositivo</p>
    <div class="bg-white p-3 rounded-lg inline-block shadow">
      <img src="{QR_IMAGE}" class="w-64 h-64 mx-auto" alt="Código QR WhatsApp" />
    </div>
    <div class="mt-4 p-2 bg-emerald-50 border border-emerald-200 rounded text-emerald-800 text-xs font-semibold">
      ✓ syncFullHistory activado (Historial desde Enero)
    </div>
    <p class="text-[var(--muted-foreground)] text-xs mt-2">Escanea este código con el teléfono que tiene todos los chats.</p>
  </div>
</body>
</html>""".replace("{QR_IMAGE}", base64_str)
        
        artifact_path = r'C:\Users\burel\.gemini\antigravity\brain\9493526b-398a-43a1-994b-f8c77d11f9c5\qr_widget.html'
        with open(artifact_path, 'w', encoding='utf-8') as f_art:
            f_art.write(html)
        print('Widget saved successfully to:', artifact_path)
except Exception as e:
    print('Error getting QR:', e)
