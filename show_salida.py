with open('portal/utils/whatsapp_salidas_tracker.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if "if tipo_evento == 'SALIDA':" in line:
            print("".join(lines[i-5:i+40]))
            break
