import json

items = json.load(open('excel_data_v2.json', 'r', encoding='utf-8'))
for i, it in enumerate(items):
    no = it['no']
    parts = it['parts'].replace('\n', ' / ')[:50]
    is_h = it.get('is_header', False)
    print(f"{i}: NO={no} | PARTS={parts} | header={is_h}")
