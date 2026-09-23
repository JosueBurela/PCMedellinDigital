import json
import base64

data = json.load(open('qr_pchistorico.json'))
base64_data = data['qrcode']['base64']

if ',' in base64_data:
    pure_b64 = base64_data.split(',', 1)[1]
else:
    pure_b64 = base64_data

artifact_png = r'C:\Users\burel\.gemini\antigravity\brain\9493526b-398a-43a1-994b-f8c77d11f9c5\qr_code.png'
with open(artifact_png, 'wb') as f:
    f.write(base64.b64decode(pure_b64))

with open('qr_code.png', 'wb') as f:
    f.write(base64.b64decode(pure_b64))

html_content = """<!DOCTYPE html>
<html>
<head>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
</head>
<body class="bg-transparent text-[var(--foreground)] antialiased p-4 flex justify-center">
  <div class="bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)] rounded-2xl p-6 shadow-xl text-center max-w-sm">
    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-600 text-xs font-semibold mb-3">
      <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
      syncFullHistory: ACTIVADO
    </div>
    <h2 class="text-[var(--foreground)] font-bold text-xl mb-1">Escanear Código QR</h2>
    <p class="text-[var(--muted-foreground)] text-xs mb-4">
      En tu teléfono: <strong>WhatsApp > Dispositivos vinculados > Vincular un dispositivo</strong>
    </p>
    <div class="bg-white p-4 rounded-xl inline-block shadow-sm border border-slate-100">
      <img src="{QR_IMAGE}" class="w-64 h-64 mx-auto" alt="Código QR WhatsApp" />
    </div>
    <p class="text-[var(--muted-foreground)] text-xs mt-3">
      Al escanearlo, WhatsApp transferirá todo el historial desde el 1 de enero a tu laptop.
    </p>
  </div>
</body>
</html>""".replace("{QR_IMAGE}", base64_data)

artifact_html = r'C:\Users\burel\.gemini\antigravity\brain\9493526b-398a-43a1-994b-f8c77d11f9c5\qr_widget.html'
with open(artifact_html, 'w', encoding='utf-8') as f:
    f.write(html_content)

print("QR code saved successfully!")
