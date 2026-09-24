import urllib.request
import re

url = 'http://www.atlasnacionalderiesgos.gob.mx/portal/MonitoreoSecretarioPublico/'
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8', errors='ignore')
        paths = set(re.findall(r'src="(/[^"]+)"', html) + re.findall(r'href="(/[^"]+)"', html))
        for p in paths:
            print(p.split('/')[1]) # Get root dir
except Exception as e:
    print("Error:", e)
