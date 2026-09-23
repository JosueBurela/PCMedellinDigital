with open('messages.jsonl', 'r', encoding='utf-8-sig') as f:
    for i, line in enumerate(f):
        if i == 6:
            with open('failing_line.txt', 'w', encoding='utf-8') as out:
                out.write(line)
            print("Wrote failing line to failing_line.txt")
            break
