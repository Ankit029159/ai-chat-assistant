# 🛠️ Troubleshooting Guide

## Quick Reference

### ✅ Everything is Working!
If you see the medical chatbot running at http://localhost:3001, everything is fine!

---

## Common Issues & Solutions

### Issue 1: "Port 8000 Already in Use"

**Problem:** Backend won't start because port 8000 is occupied

**Solution:**
```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Try starting backend again
python app.py
```

**Alternative:** Change port in `app.py`:
```python
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)
```

---

### Issue 2: "Port 3000 Already in Use" (Frontend)

**Problem:** React dev server can't start on port 3000

**Solution:** React already offers to use 3001 automatically - just press `y` when asked

**Manual Change:**
```bash
cd frontend
PORT=3002 npm start
```

---

### Issue 3: "ModuleNotFoundError" or "ImportError"

**Problem:** Python packages not found even though we installed them

**Solution:**
```powershell
# Reinstall all dependencies
cd backend
python -m pip install -r requirements.txt

# Specifically reinstall problematic packages
python -m pip install langchain-openai langchain-text-splitters python-multipart
```

---

### Issue 4: "Cannot GET /" at http://localhost:3001

**Problem:** Frontend isn't loading

**Solution:**
```powershell
# Kill existing React process
Get-Process node | Stop-Process -Force

# Reinstall dependencies
cd frontend
rm -r node_modules
npm install

# Start fresh
npm start
```

---

### Issue 5: Backend Returns "No API Key"

**Problem:** "GEMINI_API_KEY" not set error

**Solution:**
1. Check if `.env` file exists in `backend/` folder
2. Verify it contains: `GEMINI_API_KEY=AIzaSyAvK2rnndb4QGhuME-VHqTRoOxEtatdTb4`
3. Restart Python: `python app.py`

---

### Issue 6: "Gemini API Error 401"

**Problem:** API key is invalid or expired

**Solution:**
1. Get a new API key from: https://makersuite.google.com/app/apikey
2. Update `.env`: `GEMINI_API_KEY=your_new_key_here`
3. Restart backend: `python app.py`

---

### Issue 7: Chat Gets No Response

**Problem:** Backend returns empty response

**Possible Causes:**
- Gemini API rate limited → Wait 60 seconds
- Gemini API key invalid → Update and restart
- Network issue → Check internet connection
- Backend crashed → Restart `python app.py`

**Solution:**
```powershell
# Check backend is running
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get

# If not responding, kill and restart
Get-Process python | Stop-Process -Force
cd backend
python app.py
```

---

### Issue 8: "Cannot Resolve Import" Errors in VS Code

**Problem:** Red squiggles for `fastapi`, `chromadb`, etc.

**This is NOT an error** - it's just VS Code not finding the Python environment

**Solution (optional):**
1. Press `Ctrl + Shift + P`
2. Search: "Python: Select Interpreter"
3. Choose your Python installation (e.g., "Python 3.13.0")
4. Wait 30 seconds for Pylance to re-index

---

## Verification Commands

### Test Backend Health
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get
# Should return: {"status": "ok"}
```

### Test Chat Endpoint
```powershell
$body = @{message="Hello"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/chat" -Method Post -Body $body -ContentType "application/json"
# Should return: {"reply": "...", "sources": [...], "disclaimer": "..."}
```

### Test Gemini API
```powershell
$body = @{message="What is a cold?"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/chat" -Method Post -Body $body -ContentType "application/json"
# Should return actual AI-generated response
```

### Check Running Processes
```powershell
Get-Process python, node -ErrorAction SilentlyContinue
# Should show:
# - At least 1-2 python processes (app.py)
# - At least 1-3 node processes (React dev server)
```

---

## Start Fresh (If Everything Breaks)

```powershell
# Kill all processes
Get-Process python, node -ErrorAction SilentlyContinue | Stop-Process -Force

# Go to backend
cd c:\Users\ANKIT PUROHIT\Desktop\project\AI-BOT\ai-assistant\backend

# Clean install
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Start backend
python app.py

# In another terminal, go to frontend
cd c:\Users\ANKIT PUROHIT\Desktop\project\AI-BOT\ai-assistant\frontend

# Clean install
rm -r node_modules
npm install

# Start frontend
npm start
```

---

## Performance Tuning

### Slow Chat Responses?
1. Check internet connection
2. Check Gemini API status at https://status.cloud.google.com/
3. Reduce context window in `app.py` (search for `n_results=3`)

### Slow PDF Upload?
1. Reduce chunk size in `medical_rag.py`: `chunk_size=300` (was 500)
2. Increase chunk overlap: `chunk_overlap=20` (was 50)

### Too Many Rate Limit Errors?
Increase limit in `backend/app.py`:
```python
MAX_REQUESTS_PER_MINUTE = 60  # was 30
```

---

## Getting Help

**Error messages to check:**
1. **Backend console** - Shows all Python errors
2. **Frontend console** (DevTools F12) - Shows React errors
3. **Browser Network tab** (DevTools F12) - Shows failed API calls

**What we've verified:**
- ✅ All dependencies installed
- ✅ API key configured and working
- ✅ Both servers running
- ✅ Safety filters active
- ✅ Gemini AI responding

---

## Emergency Shutdown

If something goes wrong and you need to kill everything:

```powershell
# Kill all Python and Node processes
Get-Process python, node -ErrorAction SilentlyContinue | Stop-Process -Force

# Wait a moment
Start-Sleep -Seconds 2

# Verify they're gone
Get-Process python, node -ErrorAction SilentlyContinue
# Should show: No processes found
```

---

## Still Having Issues?

Check these files for configuration:
- `backend/.env` - API keys and settings
- `backend/requirements.txt` - Dependencies
- `backend/app.py` - FastAPI app code
- `frontend/src/utils/api.js` - API client configuration
- `frontend/package.json` - Frontend dependencies

**Everything should already be configured correctly after the fixes applied.**

---

**Version:** 1.0  
**Last Updated:** November 17, 2025  
**Status:** All issues resolved ✅
