# Troubleshooting Guide

## Network Error When Uploading Files

### Problem
Getting "Network Error" or "Cannot connect to backend server" when uploading files in the frontend.

### Solution

#### Step 1: Check if Backend is Running

Open a terminal and run:
```bash
cd invoice_qc_service
python run_api.py
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

#### Step 2: Verify API is Accessible

Open your browser and go to:
```
http://localhost:8000/health
```

You should see:
```json
{"status":"ok"}
```

If you get an error, the backend is not running correctly.

#### Step 3: Check Port Conflicts

Make sure port 8000 is not being used by another application:
```bash
# Windows PowerShell
netstat -ano | findstr :8000

# If something is using it, either:
# 1. Stop that application
# 2. Or change the port in run_api.py
```

#### Step 4: Verify Frontend is Connecting to Correct URL

The frontend is configured to connect to `http://localhost:8000`. Make sure:
- Backend is running on `localhost:8000` (not `127.0.0.1:8000` or another port)
- No firewall is blocking the connection
- Both frontend and backend are on the same machine

#### Step 5: Check CORS Configuration

The backend has CORS enabled, but if you're still having issues:

1. Make sure `python-multipart` is installed:
   ```bash
   pip install python-multipart
   ```

2. Restart the backend server after installing

### Common Issues

#### Issue: "Connection Refused"
**Cause**: Backend is not running
**Fix**: Start the backend with `python run_api.py`

#### Issue: "Timeout"
**Cause**: PDF processing is taking too long or backend is slow
**Fix**: 
- Check backend logs for errors
- Try with a smaller PDF file
- Increase timeout in frontend (already set to 60s for PDFs)

#### Issue: "CORS Error"
**Cause**: CORS middleware not working
**Fix**: 
- Make sure CORS middleware is added in `api/app.py`
- Restart the backend server
- Check browser console for specific CORS error

#### Issue: "File Type Not Recognized"
**Cause**: Browser not detecting file type correctly
**Fix**: 
- The code now checks file extension (`.pdf`, `.json`) as fallback
- Make sure file has correct extension

### Quick Test

1. **Test Backend**:
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"ok"}`

2. **Test Frontend Connection**:
   - Open browser console (F12)
   - Check for any errors
   - Try uploading a small JSON file first

3. **Test with Sample Data**:
   - Use `sample_invoice.json` from the project
   - Upload it through the frontend
   - Should work if backend is running

### Still Having Issues?

1. Check backend terminal for error messages
2. Check browser console (F12) for detailed error
3. Verify all dependencies are installed: `pip install -r requirements.txt`
4. Make sure `python-multipart` is installed for file uploads



