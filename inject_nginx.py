import re

with open('/tmp/default.backup', 'r', encoding='utf-8') as f:
    config = f.read()

proxy_block = """
    # Proxy para Radar CONAGUA (bypass X-Frame-Options)
    location ~ ^/(tools|data|calor_oceanico|img|rayos|pronostico_3dias|gamma2|edo_mun)/ {
        proxy_pass https://smn.conagua.gob.mx;
        proxy_hide_header X-Frame-Options;
        proxy_hide_header Content-Security-Policy;
        proxy_set_header Host smn.conagua.gob.mx;
        proxy_ssl_server_name on;
        proxy_ssl_protocols TLSv1.2 TLSv1.3;
    }
"""

if "Radar CONAGUA" not in config:
    # Insert before location / {
    config = config.replace("    location / {", proxy_block + "\n    location / {")
    with open('/tmp/default.new', 'w', encoding='utf-8') as f:
        f.write(config)
