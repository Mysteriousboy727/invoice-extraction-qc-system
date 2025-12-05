# Quick Start Guide

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install frontend dependencies (optional):**
   ```bash
   cd frontend
   npm install
   ```

## Running the CLI

From the `invoice_qc_service` directory:

```bash
# Extract invoices from PDFs
python -m invoice_qc.cli extract --pdf-dir pdfs --output extracted.json

# Validate invoices
python -m invoice_qc.cli validate --input extracted.json --report report.json

# Full run (extract + validate)
python -m invoice_qc.cli full-run --pdf-dir pdfs --report report.json
```

## Running the API

```bash
uvicorn api.app:app --reload
```

API will be available at `http://localhost:8000`

## Running the Frontend

```bash
cd frontend
npm run dev
```

Frontend will be available at `http://localhost:3000`

## Running Tests

```bash
pytest tests/
```

