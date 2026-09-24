import re

with open('portal/templates/portal/salidas_admin_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

radar_html = """
  <!-- RADAR METEOROLOGICO CONAGUA -->
  <div class="bg-slate-900 rounded-3xl p-4 shadow-xl border border-slate-800 overflow-hidden relative mt-2 mb-6">
    <div class="absolute top-6 left-6 z-10 flex items-center gap-2 bg-black/60 backdrop-blur px-3 py-1.5 rounded-lg border border-white/10 pointer-events-none">
      <span class="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse shadow-[0_0_8px_rgba(239,68,68,0.8)]"></span>
      <span class="text-white text-xs font-bold uppercase tracking-wider">Radar SIPROC - CONAGUA</span>
    </div>
    <iframe src="https://smn.conagua.gob.mx/tools/GUI/SIPROC/" class="w-full h-[500px] border-0 rounded-2xl filter contrast-125" loading="lazy"></iframe>
  </div>
"""

content = re.sub(r'<!-- SEM(.*?)FORO EN VIVO DE FLOTILLA -->', radar_html + r'\n  <!-- SEM\1FORO EN VIVO DE FLOTILLA -->', content)

anti_sleep_html = """
<!-- TRUCO PARA EVITAR QUE LA TV SE APAGUE: Video de Youtube silencioso en loop infinito -->
<iframe width="10" height="10" src="https://www.youtube.com/embed/g4mHPeMGTJM?autoplay=1&mute=1&loop=1&playlist=g4mHPeMGTJM" style="opacity:0.01; position:absolute; pointer-events:none; bottom:0; z-index:-9999;" allow="autoplay"></iframe>
"""
content = content.replace("{% endblock %}", anti_sleep_html + "\n{% endblock %}")

with open('portal/templates/portal/salidas_admin_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
