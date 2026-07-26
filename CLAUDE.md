# CLAUDE.md — SISI-OCMS

Laravel app untuk **Overhaul Component Management System (OCMS)** — workflow overhaul komponen Engine/Powertrain (stage 1–7), checksheet Google Sheets, dan otomasi **Fabrication Request (FR)** form **PLO/09/F-021**.

**Status detail & riwayat sesi:** baca `handoff.md` sebelum task besar.

---

## Stack & dev

- **PHP / Laravel**, SQLite (`database/database.sqlite`), DomPDF
- Dev: `php artisan serve`, `SESSION_DRIVER=file`
- GSheet: Apps Script webapp → `GSHEET_COPY_WEBAPP_URL`, `GSHEET_COPY_SECRET` di `.env`
- RBAC: Mechanic, Supervisor, SuperAdmin (FR scan/store); Management (approval stage)

```bash
php artisan migrate
php artisan route:list --name=components.fr
php artisan test --filter=DecisionScanTest
python tools/verify_siap_state.py
```

---

## Fitur utama: Auto-FR Stage 2

| Kategori | Spreadsheet | Kolom keputusan | → FR | → PR |
|----------|-------------|-----------------|------|------|
| **Engine** | Disassembly (`gsheet_url`, subassy disassy) | REUSE / **SALVAGE** / REPLACE | SALVAGE | REPLACE |
| **Powertrain** | Inspection (`gsheet_measurement_url`) | U/A / **U/R** / R/N | U/R | R/N |

- **1 FR = 1 part** — nomor: `FR/SIS/RC/{4digit}/{bulan Romawi}/{tahun}/INT`
- Parser **dinamis**: cari header teks, **bukan** posisi kolom tetap (U vs W vs R OK)
- **Multi-tab**: semua tab yang cocok keyword (`inspeksi`, `disassy`, `engine`, …) dibaca; nama tab disimpan di kolom `section` (FR/PR)
- Form internal (tanpa GSheet): Repair → FR, Replace → PR

### File kunci

| Path | Peran |
|------|--------|
| `app/Services/FabricationRequestService.php` | Penomoran FR, scan/store kandidat |
| `app/Services/ChecksheetGsheetService.php` | Baca GSheet, parse disassembly/inspection |
| `app/Http/Controllers/FabricationRequestController.php` | scan, store, pdf |
| `app/Http/Controllers/ComponentController.php` | Stage 2 hook, show |
| `resources/views/overhauls/show.blade.php` | Panel Scan Spreadsheet |
| `resources/views/fr/pdf.blade.php` | PDF PLO/09/F-021 |
| `tools/gsheet_copy_webapp.gs` | Apps Script: copy, upload, **read** (multi-tab) |
| `config/checksheet_gsheets.php` | Template ID per EGI |
| `tests/Feature/DecisionScanTest.php` | Test parser dengan fixture SIAP |

---

## Template Excel SIAP

Folder (jangan attach seluruh folder ke chat — terlalu besar):

```
CHECKSHEET FOR PROCESS DEVELOPMEN ROBBY/ENGINE/_SIAP_UPLOAD_GSHEET/
CHECKSHEET FOR PROCESS DEVELOPMEN ROBBY/POWERTRAIN/_SIAP_UPLOAD_GSHEET/
```

Spesifikasi: `tools/siap_decision_standard.md`

### Aturan penting

1. **JANGAN** simpan/edit template `.xlsx` dengan **openpyxl** — merusak gambar EMF/WMF (file 14 MB → 85 KB). Skrip openpyxl diblokir kecuali `--force`.
2. Edit header template hanya lewat **Excel COM**: `tools/normalize_headers_excel.ps1`
3. **Engine Measurement** = data ukuran saja — **bukan** sumber FR
4. Centang keputusan di **baris part** (NO + nama part), bukan sub-baris check point
5. Di Google Sheets master: **Insert → Checkbox** di kolom decision; sel kosong = tidak dicentang (OK)

### Verifikasi template

```bash
python tools/verify_siap_state.py          # target: MASALAH (0)
python tools/inspect_xlsx_damage.py        # target: rusak 0/72
python tools/audit_siap_sheets.py          # audit struktur → siap_sheets_audit.json
```

Backup template: `CHECKSHEET FOR PROCESS DEVELOPMEN ROBBY/_SIAP_BACKUP/`

---

## Apps Script (wajib re-deploy setelah ubah)

1. Paste `tools/gsheet_copy_webapp.gs` → Code.gs
2. Deploy → **New version** → `/exec` URL ke `.env`
3. Action `read` harus mengembalikan **semua tab** yang cocok keyword (bukan satu tab saja)

---

## Konvensi kode

- Route model binding komponen: `comp_id` (bukan `id`)
- FR model: `fr_id`
- Minimize scope — jangan refactor unrelated
- **Jangan commit** kecuali user minta: `.env`, folder checksheet besar, `FABRIKASI/`
- Jangan buat file markdown baru kecuali diminta

---

## Next steps (prioritas)

1. **Re-deploy Apps Script** (multi-tab read) jika belum
2. **Upload template SIAP** ke GSheet master + update `config/checksheet_gsheets.php` jika ID berubah
3. **Insert → Checkbox** di kolom decision di master GSheet
4. **Test E2E**: komponen Stage ≥ 2 → Scan Spreadsheet → centang SALVAGE/U/R → Simpan FR/PR → download PDF
5. Commit perubahan FR (uncommitted) jika user minta

---

## Referensi FR asli

- Form: **PLO/09/F-021**
- Contoh: `FABRIKASI/FR 2026/` (417 PDF — referensi layout, jangan commit semua)

---

## Prompt singkat untuk sesi baru

```
Baca handoff.md dan CLAUDE.md. Lanjutkan SISI-OCMS Auto-FR dari Next Steps.
Jangan edit template xlsx dengan openpyxl. Parser kolom dinamis — posisi REUSE beda per file itu normal.
```
