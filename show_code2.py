with open('portal/utils/whatsapp_salidas_tracker.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i in range(85, 105):
        print(f"{i+1}: {lines[i].rstrip()}")
