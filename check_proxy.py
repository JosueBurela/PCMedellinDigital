import urllib.request
import re

url = 'http://127.0.0.1/portal/MonitoreoSecretarioPublico/'
try:
    req = urllib.request.Request(url, headers={'Host': '107-170-59-223.sslip.io'})
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8', errors='ignore')
        paths = set(re.findall(r'http://[a-zA-Z0-9_./-]+', html))
        for p in paths:
            print(p)
except Exception as e:
    print("Error:", e)
