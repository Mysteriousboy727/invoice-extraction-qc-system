# Invoice QC Service - Frontend

A modern React + Vite frontend for the Invoice Quality Control Service.

## Features

✅ **File Upload**: Upload PDF or JSON files  
✅ **Invoice Table**: View all invoices with detailed information  
✅ **Status Badges**: VALID / INVALID badges with color coding  
✅ **Error Display**: Expandable error lists for each invoice  
✅ **Filtering**: Toggle to show only invalid invoices  
✅ **Summary Dashboard**: Real-time validation statistics  
✅ **Modern UI**: Beautiful Tailwind CSS design  
✅ **Responsive**: Works on desktop and mobile  

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Open in browser:**
   ```
   http://localhost:3000
   ```

## Usage

1. **Start the backend API first:**
   ```bash
   # In the project root
   python run_api.py
   ```

2. **Upload a file:**
   - Click "Choose File (PDF or JSON)"
   - Select a PDF or JSON file
   - Wait for processing

3. **View results:**
   - See validation summary at the top
   - Browse invoices in the table
   - Click on error counts to see details
   - Use filter to show only invalid invoices

## API Endpoints Used

- `POST /validate-json` - Validate JSON invoices
- `POST /extract-and-validate-pdfs` - Extract and validate PDF invoices

## Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

