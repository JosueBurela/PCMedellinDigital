import urllib.request

url = 'http://www.atlasnacionalderiesgos.gob.mx/portal/MonitoreoSecretarioPublico/'
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8', errors='ignore')
        if "Volc" in html or "Fase" in html or "Exhalaciones" in html:
            print("MATCHED DASHBOARD!!!")
            print(html[:1000])
        else:
            print("No match in html text, length:", len(html))
except Exception as e:
    print("Error:", e)
