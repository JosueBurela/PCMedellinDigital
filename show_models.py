with open('c:/Users/burel/OneDrive/Documentos/PCivil Digital/portal/models.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    start = -1
    for i, line in enumerate(lines):
        if 'class BitacoraSalidaVehiculo' in line:
            start = i
            break
    if start != -1:
        print("".join(lines[start:start+40]))
