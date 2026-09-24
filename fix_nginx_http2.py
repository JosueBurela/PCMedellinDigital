import re

with open('/tmp/default.backup', 'r', encoding='utf-8') as f:
    config = f.read()

# Replace the entire port 80 server block
new_server_80 = """server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name 107-170-59-223.sslip.io 107.170.59.223 _;

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
    }
}
"""

config = re.sub(r'server\s*{\s*if \(\System.Management.Automation.Internal.Host.InternalHost = 107-170-59-223\.sslip\.io\).*?return 404;.*?}', new_server_80, config, flags=re.DOTALL)

with open('/tmp/default.new3', 'w', encoding='utf-8') as f:
    f.write(config)
