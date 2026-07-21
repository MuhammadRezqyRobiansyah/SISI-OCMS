import pandas as pd
import json
import os

filepath = r'c:\flow process overhaul component\sis\002. CHECKSHEET KOMPONEN\DISASSEMBLY ENGINE12V140-3.xls'
df = pd.read_excel(filepath, sheet_name=0, header=None)

# Load image map
with open('image_map.json', 'r') as f:
    image_map = json.load(f)

# Build the correct items based on the Excel structure
# Excel rows (1-indexed): col2=NO, col3=PARTS, col5-7=CONDITIONS
# We need to find which excel rows correspond to which numbered item

items = []
current_item = None
current_start_row = None

for i in range(12, len(df)):
    row = df.iloc[i]
    excel_row = i + 1  # pandas is 0-indexed, Excel is 1-indexed
    
    col2 = str(row[2]).strip() if pd.notna(row[2]) else ''
    col3 = str(row[3]).strip() if pd.notna(row[3]) else ''
    col5 = str(row[5]).strip() if pd.notna(row[5]) else ''
    col6 = str(row[6]).strip() if pd.notna(row[6]) else ''
    col7 = str(row[7]).strip() if pd.notna(row[7]) else ''

    # Skip header row
    if col2 == 'NO.' or 'PARTS TO REMOVE OR INSPECT' in col3:
        continue

    # New numbered item
    if col2 and col2.replace('.','').isdigit():
        if current_item:
            # Assign images based on row range
            imgs = []
            for r in range(current_start_row, excel_row):
                r_str = str(r)
                if r_str in image_map:
                    imgs.extend(image_map[r_str])
            current_item['images'] = imgs
            items.append(current_item)
        
        current_start_row = excel_row
        
        # Build conditions from this row
        cond_parts = [c for c in [col6, col7] if c and c not in ['\x95', '~']]
        cond = ' '.join(cond_parts).strip()
        
        current_item = {
            'no': int(col2.replace('.', '')),
            'parts': col3,
            'conditions': cond if cond else '',
            'row_start': excel_row,
            'images': []
        }
    elif current_item:
        # Continuation row
        if col3:
            current_item['parts'] += '\n' + col3
        
        cond_parts = [c for c in [col5, col6, col7] if c and c not in ['\x95', '~', '•']]
        cond = ' '.join(cond_parts).strip()
        if cond:
            if current_item['conditions']:
                current_item['conditions'] += '\n'
            current_item['conditions'] += cond

# Don't forget the last item
if current_item:
    imgs = []
    for r in range(current_start_row, len(df) + 1):
        r_str = str(r)
        if r_str in image_map:
            imgs.extend(image_map[r_str])
    current_item['images'] = imgs
    items.append(current_item)

# Clean up bullet characters from conditions
for item in items:
    cond = item['conditions']
    # Remove bullet chars
    for char in ['\x95', '~', '•', '·']:
        cond = cond.replace(char, '')
    # Clean up multiple spaces and leading/trailing whitespace
    lines = [line.strip() for line in cond.split('\n') if line.strip()]
    item['conditions'] = '\n'.join(lines)
    
    # Clean up parts
    parts = item['parts']
    lines = [line.strip() for line in parts.split('\n') if line.strip()]
    item['parts'] = '\n'.join(lines)
    
    # Remove row_start from output
    del item['row_start']

# Summary
print(f"Total items: {len(items)}")
for idx, item in enumerate(items):
    no = item['no']
    parts = item['parts'].replace('\n', ' / ')[:50]
    num_imgs = len(item['images'])
    cond_lines = len(item['conditions'].split('\n'))
    print(f"  [{idx}] NO={no} | PARTS={parts} | {cond_lines} cond lines | {num_imgs} images")

with open('excel_data_final.json', 'w', encoding='utf-8') as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print(f"\nSaved to excel_data_final.json")
