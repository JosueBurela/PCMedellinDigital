import json

with open('messages.jsonl', 'r', encoding='utf-8-sig') as f:
    types = set()
    count = 0
    for line in f:
        line = line.strip()
        if not line: continue
        msg = json.loads(line)
        count += 1
        if msg.get('messageType'):
            types.add(msg['messageType'])

print('Total Messages:', count)
print('Message Types:', types)
