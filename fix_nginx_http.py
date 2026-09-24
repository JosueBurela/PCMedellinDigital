import re

with open('/tmp/default.backup', 'r', encoding='utf-8') as f:
    config = f.read()

http_block_old = """server {
    if (System.Management.Automation.Internal.Host.InternalHost = 107-170-59-223.sslip.io) {
        return 301 https://System.Management.Automation.Internal.Host.InternalHost;
    }"""

http_block_new = """server {
    # Permitir /intranet/mapa-tv/ por HTTP sin redirigir (para evitar bloqueo Mixed Content del mapa de CENAPRED)
    location /intranet/mapa-tv/ {
        proxy_pass http://127.0.0.1:8000/intranet/mapa-tv/;
        proxy_set_header Host System.Management.Automation.Internal.Host.InternalHost;
        proxy_set_header X-Real-IP ;
        proxy_set_header X-Forwarded-For ;
        proxy_set_header X-Forwarded-Proto ;
    }

    location / {
        if (System.Management.Automation.Internal.Host.InternalHost = 107-170-59-223.sslip.io) {
            return 301 https://System.Management.Automation.Internal.Host.InternalHost;
        }
        return 404;
    }"""

config = config.replace(http_block_old, http_block_new)

# Limpiar el proxy que hicimos antes para el portal porque ya no lo necesitamos, o lo dejamos por si acaso.
# Lo dejamos por si acaso, no estorba.

with open('/tmp/default.new2', 'w', encoding='utf-8') as f:
    f.write(config)
