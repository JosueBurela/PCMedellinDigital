import sys
import subprocess
import base64

cmd = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "uptime"
b64_cmd = base64.b64encode(cmd.encode('utf-8')).decode('ascii')
remote_wrapper = f"echo {b64_cmd} | base64 -d | bash"

res = subprocess.run([
    'ssh', '-n',
    '-i', r'C:\Users\burel\.ssh\id_ed25519_digitalocean',
    '-o', 'StrictHostKeyChecking=no',
    'root@107.170.59.223',
    remote_wrapper
], capture_output=True, text=True, encoding='utf-8')

if res.stdout:
    print(res.stdout)
if res.stderr:
    print("[STDERR]", res.stderr)
