# SIS-OCMS (Plant Rebuild Center) - Project Context & Status
*Last Updated: 2026-07-17*

**NOTE TO OTHER AI AGENTS:** 
Read this file first to quickly understand the project architecture, current progress, and pending issues.

## 1. Project Overview
This project is an **Overhaul Component Management System (OCMS)** for PT Sapta Indra Sejati (SIS) Plant Rebuild Center. It tracks the overhaul process of heavy equipment components (Engine, TC/Transmission, Final Drive, Differential, PTO, Swing Machinery, Control Valve, etc.) across 7 stages:
1. Receiving (Penerimaan DC)
2. Disassembling
3. Machining & Fabrication
4. Assembly
5. Test Performance
6. Painting
7. RFU / Delivery

## 2. Tech Stack
- **Backend:** Laravel (PHP 8+)
- **Frontend:** Blade Templates, JavaScript (Vanilla), Custom CSS (`index.css` for aesthetic, glassmorphism UI)
- **Database:** MySQL / SQLite (accessed via Eloquent ORM)
- **Features:** Dynamic form inputs, QR Code generation per component, PDF to image checksheet referencing.

## 3. Core Architecture
- **`Component` Model:** The main entity tracking a registered component (EGI, Serial Number, Category, Status).
- **`ChecksheetTemplate` Model:** Stores the baseline inspection items (JSON format) for a specific `major_category` and `egi_model` at a specific `stage_number`.
- **`Checksheet` Model:** When a component enters a new stage (e.g., Stage 1: Receiving), the system clones the `ChecksheetTemplate` items into a `Checksheet` record tied to the `Component`.
- **Controllers:** 
  - `ComponentController.php`: Handles registration and auto-attaches templates based on `major_category` and `egi_model`. If an `egi_model` is not explicitly templated, it falls back to a generic template where `egi_model = null`.
- **Views:**
  - `create.blade.php`: Uses JS to dynamically populate the EGI dropdown based on the chosen `major_category`.
  - `show.blade.php`: The interactive slider checksheet UI. It automatically maps the active component to a reference image extracted from original PDF SOPs (stored in `public/images/inspection/`).

## 4. Current Status & Recent Work
**Feature:** Multi-EGI Powertrain Receiving Checksheet (Stage 1).
- **Engine Checksheets:** Fully completed (PC2000-8, PC1250-8, D375-6, D155-6, WA800-3, GD825A-2, HD785-7, HD465-7R). Exact items extracted from PDFs.
- **Powertrain Checksheets:** Infrastructure for TC/Transmission, Final Drive, Differential, PTO, Swing Machinery, and Control Valve is fully integrated.
  - Form logic and badge indicators updated.
  - Reference images for all powertrain checksheet documents successfully extracted from `002. CHECKSHEET KOMPONEN` and mapped to `/images/inspection/{egi}/{category}.png`.

## 5. Known Problems & Pending Tasks (IMPORTANT)
**Problem:** Missing Exact Text Items for Image-Based Powertrain PDFs.
- For Powertrain components, the original PDF checksheets provided by the user are **scanned images with NO text layers** (except for `WA800-3 TC/Transmission` and `HD785-7 Differential` which were successfully parsed).
- Because automated text extraction (pdfplumber/PyMuPDF) failed on the scanned PDFs, and OCR agents were out of quota, **Generic Checksheet Templates** (4-6 basic items) were seeded into the database for the unreadable models (e.g., D155-6 Final Drive, D375-6, PC1250-8, etc.).
- **Pending Fix:** The user wants the exact, original items from the SOPs for ALL powertrain components. This requires either:
  1. Running OCR (Tesseract / Vision API) on the PDFs in `002. CHECKSHEET KOMPONEN/` to extract the item strings.
  2. The user providing a typed list of the items.
  *(Once the text is obtained, update the arrays in `ChecksheetTemplateSeeder.php` and run `php artisan db:seed --class=ChecksheetTemplateSeeder`.)*

**Minor Notice:**
- `HD1500-7 Rear Axle` was skipped for Receiving Inspection because its source PDF only contained "Disassembly" items.

## 6. Key Directories
- `database/seeders/ChecksheetTemplateSeeder.php` -> Master data for all checksheets.
- `resources/views/overhauls/create.blade.php` -> Component registration UI.
- `resources/views/overhauls/show.blade.php` -> Checksheet slider UI and Reference Image logic (`csGetRefImage`).
- `scratch_extracted_items.json` -> Temporary dump of successfully extracted PDF text.
- `002. CHECKSHEET KOMPONEN/` -> Source folder containing all the original PDF SOPs. (Excluded from git tracking).
