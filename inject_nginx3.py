import re

with open('/tmp/default.backup', 'r', encoding='utf-8') as f:
    config = f.read()

proxy_block = """
    # Proxy para Atlas Nacional de Riesgos (HTTP a HTTPS mixed-content bypass)
    location /portal/ {
        proxy_pass http://www.atlasnacionalderiesgos.gob.mx/portal/;
        proxy_hide_header X-Frame-Options;
        proxy_hide_header Content-Security-Policy;
        proxy_set_header Host www.atlasnacionalderiesgos.gob.mx;
        proxy_set_header Accept-Encoding ""; # Para que sub_filter funcione (no gzip)
        
        # Reescribir HTTP a HTTPS para evitar Mixed Content bloqueado por el navegador
        sub_filter 'http://js.arcgis.com' 'https://js.arcgis.com';
        sub_filter 'http://ajax.googleapis.com' 'https://ajax.googleapis.com';
        sub_filter 'http://rmgir.proyectomesoamerica.org' 'https://rmgir.proyectomesoamerica.org';
        sub_filter 'http://fonts.googleapis.com' 'https://fonts.googleapis.com';
        sub_filter 'http://www.atlasnacionalderiesgos.gob.mx' 'https://107-170-59-223.sslip.io';
        sub_filter_once off;
        sub_filter_types text/html text/javascript application/javascript text/css;
    }
"""

if "Atlas Nacional de Riesgos" not in config:
    # Insert before location / {
    config = config.replace("    location / {", proxy_block + "\n    location / {")
    with open('/tmp/default.new', 'w', encoding='utf-8') as f:
        f.write(config)
