# Handoff — SISI-OCMS (Cursor → Claude Desktop)

**Repo:** `c:\Users\Administrator\.gemini\antigravity\scratch\SISI-OCMS`  
**Tanggal handoff:** 2026-07-26  
**Branch:** (working tree, banyak perubahan belum commit)

---

## Update 2026-07-27 — Checksheet lokal (tanpa Google Sheets)

Tampilan checksheet sekarang bisa disajikan **langsung dari database**, 1:1
seperti Excel: lebar kolom, merge, border, warna, dan gambar ikut terbawa.

Alur: file `.xlsx` diimpor sekali → layout + peta kolom keputusan disimpan di
DB → halaman dirender dari DB → mekanik mencentang di halaman itu → jawaban
masuk ke tabel, bukan ke spreadsheet.

```bash
php artisan checksheet:import-layouts --dry-run
php artisan checksheet:import-layouts          # 44 layout, semua berhasil
php tools/render_layout_preview.php            # pratinjau HTML tanpa server
```

Rute: `/checksheet-layouts` (daftar + pratinjau) dan
`/components/{comp}/local-checksheet/{kind}` (pengisian per komponen).

| Berkas | Peran |
|--------|-------|
| `app/Services/XlsxLayoutReader.php` | Baca .xlsx (ZipArchive bawaan PHP, tanpa library luar) |
| `app/Services/SpreadsheetLayoutImporter.php` | Ekstrak gambar + deteksi kolom keputusan, simpan layout |
| `app/Services/SpreadsheetHtmlRenderer.php` | Layout → tabel HTML mirip Excel |
| `app/Http/Controllers/LocalChecksheetController.php` | Pratinjau, pengisian, simpan sel |
| `app/Console/Commands/ImportSpreadsheetLayouts.php` | `checksheet:import-layouts` |
| `tests/Feature/LocalChecksheetTest.php` | 7 test memakai template asli |

Catatan penting:

- **Pencarian keyword hanya sekali saat impor.** Setelah kolom keputusan
  ketemu, posisinya disimpan di `decision_map`. Template tidak perlu
  diseragamkan manual lagi — header `REUSE | SALVG | REPAIR` diterima apa
  adanya, begitu juga sub-header `U/A|U/R|R/N` yang ada di baris terpisah.
- **Layout dikompresi** (`App\Casts\CompressedJson`) karena
  `database/database.sqlite` ikut di-commit: 30 MB → DB total 5,3 MB.
- **Gambar** diekstrak ke `public/checksheet-media/` (887 file, 119 MB,
  gitignore). Dibuat ulang dengan perintah impor.
- **Gambar vektor EMF/WMF** (hanya di workbook Engine, 259 file) belum bisa
  ditampilkan browser — dirender sebagai kotak penanda. Seluruh Powertrain
  nol vektor, jadi tampil utuh.
- Belum dikerjakan: memindahkan scan FR agar membaca `decision_map` dari DB
  (sekarang masih lewat Google Sheets), dan input untuk kolom ukuran.

---

## Update 2026-07-26 (2) — Format Excel dipulihkan

**Masalah:** skrip openpyxl (`format_siap_templates.py`,
`normalize_decision_headers.py`) merusak **30 dari 72** file SIAP. openpyxl
membuang gambar **EMF/WMF** saat menyimpan, dan drawing ikut hilang —
DISASSEMBLY ENGINE SAA6D170E-5 anjlok dari **14,6 MB → 85 KB** (53 gambar → 0).

**Sudah diperbaiki:**

1. Semua 72 file dipulihkan dari `_SIAP_BACKUP/20260726_182618/`
   (`tools/restore_siap_from_backup.py`). Kondisi rusak diarsipkan ke
   `_SIAP_BACKUP/20260726_210211_before_restore/`.
2. Penyeragaman header diulang lewat **Excel COM**
   (`tools/normalize_headers_excel.ps1`) — 9 file, 25 sel, gambar utuh.
3. Kedua skrip openpyxl kini **menolak berjalan** tanpa flag paksa.
4. Dua alat pemeriksa baru:
   - `tools/inspect_xlsx_damage.py` — bandingkan gambar/drawing/merge vs backup
   - `tools/verify_siap_state.py` — kesiapan otomasi, MASALAH vs CATATAN

**Status sekarang:** `inspect_xlsx_damage.py` → **rusak 0 / 72**;
`verify_siap_state.py` → **MASALAH (0)**, 6 catatan tidak menghambat.

**Pelajaran:** template SIAP hanya boleh diedit lewat Excel COM. Sel keputusan
**tidak** perlu diisi `FALSE` — sel kosong sudah dibaca sebagai tidak
dicentang, dan Google Sheets mengubahnya jadi checkbox saat Insert → Checkbox.

---

## Update 2026-07-26 (1) — Stage 2 / Disassembly

**Formatting template SIAP: SELESAI.** `python tools/verify_siap_state.py` → **MASALAH (0)**.

Yang dikerjakan sesi ini:

1. **Multi-tab** — OCMS dulu hanya membaca **satu** tab per workbook. Semua
   keputusan di tab lain (`INSPEKSI NO2/NO3`, `DISASSY RH`, `CYL HEAD`,
   `TURBO`, `SUPPLY PUMP`) tidak pernah jadi FR/PR. Sekarang webapp
   mengembalikan semua tab yang cocok keyword dan parser memproses semuanya.
   Contoh nyata: SUBASSY DISASSEMBLY D375-6 dari **0 → 39 baris part**.
2. **Kolom `section`** (migrasi `2026_07_26_120000`) — nama tab disimpan di FR
   dan Part Request. Part bernama sama pada unit berbeda (valve NO1 vs NO2)
   tidak lagi saling menghapus saat dedup.
3. **Header `REPAIR` → `REPLACE`** di 8 file Powertrain Disassembly
   (`tools/normalize_decision_headers.py`, 22 sel). Sebelumnya parser tidak
   mengenali kolom ketiga sehingga **Part Request tidak pernah terpicu**.
4. **Parser terima header `PART` tunggal** — tab SUPPLY PUMP DISASSY tadinya
   0 baris.
5. **Deteksi centang jadi daftar-putih** — `N/A`, `OK`, catatan bebas tidak
   lagi dianggap centang (dulu memicu FR palsu).
6. **6 test baru** (`tests/Feature/DecisionScanTest.php`) memakai data sel asli
   dari template SIAP. Fixture dibuat `tools/export_decision_fixtures.py`.

**Wajib sebelum dipakai:** re-deploy Apps Script (Deploy → **New version**),
kalau tidak, `action: read` masih mengembalikan satu tab saja (kode PHP tetap
jalan, cuma kembali ke perilaku lama).

Backup template: `_SIAP_BACKUP/20260726_200906_headers/`.

---

## Current Task (lanjutkan ini)

**Merapikan / menseragamkan semua template Excel di folder SIAP upload** agar otomasi **Fabrication Request (FR)** form **PLO/09/F-021** (`FABRIKASI/FR 2026/`) jalan mulus dari Google Sheets.

Folder target:

```
CHECKSHEET FOR PROCESS DEVELOPMEN ROBBY/ENGINE/_SIAP_UPLOAD_GSHEET/     (~20 file)
CHECKSHEET FOR PROCESS DEVELOPMEN ROBBY/POWERTRAIN/_SIAP_UPLOAD_GSHEET/  (~52 file)
```

**Belum dikerjakan:** formatting massal file `.xlsx` (checkbox decision, perbaikan outlier, re-upload ke GSheet master).  
**Sudah dikerjakan:** spesifikasi standar, audit script, implementasi parser + UI FR di Laravel.

---

## What Has Been Done

### 1. Auto-FR dari Stage 2 (Laravel — implemented)

- Migrasi + model `fabrication_requests`, relasi `Component::fabricationRequests()`
- `FabricationRequestService` — penomoran `FR/SIS/RC/{4digit}/{bulan Romawi}/{tahun}/INT`
- `FabricationRequestController` — scan, store, index, pdf
- Routes di `routes/web.php` (`components/{component}/fr/*`)
- Panel FR di `resources/views/overhauls/show.blade.php` (Stage ≥ 2)
- PDF form PLO/09/F-021: `resources/views/fr/pdf.blade.php`
- Hook Stage 2: decision **Repair** di form internal → auto draft FR
- Migrasi sudah dijalankan: `2026_07_24_100000_create_fabrication_requests_table.php`

### 2. Parser dual-profile GSheet (implemented)

| Kategori | Sheet yang discan | FR trigger | PR trigger |
|----------|-------------------|------------|------------|
| **Engine** | **Disassembly** (`gsheet_url`, subassy disassy) | **SALVAGE** | **REPLACE** |
| **Powertrain** | **Inspection** (`gsheet_measurement_url`) | **U/R** | **R/N** |

File kunci:

- `app/Services/ChecksheetGsheetService.php` — `readPartDecisionRows()`, `parseDisassemblyValues()`, `parseInspectionValues()`
- `app/Services/FabricationRequestService.php` — `scanCandidates()`, buat FR + Part Request
- `tools/gsheet_copy_webapp.gs` — action `read` + `sheet_keywords` (perlu **re-deploy New version**)

### 3. Dokumen & audit template (implemented)

- `tools/siap_decision_standard.md` — standar kolom REUSE/SALVAGE/REPLACE vs U/A/U/R/R/N
- `tools/audit_siap_sheets.py` — audit 72 file → `tools/siap_sheets_audit.json`
- `tools/powertrain_siap_gap_list.md` — gap list powertrain stages

### 4. Temuan audit (ringkas)

**Engine (20 file):**

- Disassembly: header **REUSE | SALVAGE | REPLACE** konsisten (1 sheet, multi-section)
- Measurement: **6–8 tab per workbook**, format **campur** (Good/No Good, New/Reuse, dll.) — **bukan** sumber FR
- Banyak file Disassembly **9–14 MB** (gambar embedded) — audit script skip detail

**Powertrain (52 file):**

- **Inspection (10/10):** seragam **U/A | U/R | R/N** ✅
- **Disassembly (8/10):** REUSE/SALVAGE/REPLACE ✅
- **Outlier:**
  - `Control Valve/D375-6/DISASSEMBLY` — kolom `REPAIR | SALVG | REPAIR` (typo)
  - `Control Valve/HD785-7/DISASSEMBLY` — **tanpa** kolom keputusan
- Receiving/Assembly/Delivery/Test — bukan sumber trigger FR awal

### 5. Keputusan desain (disepakati dengan user)

- Kolom keputusan harus **checkbox** (Google Sheets), bukan input teks bebas
- Engine: keputusan part di **Disassembly**, bukan Measurement
- 1 FR = 1 part; SALVAGE/U/R → FR; REPLACE/R/N → Part Request
- Checkbox di **baris part utama** (NO + PART NAME), bukan sub-baris check point

---

## Current Problem / Blockers

1. **Template SIAP belum diformat** — task formatting folder belum dimulai (user minta lanjut, agent sempat idle/error context besar).
2. **Checkbox belum di-set** di master template (Excel lokal masih cell teks kosong).
3. **Apps Script** `gsheet_copy_webapp.gs` perlu re-deploy agar `action: read` + `sheet_keywords` aktif di production.
4. **File Engine Disassembly sangat besar** — pertimbangkan kompres gambar sebelum upload GSheet.
5. **Banyak perubahan belum di-commit** — lihat `git status` di bawah.

---

## Key Files (FR / GSheet)

| Path | Peran |
|------|--------|
| `app/Services/FabricationRequestService.php` | Penomoran FR, scan/store kandidat |
| `app/Services/ChecksheetGsheetService.php` | Baca & parse GSheet |
| `app/Http/Controllers/FabricationRequestController.php` | API scan/store/pdf |
| `app/Http/Controllers/ComponentController.php` | Hook Stage 2, load FR |
| `resources/views/overhauls/show.blade.php` | Panel Scan Spreadsheet + FR/PR |
| `resources/views/fr/pdf.blade.php` | Output PDF PLO/09/F-021 |
| `tools/gsheet_copy_webapp.gs` | Apps Script webapp (copy/read/upload) |
| `config/checksheet_gsheets.php` | Template ID per EGI |
| `tools/siap_decision_standard.md` | Spec standarisasi template |
| `tools/audit_siap_sheets.py` | Audit otomatis folder SIAP |
| `FABRIKASI/FR 2026/` | 417 PDF contoh FR asli (referensi layout) |

---

## Next Steps Expected (prioritas)

### A. Format template SIAP (task utama user) — **DONE 2026-07-26**

Script `tools/format_siap_templates.py` sudah dijalankan:

- **30 file** diformat (Engine/Powertrain Disassembly + Powertrain Inspection)
- **1016 baris part**, **1332 sel decision** → `FALSE` + dropdown TRUE/FALSE
- Backup: `CHECKSHEET FOR PROCESS DEVELOPMEN ROBBY/_SIAP_BACKUP/{timestamp}/`
- Outlier D375 + HD785 Disassembly diperbaiki

**Sisa manual (Google Sheets):**

1. Upload template ke Drive / update `config/checksheet_gsheets.php` jika perlu
2. Di master GSheet: **Insert → Checkbox** di kolom decision (ganti TRUE/FALSE dropdown)
3. Re-deploy Apps Script `gsheet_copy_webapp.gs`
4. Test scan FR/PR dari UI komponen

### A-old checklist (referensi)

### B. Verifikasi OCMS

```bash
php artisan serve
# Login sebagai Mechanic/Supervisor
# Buka komponen Stage ≥ 2 → Scan Spreadsheet → centang SALVAGE/U/R di GSheet dulu → Simpan FR/PR
```

### C. Commit (jika diminta user)

Perubahan FR belum di-commit. Jangan commit folder `FABRIKASI/`, checksheet besar, atau `.env` tanpa konfirmasi.

---

## Environment

```env
GSHEET_COPY_WEBAPP_URL=...   # Apps Script /exec URL
GSHEET_COPY_SECRET=...       # optional
SESSION_DRIVER=file          # local dev
DB=SQLite (database/database.sqlite)
```

Server dev: `php artisan serve` (sering sudah jalan di terminal).

---

## Git Status (snapshot)

Modified (FR-related + lainnya):

- `app/Services/ChecksheetGsheetService.php`
- `app/Services/FabricationRequestService.php` (new)
- `app/Http/Controllers/FabricationRequestController.php` (new)
- `app/Http/Controllers/ComponentController.php`
- `app/Models/FabricationRequest.php` (new)
- `app/Models/Component.php`
- `routes/web.php`
- `resources/views/overhauls/show.blade.php`
- `resources/views/fr/pdf.blade.php` (new)
- `tools/gsheet_copy_webapp.gs`
- `database/migrations/2026_07_24_100000_create_fabrication_requests_table.php` (new)

Untuk diff lengkap:

```bash
git diff --stat
git diff app/Services/ChecksheetGsheetService.php
```

---

## Commands Berguna

```bash
# Audit template SIAP
python tools/audit_siap_sheets.py

# Migrasi (sudah run)
php artisan migrate

# Routes FR
php artisan route:list --name=components.fr

# Test parser Disassembly (manual, contoh)
python -c "..."  # lihat conversation — parser baca 33 part dari DISASSEMBLY PC1250-8
```

---

## Context yang TIDAK perlu di-paste ke Claude

- Jangan paste full agent transcript (~216k tokens)
- Jangan attach seluruh folder `CHECKSHEET FOR PROCESS DEVELOPMEN ROBBY/` atau `FABRIKASI/` sekaligus
- Cukup: **repo + handoff.md + file spesifik** yang sedang diedit

---

## Referensi FR Asli

Form: **PLO/09/F-021**  
Contoh nomor: `FR/SIS/RC/0475/VII/2026/INT`  
Folder: `FABRIKASI/FR 2026/` (417 PDF)

---

## Agent Transcript (Cursor)

Jika perlu detail percakapan:  
`C:\Users\Administrator\.cursor\projects\c-Users-Administrator-gemini-antigravity-scratch-SISI-OCMS/agent-transcripts/d793d4da-272d-4d4d-8d5b-b3ff50224928/d793d4da-272d-4d4d-8d5b-b3ff50224928.jsonl`

Cari keyword: `Auto-FR`, `SALVAGE`, `audit_siap`, `checkbox`, `PC1250-8`.
