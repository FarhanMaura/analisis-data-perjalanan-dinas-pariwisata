<!-- Copilot / AI contributor instructions for 'analisis-data-perjalanan-dinas-pariwisata' -->

# Project Snapshot

This is a small Flask application for ingesting tourism CSV/PDF reports, storing them in a local SQLite DB (`tourism.db`), generating analytics (including ML-driven suggestions), rendering charts, and exporting Excel reports.

Key runtime behavior:
- Web server entrypoint: `app.py` (runs `init_db()` and `app.run(debug=True)` when executed).
- Uploaded files saved to `uploads/` (created at startup if missing).
- Database: SQLite file `tourism.db` in repo root. Tables created: `tourism_data`, `uploaded_files`.

**Primary components (files)**
- `app.py` — Flask routes, I/O, Excel export logic (openpyxl + matplotlib images), and chart image generation helpers.
- `data_processor.py` — CSV validation and ingestion logic; canonical place for CSV parsing rules.
- `pdf_processor.py` — PDF extraction using `pdfplumber`; maps Indonesian month names to English months.
- `ml_analysis.py` — `TourismAnalyzer` encapsulates ML/heuristics: pattern discovery, seasonal analysis, and suggestion generation.
- `chart_generator.py` — JSON-ready chart payloads for front-end charts; optionally uses `TourismAnalyzer`.
- `utils.py` & `config.py` — helpers, logging, constants (eg. `UPLOAD_FOLDER`, `DATABASE`, `MAX_CONTENT_LENGTH`).
- `templates/` — Jinja templates for UI: `index.html`, `upload.html`, `upload_pdf.html`, `dashboard.html`.

## Big Picture & Data Flow
- Upload (CSV or PDF) → saved to `uploads/` → `DataProcessor` / `PDFProcessor` extracts Palembang rows and monthly values → writes into `tourism_data` table (year, month, value) and records filename/year into `uploaded_files`.
- `TourismAnalyzer` reads `tourism_data` from SQLite and returns JSON-serializable `patterns`, `summary`, `data_quality`, and `suggestions` used by the dashboard and chart generator.
- `ChartGenerator` consumes the same DB-derived dataframe and returns chart payloads used by `/api/advanced-chart-data` and the UI.
- `/export-excel` (in `app.py`) composes an Excel workbook with raw data, ML analysis, charts (matplotlib images embedded via `openpyxl`) and statistics.

## Project-specific conventions & patterns (important for agents)
- Month names in the DB and code are English full names: `January`..`December`. PDF extraction maps Indonesian month names to these English names.
- CSV detection looks specifically for the string `Palembang` in the first column (or any cell in a row). Many CSV paths assume the Palembang row contains monthly numbers.
- Year validation: `utils.validate_year()` allows 2000..(current_year + 1). Use this when inferring year from filenames or forms.
- DB path is defined in `config.Config.DATABASE` (defaults to `tourism.db`). Many modules instantiate with the same default string; prefer using `Config` when modifying code.
- ML suggestions include emoji and Indonesian text; do not normalize or strip emojis when returning suggestions to the UI.

## Integration points & external deps
- Local filesystem: `uploads/`, `backups/`, `tourism_analysis.log` (created by `utils.setup_logging()`).
- SQLite database: `tourism.db` (no external DB server).
- Python libraries used in code but not all present in `requirements.txt`: `openpyxl`, `matplotlib`, `pdfplumber`, and `openpyxl.drawing.image`. Ensure these are installed for Excel export and PDF parsing.

Minimal dev setup (commands)
- Create venv and install deps:
```
python -m venv .venv
source .venv/Scripts/activate   # Windows (bash.exe)
pip install -r requirements.txt
pip install openpyxl matplotlib pdfplumber
```
- Run locally:
```
python app.py
# server available at http://127.0.0.1:5000
```

Quick debug / inspection tips
- Check `tourism.db` with `sqlite3 tourism.db` or DB browser to inspect `tourism_data` and `uploaded_files`.
- Check `tourism_analysis.log` for runtime logs (created by `utils.setup_logging`).
- If PDF uploads fail, look into `pdf_processor.py` — it expects certain keywords (`bulan`, `nusantara`, `manca`) and maps Indonesian months to English.
- For CSV ingestion issues, inspect `DataProcessor.validate_csv_structure()` and `process_csv_data()`; they attempt multiple header formats (multi-row headers) and search for month-name-like columns.

APIs & routes useful for automated agents
- `GET /api/chart-data` — simple chart payloads used on the dashboard.
- `GET /api/advanced-chart-data` — ChartGenerator JSON payloads.
- `GET /api/analysis-data` — ML analysis suggestions/patterns.
- `GET /api/db-stats` — quick DB statistics (record counts, years, last update).
- `POST /convert-pdf-to-csv` — convert uploaded PDF to CSV and return as file download.

Notes for pull requests and edits
- Preserve Indonesian user-facing strings unless requested otherwise.
- When changing DB schema, update `init_db()` in `app.py` and check all places that `SELECT`/`INSERT` into `tourism_data` and `uploaded_files`.
- When adding dependencies, update `requirements.txt` and mention why (e.g., `pdfplumber` for PDF parsing, `openpyxl` for Excel export).

If anything in this summary is unclear or you want more detail about a specific component (CSV formats, PDF parsing heuristics, or Excel export embedding), tell me which part to expand and I will update this file. 
