import urllib.request
import re

url = 'http://www.atlasnacionalderiesgos.gob.mx/portal/MonitoreoSecretarioPublico/'
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8', errors='ignore')
        # find all http://
        paths = set(re.findall(r'http://[a-zA-Z0-9_./-]+', html))
        for p in paths:
            print(p)
except Exception as e:
    print("Error:", e)
