import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

frap_list = []
with open('messages.jsonl', 'r', encoding='utf-8') as f:
    for line_idx, line in enumerate(f):
        if 'NOMBRE DEL PACIENTE' in line:
            try:
                data = json.loads(line)
                frap_list.append(data)
            except Exception as e:
                pass

print(f"Total mensajes FRAP parseados de messages.jsonl: {len(frap_list)}")
print("Claves de un mensaje:", list(frap_list[0].keys()) if frap_list else [])

# Ver primeros 5
for i, d in enumerate(frap_list[:5]):
    print(f"\n--- FRAP {i+1} ---")
    txt = d.get('text_content') or d.get('message_text') or d.get('text') or str(d)
    print(txt[:400])
