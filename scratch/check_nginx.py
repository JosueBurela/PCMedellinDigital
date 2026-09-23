import subprocess

res = subprocess.run([
    'ssh', '-n',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    'root@107.170.59.223',
    'cat /etc/nginx/sites-enabled/* /etc/nginx/conf.d/*'
], capture_output=True, text=True, encoding='utf-8')

print("NGINX:\n", res.stdout[:1500])
