# PLAN: Multi-EGI Engine Receiving Inspection Checksheet

> **Status:** IN PROGRESS  
> **Last Updated:** 2026-07-16 09:19 WIB  
> **Current Step:** Step 5-7 (PDF text extracted, need to parse items & copy images)

---

## GOAL

Saat ini checksheet Engine Receiving Inspection hanya ada **1 template generik** (D375-6, 64 item) yang dipakai untuk **semua model/EGI**. 

Tiap model punya **EG MAINLINE** sendiri (Receiving Inspection ada di halaman-halaman awal dokumen ini) dengan daftar item dan gambar referensi yang **berbeda**. Goal: buat template per-EGI agar saat komponen didaftarkan, otomatis dapat checksheet yang sesuai modelnya.

---

## ARSITEKTUR

### Database
- **`checksheet_templates`** — tambah kolom `egi_model` (nullable) untuk identifikasi template per-model
- **`component_checksheets`** — tidak berubah (tetap `comp_id`, `stage_number`, `items`, `answers`)
- Template lookup: cari berdasarkan `egi_model` dulu → fallback ke `egi_model = NULL` (generik)

### File Penting
| File | Fungsi |
|------|--------|
| `app/Models/ChecksheetTemplate.php` | Model template, fillable: `major_category, egi_model, stage_number, template_name, items` |
| `app/Http/Controllers/ComponentController.php` | Method `store()` line ~136: lookup template saat komponen baru didaftarkan |
| `database/seeders/ChecksheetTemplateSeeder.php` | Seeder untuk inject template items per-EGI |
| `resources/views/overhauls/checksheet.blade.php` | Halaman checksheet fullscreen (slide/daftar view) |
| `resources/views/overhauls/show.blade.php` | Halaman detail komponen dengan inline checksheet |
| `public/images/inspection/` | Gambar referensi visual inspeksi (per model) |

### Slide Reference Image Logic
Di slide view, gambar referensi ditampilkan **di atas nomor item** berdasarkan **nomor urut item** (bukan nama grup). Mapping saat ini hardcoded untuk D375-6:
```javascript
// Di checksheet.blade.php & show.blade.php
function getRefImage(itemNum) {
    if (itemNum >= 1 && itemNum <= 18) return 'right-side-view.png';
    if (itemNum >= 21 && itemNum <= 27) return 'rear-side-view-1.png';
    if (itemNum >= 28 && itemNum <= 53) return 'left-side-view.png';
    if (itemNum >= 54 && itemNum <= 64) return 'rear-side-view-2.png';
    return null;
}
```
**Perlu diubah** → dynamic per EGI, data mapping disimpan di template atau di-pass dari server.

---

## MODEL/EGI YANG DIPROSES

Sumber dokumen yang benar adalah **EG MAINLINE**, bukan checksheet delivery. Bagian "Receiving Inspection" ada di halaman 1-4 dokumen tersebut.

*Note: CAT C32 dan CAT C15 di luar skope karena tidak pakai format EG MAINLINE standar Komatsu.*

---

## PROGRESS CHECKLIST

- [x] Step 1: Install PDF extraction tools (PyMuPDF/fitz)
- [x] Step 2: Create migration `add_egi_model_to_checksheet_templates` → file: `database/migrations/2026_07_16_091230_add_egi_model_to_checksheet_templates_table.php`
- [x] Step 3: Update `ChecksheetTemplate` model → tambah `egi_model` ke `$fillable`
- [x] Step 4: Update `ComponentController::store()` → EGI-specific lookup + fallback
- [x] Step 5: Extract PDF EG MAINLINE untuk D375-6, HD785-7, D155-6, WA800-3, GD825A-2, HD465-7R, PC1250-8, PC2000-8.
- [x] **Step 6: Parse extracted text / images → buat daftar items per model**
  - Karena text extraction PDF berupa gambar (scanned), parse item berdasarkan visual page renders di `scratch/{model}/images/full_page_*.png`
  - Parse nomor, grup (Right Side View / Left Side View / Rear Side View / Front Side View), dan label item
  - Tentukan range nomor item per gambar referensi
- [x] **Step 7: Copy & organize reference images**
  - Dari PDF extracted images → pilih yang benar (gambar engine view, bukan logo)
  - Copy ke `public/images/inspection/{model}/` (e.g. `public/images/inspection/hd785-7/`)
  - Format nama diseragamkan misal: `right-side-view.png`, `left-side-view.png`, `rear-side-view.png`, `front-side-view.png`
  - D375-6 images sudah ada di `public/images/inspection/` → pindah ke `public/images/inspection/d375-6/`
- [x] **Step 8: Update seeder `ChecksheetTemplateSeeder.php`**
  - Tambah `egi_model` ke existing D375-6 entry
  - Fix groups item 21-27 D375-6: Right Side View → Rear Side View
  - Tambah entry baru untuk sisa 7 EGI
  - Setiap entry: `['major_category' => 'Engine', 'egi_model' => 'MODEL', 'stage_number' => 1, ...]`
  - Tambah metadata untuk referensi gambar per grup
- [x] **Step 9: Update views untuk dynamic image path per EGI**
  - Pass logic map range item -> gambar di backend/frontend
  - Update view slide checksheet agar resolve image URL berdasarkan `egi_model` 
- [x] **Step 10: Run migration & seeder**
  - `php artisan migrate`
  - `php artisan db:seed --class=ChecksheetTemplateSeeder`
- [x] **Step 11: Test manual**
  - Register komponen baru EGI=HD785-7 → cek checksheet items sesuai
  - Register komponen baru EGI=D155-6 → cek checksheet items sesuai
  - Cek gambar referensi muncul di slide view sesuai model
- [ ] Step 12: Push ke GitHub

---

## EXTRACTED DATA LOCATIONS

PDF text & images sudah diekstrak ke folder scratch (artifact):
```
C:\Users\ASUS\.gemini\antigravity-ide\brain\badd5cf1-401a-4449-86c5-0f0c13cf0ee2\scratch\
├── extract_pdf.py          # Script Python untuk ekstrak PDF
├── d375-6/
│   ├── raw_text.txt        # Text content dari PDF
│   └── images/             # Extracted images & full page renders
├── hd785-7/
│   ├── raw_text.txt
│   └── images/
├── d155-6/
│   ├── raw_text.txt
│   └── images/
└── wa800-3/
    ├── raw_text.txt
    └── images/
```

### Cara Baca Data
1. Buka `raw_text.txt` untuk masing-masing model
2. Parse daftar item: cari pola `nomor. NAMA_KOMPONEN` atau tabel checksheet
3. Identifikasi grup view dari header di PDF (RIGHT SIDE VIEW, LEFT SIDE VIEW, REAR SIDE VIEW)
4. Lihat `images/full_page_1.png` dan `full_page_2.png` untuk visual referensi
5. Pilih gambar engine view yang bersih dari `images/page*_img*.png`

---

## CATATAN TEKNIS

### Format Items di Seeder
```php
['id' => 'RCV-001', 'group' => 'Right Side View', 'label' => 'Turbocharger (P/N: xxx)']
```
- `id`: format `RCV-{3digit}`, harus unique per template
- `group`: `Right Side View`, `Left Side View`, `Rear Side View` (sesuai PDF)
- `label`: nama komponen dari PDF

### Reference Image di Slide
Gambar muncul di atas nomor item (#01, #02, dst) sebagai thumbnail (240px). Klik untuk zoom (lightbox).
Mapping saat ini berdasarkan `currentIndex + 1` (nomor item), bukan nama grup.

### Template Lookup di Controller
```php
// File: app/Http/Controllers/ComponentController.php, line ~136
// 1. Cari template EGI-specific
$template = ChecksheetTemplate::where('major_category', $cat)
    ->where('stage_number', 1)
    ->whereRaw('UPPER(egi_model) = ?', [strtoupper($egi)])
    ->first();
// 2. Fallback ke generik
if (!$template) {
    $template = ChecksheetTemplate::where('major_category', $cat)
        ->where('stage_number', 1)
        ->whereNull('egi_model')
        ->first();
}
```
