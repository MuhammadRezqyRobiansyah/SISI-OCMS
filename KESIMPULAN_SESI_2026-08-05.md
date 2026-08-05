# Kesimpulan Sesi — SISI-OCMS

Tanggal: 5–6 Agustus 2026
Lingkup: penerapan laporan test (`LAPORAN_TEST_PROYEK.txt`), perubahan UI FR/MOL, audit checksheet lokal + Google Sheets online, upload template Assembly/Testbench semua EGI.

---

## 1. Fix keamanan (dari laporan test, semua diterapkan)

| Temuan | Perbaikan | File |
|---|---|---|
| S-1: `saveAnswer` tanpa cek role | Dibatasi Mechanic/Supervisor/SuperAdmin + `item_id` divalidasi terhadap item checksheet (id ngawur tidak lagi menaikkan progress) | `app/Http/Controllers/ChecksheetController.php` |
| S-2: FR `edit`/`update` tanpa cek role | Dibatasi Mechanic/Supervisor/SuperAdmin (abort 403) | `app/Http/Controllers/FabricationRequestController.php` |
| S-3: PR `updateStatus` tanpa cek role | Dibatasi Mechanic/Supervisor/SuperAdmin | `app/Http/Controllers/PartRequestController.php` |
| S-4: Registrasi publik terbuka | `Features::registration()` Fortify dimatikan — user baru hanya lewat Admin → Users | `config/fortify.php` |

Catatan operasional:
- **O-1 (queue)**: tabel jobs kosong (tidak ada yang menumpuk). Queue worker dinyalakan (`php artisan queue:work`) — **mati saat PC restart, jalankan lagi manual** agar duplikasi GSheet stage 4/5 berjalan.
- **P-2 (race condition nomor FR)**: sudah diperbaiki sesi sebelumnya (`DB::transaction` + `lockForUpdate`) — tidak perlu diubah.
- **O-3**: `APP_DEBUG=true` dibiarkan karena masih local dev. Wajib `false` bila dipakai di luar dev.

## 2. Perubahan UI / fitur

- **Panel FR**: kolom **Jenis** & **Sumber** dihapus dari tabel FR (`resources/views/overhauls/show.blade.php`).
- **Tab MOL**: kolom **P/N, Kode Order, Qty** dihapus (tinggal Part, Section, Status) — nilai-nilai itu bukan hasil scan (P/N kosong, Kode Order selalu "A", Qty selalu 1).
- **Export MOL PDF dihapus total**: tombol di tab MOL & form MOL, route `components.mol.pdf`, method `molPdf`, `MolExportService::exportPdf`, view `mol/pdf.blade.php`. Pengganti: **upload dokumen MOL manual** (PDF/JPG/PNG) yang sudah ada di tab MOL.
- **Approval GL stage 3/4/5**: sudah terpasang di backend (`updateStage` menahan stage 2–5 dengan `is_waiting_approval`; panel Approve/Tolak Management berlaku untuk semuanya). Stage 1 & 6 lanjut otomatis. Label tombol dirapikan: stage non-approval kini "Selesaikan Tahap & Lanjut", bukan "Ajukan Approval".

## 3. Test suite

- Test scaffold bawaan starter kit dihapus: `tests/Feature/Auth`, `Teams`, `Settings`, `ProfileTest`, `DashboardTest`, `ExampleTest`.
- Test export MOL PDF dihapus dari `FrMolFormTest` (fiturnya dihapus).
- Hasil akhir: **72/72 test lulus (756 assertion)** — sebelumnya 146 test dengan 72 gagal scaffold.

## 4. Cek data asli lokal (31 komponen)

- **Belum ada komponen melewati stage 3** → belum pernah ada data nyata stage 4–7 (assembly, test bench, foto painting, delivery).
- 2 komponen menunggu approval Management: ID 1 (VJ-634870) & ID 26 (SN 142), keduanya stage 2.
- ID 1 & ID 4 tidak punya checksheet sama sekali (dibuat sebelum seeder template ada); sistem membuatkan otomatis saat halaman review dibuka.
- Template checksheet Delivery (stage 7) hanya ada untuk EGI SA12V140E-1 (seeder) — EGI lain di stage 7 tidak akan punya checksheet delivery.
- Komponen demo terlengkap: **ID 27** (Control Valve D155-6, stage 3, 6 FR, 1 PR, dokumen MOL terupload).
- Data uji tidak valid: ID 2 (EGI "FGH"); ID 18 (HD465-7R) tidak punya GSheet karena EGI-nya tidak ada di config.

## 5. Audit checkbox keputusan

**Template lokal (457 file xlsx, read-only):** 0 masalah kritis, 0 file rusak. Semua sumber FR/PR lengkap: Engine disassembly + subassy (REUSE/SALVAGE/REPLACE), Powertrain inspection (U/A, U/R, R/N).

**Master GSheet online (20 spreadsheet, via action `read`):** semua kolom keputusan sudah ber-checkbox — termasuk REUSE. Temuan minor:
- Tab **COMPRESSOR DISASSY** di subassy **GD825A** dan **D375-6/PC1250-8** tidak punya kolom keputusan — bawaan desain template (versi WA800-3 punya). Part compressor dua engine itu tidak bisa menghasilkan FR dari scan.
- `DISASSEMBLY Control Valve HD785-7.xlsx` lokal tanpa kolom keputusan (bukan sumber FR — inspection-nya lengkap; kemungkinan ter-revert saat restore backup).

Tool baru untuk audit ulang kapan saja:
```bash
php tools/audit_gsheet_checkboxes.php              # semua 20 master
php tools/audit_gsheet_checkboxes.php "HD785-7"    # filter EGI/label
```

## 6. Upload Assembly (stage 4) & Testbench (stage 5) — semua EGI

Masalah yang ditemukan: config hanya punya key `SA12V140E-1` (nama model engine), padahal lookup `templateIdFor` memakai **EGI unit** komponen → komponen nyata tidak pernah dapat GSheet stage 4/5. Sudah diperbaiki: 17 spreadsheet baru diupload, config dipetakan ke EGI unit.

**Engine (mainline):**

| Engine → EGI unit | Assembly | Testbench |
|---|---|---|
| SA12V140E-1 → WA800-3 | OK (alias baru) | OK (alias baru) |
| SAA12V140E-3 → PC2000-8 | TIDAK ADA (file .doc Word) | OK baru |
| SAA6D140E-5 → D155-6 | OK baru (konversi .xls via Excel COM) | OK baru |
| SAA6D170E-5 → D375-6, PC1250-8 | OK baru (konversi .xls via Excel COM) | OK baru |
| SA6D140E-2 → GD825A-2 | TIDAK ADA (file .doc) | **TIDAK ADA (file tidak pernah ada)** |

**Powertrain:** 12 ASSEMBLY terupload (Control Valve 7 EGI, Front/Rear Suspension, Hydraulic Cylinder HD785-7) + 2 TEST (CV PC1250-8, PC2000-8).

Tool:
- `tools/upload_engine_stage_gsheets.php` (baru) — upload engine + alias EGI unit.
- `tools/upload_powertrain_gsheets.php` — diperluas: ASSEMBLY/TEST kini ikut masuk config (dulu hanya DISASSEMBLY/INSPECTION).

Catatan: koneksi ke Google sempat putus-putus; kemungkinan ada 1–2 duplikat "ASSEMBLY Front Suspension HD785-7" di Drive dari percobaan gagal (config menunjuk yang terakhir; sisanya boleh dihapus manual).

## 7. Step yang benar-benar belum ada filenya (gap, perlu dibuat manual)

1. **Engine GD825A-2**: testbench tidak ada; assembly hanya `.doc` (juga assembly PC2000-8).
2. **Powertrain TEST**: hanya CV PC1250-8 & PC2000-8. CV lain + Front/Rear Suspension + Hydraulic Cylinder tidak punya file TEST.
3. **Kategori lain** (TC/Transmission, Final Drive, Differential, PTO, Swing Machinery): tidak ada template SIAP stage 4/5 sama sekali. Bahan mentah di luar SIAP yang bisa dinormalisasi: `Checksheet test performance TM GD825A-2`, torque flow HD785-7/HD1500/WA800-3, power module D155A-6/D375A-6R, assembly+test FD HD785-7.
4. Kolom keputusan tab COMPRESSOR DISASSY (GD825A & D375-6/PC1250-8) — tambah via Excel COM + re-upload, atau langsung di GSheet master + `apply_checkboxes`.
5. Seeder Delivery (stage 7) baru mencakup SA12V140E-1 — perlu EGI lain / template generik.

## 8. Yang perlu diingat saat menjalankan

```bash
php artisan queue:work        # WAJIB jalan untuk duplikasi GSheet stage 4/5
php artisan test              # 72/72 hijau (~9 menit di mesin ini)
php tools/audit_gsheet_checkboxes.php   # audit checkbox master GSheet
```

Registrasi publik sudah ditutup — buat user lewat menu Admin → Users (SuperAdmin).
