"""
Full extraction of DISASSEMBLY ENGINE12V140-3.xls
Captures:
  - Header info fields (WO NUMBER, ENGINE MODEL, etc.)
  - All 33 numbered items with sub-rows for LH/RH
  - Measurement/backlash tables at the end
"""
import pandas as pd
import json

filepath = r'c:\flow process overhaul component\sis\002. CHECKSHEET KOMPONEN\DISASSEMBLY ENGINE12V140-3.xls'
df = pd.read_excel(filepath, sheet_name=0, header=None)

def cell(r, c):
    """Get cell value as string, empty string if NaN"""
    if r >= len(df): return ''
    v = df.iloc[r][c] if c < len(df.columns) else None
    return str(v).strip() if pd.notna(v) else ''

# ============================================================
# 1. HEADER INFO (rows 0-11 in 0-indexed = rows 1-12 in Excel)
# ============================================================
header_info = {
    'title': 'DISASSEMBLY CHECK SHEET',
    'subtitle': 'KOMATSU ENGINE 12V140-3',
    'fields': [
        {'label': 'WO NUMBER', 'value': '', 'editable': True},
        {'label': 'ENGINE MODEL', 'value': 'SAA12V140E-3', 'editable': False},
        {'label': 'ENGINE SER. NO', 'value': '', 'editable': True},
        {'label': 'MACHINE MODEL', 'value': '', 'editable': True},
        {'label': 'UNIT CODE', 'value': '', 'editable': True},
        {'label': 'PUBL. DATE', 'value': '', 'editable': True},
        {'label': 'REVISION NO.', 'value': '06', 'editable': False},
        {'label': 'DOCUMENT NO.', 'value': '', 'editable': True},
    ],
    'process_fields': [
        {'label': 'PROCESS', 'value': '', 'editable': True},
        {'label': 'START/date&time', 'value': '', 'editable': True},
        {'label': 'FINISH/date&time', 'value': '', 'editable': True},
        {'label': 'DISASSEMBLY BY', 'value': '', 'editable': True},
    ]
}

# ============================================================
# 2. MAIN CHECKSHEET ITEMS (starting from row index 12)
# ============================================================
# We need to capture sub-rows for LH/RH entries
# Excel structure: col2=NO, col3=PARTS, col5-7=CONDITIONS
# Some items have sub-entries like UPPER/LOWER, LH/RH, FRONT/CENTRE/REAR

items = []
current_item = None
current_start_row = None

# Load image map if available
try:
    with open('image_map.json', 'r') as f:
        image_map = json.load(f)
except:
    image_map = {}

def get_images(start_row, end_row):
    imgs = []
    for r in range(start_row, end_row):
        r_str = str(r)
        if r_str in image_map:
            imgs.extend(image_map[r_str])
    return imgs

for i in range(12, len(df)):
    excel_row = i + 1
    
    c2 = cell(i, 2)  # NO
    c3 = cell(i, 3)  # PARTS col 1
    c4 = cell(i, 4)  # PARTS col 2 (sometimes sub-label)
    c5 = cell(i, 5)  # CONDITIONS col 1
    c6 = cell(i, 6)  # CONDITIONS col 2
    c7 = cell(i, 7)  # CONDITIONS col 3
    c8 = cell(i, 8)  # Sometimes REUSE area or sub-labels
    c9 = cell(i, 9)  # Sub-labels like LH/RH
    
    # Skip header
    if c2 == 'NO.' or 'PARTS TO REMOVE' in c3:
        continue
    
    # Check for section breaks like "ATTACHED", "OUTSIDE DIAMETER..."
    # These signal the measurement tables section
    if 'ATTACHED' in c5 or 'OUTSIDE DIAMETER' in c5 or 'CAMSHAFT JOURNAL' in c5:
        if current_item:
            current_item['images'] = get_images(current_start_row, excel_row)
            items.append(current_item)
            current_item = None
        break  # Stop main items, rest is measurement tables
    
    # New numbered item
    if c2 and c2.replace('.','').isdigit():
        if current_item:
            current_item['images'] = get_images(current_start_row, excel_row)
            items.append(current_item)
        
        current_start_row = excel_row
        
        # Clean bullet chars
        cond_parts = [c for c in [c5, c6, c7] if c and c not in ['\x95', '~', '•', '·']]
        cond = ' '.join(cond_parts).strip()
        
        # Detect sub-rows (LH/RH, UPPER/LOWER, FRONT/CENTRE/REAR)
        sub_rows = []
        
        current_item = {
            'no': int(c2.replace('.', '')),
            'parts': c3,
            'conditions': [cond] if cond else [],
            'sub_rows': sub_rows,
            'images': []
        }
    elif current_item:
        # Continuation row
        if c3:
            current_item['parts'] += '\n' + c3
        
        # Check for sub-row indicators (LH, RH, UPPER, LOWER, FRONT, CENTRE, REAR)
        sub_labels_in_row = []
        for col_val in [c4, c5, c6, c7, c8, c9]:
            if col_val.upper() in ['LH', 'RH', 'UPPER', 'LOWER', 'FRONT', 'CENTRE', 'CENTER', 'REAR']:
                sub_labels_in_row.append(col_val.upper())
        
        if sub_labels_in_row:
            for sl in sub_labels_in_row:
                current_item['sub_rows'].append({
                    'label': sl,
                    'reuse': False,
                    'salvage': False,
                    'replace': False,
                    'remarks': ''
                })
        
        # Append conditions
        cond_parts = [c for c in [c5, c6, c7] if c and c not in ['\x95', '~', '•', '·']]
        # Don't add if it's just a sub-label
        cond = ' '.join(cond_parts).strip()
        if cond and cond.upper() not in ['LH', 'RH', 'UPPER', 'LOWER', 'FRONT', 'CENTRE', 'CENTER', 'REAR']:
            current_item['conditions'].append(cond)

def get_images(start_row, end_row):
    imgs = []
    for r in range(start_row, end_row):
        r_str = str(r)
        if r_str in image_map:
            imgs.extend(image_map[r_str])
    return imgs

# Finish last item
if current_item:
    current_item['images'] = get_images(current_start_row, len(df) + 1)
    items.append(current_item)

# Clean up conditions
for item in items:
    cleaned = []
    for line in item['conditions']:
        for char in ['\x95', '~', '•', '·']:
            line = line.replace(char, '')
        line = line.strip()
        if line:
            cleaned.append(line)
    item['conditions'] = cleaned
    
    # Clean parts
    parts_lines = [l.strip() for l in item['parts'].split('\n') if l.strip()]
    item['parts'] = '\n'.join(parts_lines)

# ============================================================
# 3. MEASUREMENT TABLES (after the main items)
# ============================================================
# Find where measurement data starts
measurement_tables = []
in_measurement = False
current_table = None

for i in range(12, len(df)):
    c5 = cell(i, 5)
    
    if 'OUTSIDE DIAMETER OF CRANKSHAFT' in c5:
        current_table = {
            'title': 'OUTSIDE DIAMETER OF CRANKSHAFT PIN JOURNAL AND MAIN JOURNAL',
            'sections': []
        }
        in_measurement = True
        continue
    
    if 'OUTSIDE DIAMETER OF CAMSHAFT' in c5:
        if current_table:
            measurement_tables.append(current_table)
        current_table = {
            'title': 'OUTSIDE DIAMETER OF CAMSHAFT JOURNAL AND CAM HEIGHT',
            'sections': []
        }
        continue
    
    if in_measurement and current_table:
        # Collect section info
        if 'Series' in c5 or 'series' in c5:
            current_table['sections'].append({
                'series': c5,
                'rows': []
            })
        elif current_table['sections']:
            # Add measurement rows
            vals = [cell(i, c) for c in range(2, 12)]
            if any(v for v in vals):
                current_table['sections'][-1]['rows'].append(vals)

if current_table:
    measurement_tables.append(current_table)

# ============================================================
# FINAL OUTPUT
# ============================================================
output = {
    'header': header_info,
    'items': items,
    'measurement_tables': measurement_tables
}

with open('excel_data_final.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

# Summary
print(f"Header fields: {len(header_info['fields'])}")
print(f"Main items: {len(items)}")
for idx, item in enumerate(items):
    no = item['no']
    parts = item['parts'].replace('\n', ' / ')[:45]
    n_cond = len(item['conditions'])
    n_sub = len(item['sub_rows'])
    n_img = len(item['images'])
    print(f"  {no:2d}. {parts:<47s} | {n_cond} conds | {n_sub} subs | {n_img} imgs")
print(f"Measurement tables: {len(measurement_tables)}")
for mt in measurement_tables:
    print(f"  - {mt['title'][:60]} ({len(mt['sections'])} sections)")

print(f"\nSaved to excel_data_final.json")
