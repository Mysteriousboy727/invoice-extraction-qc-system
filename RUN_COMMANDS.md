# Commands to Run the Project

## Step 1: Install Dependencies

```bash
# Navigate to project directory
cd invoice_qc_service

# Install Python dependencies
pip install -r requirements.txt

# (Optional) Install package in development mode
pip install -e .
```

## Step 2: Run the CLI Tool

```bash
# Show help
python -m invoice_qc.cli --help

# Extract invoices from PDFs
python -m invoice_qc.cli extract --pdf-dir pdfs --output extracted.json

# Validate invoices from JSON
python -m invoice_qc.cli validate --input sample_invoice.json --report report.json

# Full run (extract + validate)
python -m invoice_qc.cli full-run --pdf-dir pdfs --report report.json
```

## Step 3: Run the API Server

```bash
# Option 1: Using the run script
python run_api.py

# Option 2: Using uvicorn directly
uvicorn api.app:app --reload

# Option 3: With custom host/port
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: `http://localhost:8000`

Test it:
```bash
# Health check
curl http://localhost:8000/health

# Or open in browser
# http://localhost:8000/health
```

## Step 4: Run the Frontend (Bonus)

Open a **new terminal** and run:

```bash
# Navigate to frontend directory
cd invoice_qc_service/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

The frontend will be available at: `http://localhost:3000`

## Step 5: Run Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_validator.py
```

## Quick Test Commands

```bash
# Test validation with sample data
python -m invoice_qc.cli validate --input sample_invoice.json --report test_report.json

# Check API health
curl http://localhost:8000/health
```

