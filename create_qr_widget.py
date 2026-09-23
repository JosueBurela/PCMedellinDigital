import json

data = json.load(open('qr_response.json'))
base64_str = data['base64']

html = f"""
<!DOCTYPE html>
<html>
<head>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
</head>
<body class="bg-transparent text-[var(--foreground)] antialiased p-5 flex justify-center">
  <div class="bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)] rounded-xl p-5 shadow-sm text-center">
    <h2 class="text-[var(--foreground)] font-semibold text-lg mb-2">Conectar WhatsApp a Protección Civil</h2>
    <p class="text-[var(--muted-foreground)] text-sm mb-4">Abre WhatsApp > Dispositivos vinculados > Vincular un dispositivo</p>
    <img src="{base64_str}" class="mx-auto" alt="Código QR" />
    <p class="text-[var(--muted-foreground)] text-xs mt-4">Escanea el código para sincronizar los mensajes nuevos.</p>
  </div>
</body>
</html>
"""
with open(r'C:\Users\burel\.gemini\antigravity\brain\9493526b-398a-43a1-994b-f8c77d11f9c5\qr_widget.html', 'w', encoding='utf-8') as f:
    f.write(html)
