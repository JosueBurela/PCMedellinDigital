import os
import re

with open('portal/templates/portal/salidas_admin_dashboard.html', 'r', encoding='utf-8') as f:
    admin_html = f.read()

# Replace extends and block page_title
tv_html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TV Base - PC Medellin</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script>
      tailwind.config = {
        theme: {
          extend: {
            colors: {
              medellinVino: '#5d1140',
              medellinOro: '#d4af37'
            }
          }
        }
      }
    </script>
</head>
<body class="bg-slate-50 text-slate-800 p-4">
"""

# Extract the content block
match = re.search(r'{% block content %}(.*?){% endblock %}', admin_html, re.DOTALL)
if match:
    content = match.group(1)
    
    # Insert radar before semaphore
    radar_html = """
  <!-- RADAR Y MONITOREO METEOROLOGICO CONAGUA (Mantiene la TV encendida) -->
  <div class="bg-slate-900 rounded-3xl p-4 shadow-xl border border-slate-800 overflow-hidden relative mt-6 mb-6">
    <div class="absolute top-6 left-6 z-10 flex items-center gap-2 bg-black/60 backdrop-blur px-3 py-1.5 rounded-lg border border-white/10 pointer-events-none">
      <span class="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse shadow-[0_0_8px_rgba(239,68,68,0.8)]"></span>
      <span class="text-white text-xs font-bold uppercase tracking-wider">Radar en Vivo SIPROC</span>
    </div>
    <iframe src="https://smn.conagua.gob.mx/tools/GUI/SIPROC/" class="w-full h-[500px] border-0 rounded-2xl filter contrast-125" loading="lazy"></iframe>
  </div>
"""
    content = re.sub(r'<!-- SEM(.*?)FORO EN VIVO DE FLOTILLA -->', radar_html + r'\n  <!-- SEM\1FORO EN VIVO DE FLOTILLA -->', content)
    
    # We remove the "Salida Manual" button from TV
    content = re.sub(r'<button type="button" onclick="abrirModalManual\(\)".*?</button>', '', content, flags=re.DOTALL)
    
    tv_html += content

# Extract the scripts block
scripts_match = re.search(r'{% block extra_scripts %}(.*?){% endblock %}', admin_html, re.DOTALL)
if scripts_match:
    scripts = scripts_match.group(1)
    
    # Append WakeLock script
    wakelock = """
// ==========================================
// WAKE LOCK API PARA EVITAR QUE LA TV SE APAGUE
// ==========================================
let wakeLock = null;
const requestWakeLock = async () => {
    try {
        if ('wakeLock' in navigator) {
            wakeLock = await navigator.wakeLock.request('screen');
            console.log('Wake Lock is active! La pantalla no se suspendera.');
        }
    } catch (err) {
        console.error('WakeLock error');
    }
};

document.addEventListener('DOMContentLoaded', requestWakeLock);
document.addEventListener('visibilitychange', () => {
    if (wakeLock !== null && document.visibilityState === 'visible') {
        requestWakeLock();
    }
});
"""
    scripts = scripts.replace("</script>", wakelock + "\n</script>")
    tv_html += scripts

tv_html += "\n</body>\n</html>"

with open('portal/templates/portal/salidas_tv_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(tv_html)
