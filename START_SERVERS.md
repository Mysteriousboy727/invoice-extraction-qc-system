# Commands to Start Backend and Frontend

## Option 1: Run in Separate Terminals (Recommended)

### Terminal 1 - Backend (API Server)

```powershell
# Navigate to project directory
cd invoice_qc_service

# Start the API server
python run_api.py
```

**OR**

```powershell
uvicorn api.app:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at: `http://localhost:8000`

### Terminal 2 - Frontend (React App)

```powershell
# Navigate to frontend directory
cd invoice_qc_service\frontend

# Install dependencies (first time only)
npm install

# Start the development server
npm run dev
```

The frontend will be available at: `http://localhost:3000`

---

## Option 2: Quick Start Scripts

### Start Backend Only

```powershell
cd invoice_qc_service
python run_api.py
```

### Start Frontend Only

```powershell
cd invoice_qc_service\frontend
npm run dev
```

---

## Verify Everything is Running

1. **Backend Health Check:**
   ```powershell
   # In a new terminal or browser
   curl http://localhost:8000/health
   # OR open in browser: http://localhost:8000/health
   ```

2. **Frontend:**
   - Open browser: `http://localhost:3000`
   - You should see the Invoice QC Service interface

---

## Troubleshooting

- **Backend not starting?** Make sure port 8000 is not in use
- **Frontend not starting?** Make sure you ran `npm install` first
- **CORS errors?** Make sure backend is running on port 8000

