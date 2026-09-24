with open('portal/utils/whatsapp_salidas_tracker.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if "quoted_participant" in line:
            print("".join(lines[i-15:i+35]))
            break
