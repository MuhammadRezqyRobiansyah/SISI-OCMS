import re

html_content = """        <style>
            .dis-table-wrap { overflow-x: auto; border-radius: 8px; border: 2px solid #334155; }
            .dis-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; background: #0d1b2a; color: #e2e8f0; }
            .dis-table th { background: linear-gradient(180deg, #1e3a5f, #162d50); color: #93c5fd; font-weight: 700; text-transform: uppercase; font-size: 0.7rem; letter-spacing: 0.05em; padding: 10px 8px; border: 1px solid #334155; position: sticky; top: 0; z-index: 2; text-align: center; }
            .dis-table td { border: 1px solid #1e293b; padding: 8px; vertical-align: top; }
            .dis-table tr:hover td { background: rgba(56,189,248,0.06); }
            .dis-td-no { text-align: center; font-weight: 700; color: #93c5fd; width: 40px; }
            .dis-td-parts { font-weight: 600; color: #f1f5f9; width: 180px; white-space: pre-line; }
            .dis-td-cond { color: #cbd5e1; width: 280px; line-height: 1.6; }
            .dis-td-chk { text-align: center; width: 35px; }
            .dis-td-chk input[type=checkbox] { width: 18px; height: 18px; accent-color: #38bdf8; cursor: pointer; }
            .dis-td-sketch { width: 220px; }
            .dis-td-sketch img { max-width: 200px; max-height: 150px; border-radius: 6px; border: 1px solid #334155; margin: 4px 2px; cursor: pointer; transition: transform 0.2s; display: block; }
            .dis-td-sketch img:hover { transform: scale(1.05); }
            .dis-td-remarks { width: 160px; }
            .dis-td-remarks textarea { width: 100%; min-height: 40px; background: rgba(255,255,255,0.05); border: 1px solid #334155; border-radius: 4px; color: #e2e8f0; padding: 6px; font-size: 0.78rem; resize: vertical; }
            .dis-sub-row td { background: rgba(30,58,95,0.3) !important; }
            .dis-sub-label { font-weight: 600; color: #60a5fa; font-size: 0.75rem; text-align: center; }
            .dis-header-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 16px; }
            .dis-header-field { display: flex; align-items: center; gap: 8px; }
            .dis-header-field label { font-size: 0.7rem; font-weight: 700; color: #93c5fd; text-transform: uppercase; white-space: nowrap; min-width: 120px; }
            .dis-header-field input { flex: 1; background: rgba(255,255,255,0.05); border: 1px solid #334155; border-radius: 4px; color: #e2e8f0; padding: 6px 8px; font-size: 0.8rem; }
            .dis-header-field input:read-only { opacity: 0.6; }
            .dis-img-modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.85); backdrop-filter: blur(8px); z-index: 9999; align-items: center; justify-content: center; cursor: zoom-out; }
            .dis-img-modal img { max-width: 90vw; max-height: 90vh; border-radius: 12px; box-shadow: 0 0 40px rgba(56,189,248,0.3); }
            
            /* Vertical text styles */
            .dis-vertical-th {
                writing-mode: vertical-rl;
                transform: rotate(180deg);
                white-space: nowrap;
                height: 100px;
                padding: 10px 4px !important;
                vertical-align: middle;
            }
        </style>

        <div class="glass-card fade-up">
            @php
                $csData = $currentChecksheet->items;
                $headerData = $csData['header'] ?? null;
                $mainItems = $csData['items'] ?? $csData;
                $isArray = isset($csData['items']);
            @endphp

            {{-- HEADER INFO FORM --}}
            @if($headerData)
            <div style="border: 1px solid #334155; border-radius: 8px; padding: 16px; margin-bottom: 20px; background: rgba(30,58,95,0.2);">
                <div style="font-weight: 800; font-size: 1rem; color: #f1f5f9; text-align: center; margin-bottom: 4px;">📋 {{ $headerData['title'] ?? 'DISASSEMBLY CHECK SHEET' }}</div>
                <div style="font-size: 0.85rem; color: #93c5fd; text-align: center; margin-bottom: 12px;">{{ $headerData['subtitle'] ?? 'KOMATSU ENGINE 12V140-3' }}</div>
                <div class="dis-header-grid" id="headerFields">
                    @foreach($headerData['fields'] ?? [] as $fIdx => $field)
                    <div class="dis-header-field">
                        <label>{{ $field['label'] }}</label>
                        <input type="text" 
                               value="{{ $field['value'] ?? '' }}" 
                               data-field-idx="{{ $fIdx }}"
                               {{ ($field['editable'] ?? true) ? '' : 'readonly' }}
                               {{ (!$isReviewMode && auth()->user()->hasAnyRole(['Mechanic', 'Supervisor', 'SuperAdmin'])) ? '' : 'readonly' }}
                        />
                    </div>
                    @endforeach
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 8px;">
                    @foreach($headerData['process_fields'] ?? [] as $pIdx => $pf)
                    <div class="dis-header-field">
                        <label style="min-width: auto; font-size: 0.65rem;">{{ $pf['label'] }}</label>
                        <input type="text" value="{{ $pf['value'] ?? '' }}" data-process-idx="{{ $pIdx }}"
                               {{ (!$isReviewMode && auth()->user()->hasAnyRole(['Mechanic', 'Supervisor', 'SuperAdmin'])) ? '' : 'readonly' }} />
                    </div>
                    @endforeach
                </div>
            </div>
            @endif

            {{-- Save + Info Bar --}}
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; flex-wrap:wrap; gap:8px;">
                <div style="font-size:0.75rem; color:var(--text-secondary);">{{ count(is_array($mainItems) ? $mainItems : []) }} item inspeksi • Centang REUSE/SALVAGE/REPLACE lalu klik Simpan</div>
                @if(!$isReviewMode && auth()->user()->hasAnyRole(['Mechanic', 'Supervisor', 'SuperAdmin']))
                <button id="btnSaveSpreadsheet" style="padding:10px 24px; border-radius:6px; font-weight:700; cursor:pointer; background:linear-gradient(135deg,#2563eb,#1d4ed8); color:#fff; border:none; font-size:0.85rem; transition:all 0.3s;">
                    💾 Simpan Data
                </button>
                @endif
            </div>

            {{-- MAIN TABLE --}}
            <div class="dis-table-wrap" style="max-height:700px; overflow-y:auto;">
                <table class="dis-table" id="disTable">
                    <thead>
                        <tr>
                            <th>NO</th>
                            <th>PARTS TO REMOVE OR INSPECT</th>
                            <th>CONDITIONS TO BE INSPECTED</th>
                            <th style="padding: 0;"><div class="dis-vertical-th">REUSE</div></th>
                            <th style="padding: 0;"><div class="dis-vertical-th">SALVAGE</div></th>
                            <th style="padding: 0;"><div class="dis-vertical-th">REPLACE</div></th>
                            <th>SKETCH DRAWING / PHOTOES</th>
                            <th>REMARKS</th>
                        </tr>
                    </thead>
                    <tbody id="disTableBody"></tbody>
                </table>
            </div>
        </div>

        {{-- Image zoom modal --}}
        <div class="dis-img-modal" id="disImgModal" onclick="this.style.display='none'">
            <img id="disImgModalImg" src="" alt="Zoom" />
        </div>

        <script>
        document.addEventListener('DOMContentLoaded', function() {
            const rawData = @json($currentChecksheet->items);
            const savedAnswers = @json($currentChecksheet->answers ?? []);
            const isEditable = @json(!$isReviewMode && auth()->user()->hasAnyRole(['Mechanic', 'Supervisor', 'SuperAdmin']));
            
            // Handle both old format (array) and new format (object with items key)
            const items = rawData.items || rawData;
            const tbody = document.getElementById('disTableBody');
            
            items.forEach(function(item, idx) {
                const saved = (savedAnswers && savedAnswers[idx]) ? savedAnswers[idx] : {};
                const hasSubRows = item.sub_rows && item.sub_rows.length > 0;
                const subCount = hasSubRows ? item.sub_rows.length : 1;
                
                // === MAIN ROW ===
                const tr = document.createElement('tr');
                
                // NO (rowspan if sub_rows)
                const tdNo = document.createElement('td');
                tdNo.className = 'dis-td-no';
                tdNo.textContent = item.no || '';
                if (hasSubRows) tdNo.rowSpan = subCount + 1;
                tr.appendChild(tdNo);
                
                // PARTS (rowspan)
                const tdParts = document.createElement('td');
                tdParts.className = 'dis-td-parts';
                tdParts.textContent = (item.parts || '').replace(/\\n/g, '\\n');
                if (hasSubRows) tdParts.rowSpan = subCount + 1;
                tr.appendChild(tdParts);
                
                // CONDITIONS (rowspan)
                const tdCond = document.createElement('td');
                tdCond.className = 'dis-td-cond';
                const condArr = Array.isArray(item.conditions) ? item.conditions : (item.conditions || '').split('\\n');
                condArr.forEach(function(line, li) {
                    if (!line.trim()) return;
                    const p = document.createElement('div');
                    p.style.marginBottom = '3px';
                    p.textContent = '• ' + line.trim();
                    tdCond.appendChild(p);
                });
                if (hasSubRows) tdCond.rowSpan = subCount + 1;
                tr.appendChild(tdCond);
                
                if (!hasSubRows) {
                    // Checkboxes for main row (no sub-rows)
                    ['reuse', 'salvage', 'replace'].forEach(function(field) {
                        const td = document.createElement('td');
                        td.className = 'dis-td-chk';
                        const cb = document.createElement('input');
                        cb.type = 'checkbox';
                        cb.checked = saved[field] || false;
                        cb.disabled = !isEditable;
                        td.appendChild(cb);
                        tr.appendChild(td);
                    });
                } else {
                    // Empty cells for main row when sub-rows exist
                    for (let c = 0; c < 3; c++) {
                        const td = document.createElement('td');
                        td.className = 'dis-td-chk';
                        tr.appendChild(td);
                    }
                }
                
                // SKETCH (rowspan)
                const tdSketch = document.createElement('td');
                tdSketch.className = 'dis-td-sketch';
                if (item.images && item.images.length > 0) {
                    item.images.forEach(function(src) {
                        const img = document.createElement('img');
                        img.src = src;
                        img.alt = 'Sketch ' + item.no;
                        img.loading = 'lazy';
                        img.onclick = function(e) {
                            e.stopPropagation();
                            document.getElementById('disImgModalImg').src = src;
                            document.getElementById('disImgModal').style.display = 'flex';
                        };
                        tdSketch.appendChild(img);
                    });
                }
                if (hasSubRows) tdSketch.rowSpan = subCount + 1;
                tr.appendChild(tdSketch);
                
                // REMARKS (rowspan)
                const tdRemarks = document.createElement('td');
                tdRemarks.className = 'dis-td-remarks';
                if (isEditable) {
                    const ta = document.createElement('textarea');
                    ta.value = saved.remarks || '';
                    ta.placeholder = 'Catatan...';
                    tdRemarks.appendChild(ta);
                } else {
                    tdRemarks.textContent = saved.remarks || '';
                }
                if (hasSubRows) tdRemarks.rowSpan = subCount + 1;
                tr.appendChild(tdRemarks);
                
                tbody.appendChild(tr);
                
                // === SUB-ROWS (LH/RH/UPPER/LOWER etc) ===
                if (hasSubRows) {
                    item.sub_rows.forEach(function(sub, si) {
                        const subTr = document.createElement('tr');
                        subTr.className = 'dis-sub-row';
                        
                        const savedSub = (saved.sub_rows && saved.sub_rows[si]) ? saved.sub_rows[si] : {};
                        
                        ['reuse', 'salvage', 'replace'].forEach(function(field) {
                            const td = document.createElement('td');
                            td.className = 'dis-td-chk';
                            // Add label before first checkbox
                            if (field === 'reuse') {
                                const lbl = document.createElement('div');
                                lbl.className = 'dis-sub-label';
                                lbl.textContent = sub.label;
                                td.insertBefore(lbl, td.firstChild);
                            }
                            const cb = document.createElement('input');
                            cb.type = 'checkbox';
                            cb.checked = savedSub[field] || false;
                            cb.disabled = !isEditable;
                            td.appendChild(cb);
                            subTr.appendChild(td);
                        });
                        
                        tbody.appendChild(subTr);
                    });
                }
            });
            
            // === SAVE HANDLER ===
            const saveBtn = document.getElementById('btnSaveSpreadsheet');
            if (saveBtn) {
                saveBtn.addEventListener('click', function() {
                    const answers = {};
                    
                    // Collect header fields
                    const headerFields = document.querySelectorAll('#headerFields input[data-field-idx]');
                    const processFields = document.querySelectorAll('input[data-process-idx]');
                    if (headerFields.length > 0) {
                        answers.header_fields = {};
                        headerFields.forEach(function(input) {
                            answers.header_fields[input.dataset.fieldIdx] = input.value;
                        });
                    }
                    if (processFields.length > 0) {
                        answers.process_fields = {};
                        processFields.forEach(function(input) {
                            answers.process_fields[input.dataset.processIdx] = input.value;
                        });
                    }
                    
                    // Collect table data
                    let itemIdx = 0;
                    const tableAnswers = [];
                    const allRows = tbody.querySelectorAll('tr:not(.dis-sub-row)');
                    
                    allRows.forEach(function(mainRow) {
                        const cbs = mainRow.querySelectorAll('input[type=checkbox]');
                        const ta = mainRow.querySelector('textarea');
                        const itemAnswer = {
                            reuse: cbs[0] ? cbs[0].checked : false,
                            salvage: cbs[1] ? cbs[1].checked : false,
                            replace: cbs[2] ? cbs[2].checked : false,
                            remarks: ta ? ta.value : '',
                            sub_rows: []
                        };
                        
                        // Collect sub-rows
                        let next = mainRow.nextElementSibling;
                        while (next && next.classList.contains('dis-sub-row')) {
                            const subCbs = next.querySelectorAll('input[type=checkbox]');
                            itemAnswer.sub_rows.push({
                                reuse: subCbs[0] ? subCbs[0].checked : false,
                                salvage: subCbs[1] ? subCbs[1].checked : false,
                                replace: subCbs[2] ? subCbs[2].checked : false
                            });
                            next = next.nextElementSibling;
                        }
                        
                        tableAnswers.push(itemAnswer);
                    });
                    
                    answers.items = tableAnswers;
                    
                    saveBtn.textContent = 'Menyimpan...';
                    saveBtn.disabled = true;
                    
                    fetch(`/components/{{ $comp->comp_id }}/spreadsheet-checksheet/{{ $checksheetStage }}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', 'X-CSRF-TOKEN': '{{ csrf_token() }}' },
                        body: JSON.stringify({ answers: answers })
                    })
                    .then(r => r.json())
                    .then(res => {
                        if (res.success) {
                            saveBtn.textContent = '✅ Tersimpan!';
                            saveBtn.style.background = 'linear-gradient(135deg,#059669,#047857)';
                            setTimeout(() => { saveBtn.textContent = '💾 Simpan Data'; saveBtn.style.background = 'linear-gradient(135deg,#2563eb,#1d4ed8)'; }, 2000);
                        } else {
                            alert('Gagal: ' + (res.message || 'Error'));
                        }
                    })
                    .catch(() => alert('Kesalahan koneksi!'))
                    .finally(() => { saveBtn.disabled = false; });
                });
            }
        });
        </script>
"""

with open(r'c:\flow process overhaul component\sis\resources\views\overhauls\show.blade.php', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = re.compile(r'<div class="glass-card fade-up" style="padding: 0; overflow: hidden; height: 800px;">\s*<iframe.*?</iframe>\s*</div>', re.DOTALL)
new_content = pattern.sub(html_content, content)

with open(r'c:\flow process overhaul component\sis\resources\views\overhauls\show.blade.php', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Done")
