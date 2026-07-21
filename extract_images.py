import win32com.client
import os
import json
import time
import pythoncom

filepath = os.path.abspath(r'c:\flow process overhaul component\sis\002. CHECKSHEET KOMPONEN\DISASSEMBLY ENGINE12V140-3.xls')
outdir = os.path.abspath(r'c:\flow process overhaul component\sis\public\images\checksheet-12v140')

# Clean old broken images
for f in os.listdir(outdir):
    os.remove(os.path.join(outdir, f))

pythoncom.CoInitialize()
excel = win32com.client.Dispatch("Excel.Application")
excel.Visible = False
excel.DisplayAlerts = False

try:
    wb = excel.Workbooks.Open(filepath)
    ws = wb.Worksheets(1)
    shapes = ws.Shapes
    
    print(f"Total shapes: {shapes.Count}")
    image_map = {}
    exported = 0
    
    for i in range(1, shapes.Count + 1):
        shape = shapes.Item(i)
        try:
            top_row = shape.TopLeftCell.Row
            shape_type = shape.Type
            
            # Only Picture type=13, skip header row images
            if shape_type != 13 or top_row < 13:
                continue
            
            img_filename = f"img_{i}_row{top_row}.png"
            img_path = os.path.join(outdir, img_filename)
            
            # Method 2: Export by selecting shape and using SendKeys workaround
            # Actually use the Copy + Paste to MSPaint approach via clipboard
            # Better method: use Shape.Copy then paste into a new temp workbook chart
            
            shape.Copy()
            
            # Create a temp chart sheet in the same workbook
            chart_sheet = wb.Charts.Add()
            chart_sheet.Paste()
            # Remove the chart title etc, make background white
            try:
                chart_sheet.HasTitle = False
                chart_sheet.ChartArea.Format.Fill.ForeColor.RGB = 0xFFFFFF
            except:
                pass
            
            chart_sheet.Export(img_path, "PNG")
            chart_sheet.Delete()
            
            fsize = os.path.getsize(img_path)
            if fsize > 500:  # Only count real images
                r_str = str(top_row)
                if r_str not in image_map:
                    image_map[r_str] = []
                image_map[r_str].append(f"/images/checksheet-12v140/{img_filename}")
                exported += 1
                print(f"  OK shape {i} row {top_row}: {img_filename} ({fsize} bytes)")
            else:
                os.remove(img_path)
                print(f"  SKIP shape {i} row {top_row}: too small ({fsize} bytes)")
                
        except Exception as e:
            print(f"  ERR shape {i}: {str(e)[:80]}")
    
    wb.Close(False)
    
    with open('image_map.json', 'w') as f:
        json.dump(image_map, f, indent=2)
    
    print(f"\nExported {exported} valid images across {len(image_map)} rows")
    
finally:
    excel.Quit()
    pythoncom.CoUninitialize()
    print("Done!")
