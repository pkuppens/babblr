# Testing Error Handling (PR #22)

This guide shows how to test the new error handling features that replace `alert()` with user-friendly toast notifications and React Error Boundaries.

## 1. Running the Backend

### Option A: Using the Script (Recommended)
```bash
# From project root
./run-backend.sh
```

### Option B: Using uv (Windows PowerShell)
```powershell
cd backend
uv run babblr-backend
```

### Option C: Manual Python (if uv not available)
```bash
cd backend
# Activate virtual environment
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac

# Set PYTHONPATH
$env:PYTHONPATH = (Get-Location).Path  # Windows PowerShell
# or
export PYTHONPATH=$(pwd)  # Linux/Mac

# Run
cd app
python main.py
```

The backend should start on `http://127.0.0.1:8000`

**Verify it's running:**
```bash
curl http://localhost:8000/health
```

## 2. Installing Frontend Dependencies

Before testing, install the new dependencies:

```bash
cd frontend
npm install
```

This will install:
- `react-hot-toast` - for toast notifications
- `lucide-react` - for icons in ErrorBoundary

## 3. Starting the Frontend

```bash
# From project root
./run-frontend.sh

# Or manually:
cd frontend
npm run electron:dev
```

## 4. Testing Error Scenarios

### Test 1: Backend Not Running (Network Error)

**Steps:**
1. **Don't start the backend** (or stop it if running)
2. Start the frontend
3. Try to create a new conversation
4. **Expected:** Toast notification appears saying "Network error. Please check your internet connection." (instead of browser alert)

**What to look for:**
- ✅ Toast appears in top-right corner
- ✅ Message is user-friendly
- ✅ No browser alert popup
- ✅ App doesn't crash

### Test 2: Invalid Conversation ID (404 Error)

**Steps:**
1. Start backend and frontend
2. Open browser DevTools (F12)
3. In Console, run:
   ```javascript
   // Try to access a non-existent conversation
   fetch('http://localhost:8000/conversations/99999')
     .then(r => r.json())
     .catch(e => console.log(e))
   ```
4. **Expected:** Toast notification with error message

**Alternative:** Modify the code temporarily to use an invalid ID:
- In `ConversationInterface.tsx`, change `conversation.id` to `99999` temporarily

### Test 3: API Timeout

**Steps:**
1. Start backend
2. In backend code, add a delay to simulate timeout:
   ```python
   # In backend/app/routes/chat.py, add at the top:
   import asyncio
   
   # In the chat endpoint, add:
   await asyncio.sleep(30)  # Simulate slow response
   ```
3. Start frontend
4. Try to send a message
5. **Expected:** Toast saying "The request timed out. Please check your connection."

### Test 4: React Error Boundary

**Steps:**
1. Start frontend
2. Open DevTools (F12)
3. In Console, run:
   ```javascript
   // Force a React error
   throw new Error("Test error for ErrorBoundary");
   ```
4. **Expected:**
   - ErrorBoundary UI appears (full-screen error page)
   - Shows "Something went wrong" message
   - Has "Refresh Page" and "Copy Error Text" buttons
   - No white screen of death

**Better test:** Temporarily break a component:
- In `App.tsx`, add: `{null.undefined}` somewhere in render
- Save and see ErrorBoundary catch it

### Test 5: Backend Returns Error Response

**Steps:**
1. Start backend
2. Temporarily break backend (e.g., remove API key from `.env`)
3. Start frontend
4. Try to create a conversation
5. **Expected:** Toast with backend error message

### Test 6: Normal Operation (No Errors)

**Steps:**
1. Start backend (with valid API key)
2. Start frontend
3. Create a conversation
4. Send messages
5. **Expected:** Everything works normally, no error toasts

## 5. What Changed

### Before (Old Behavior):
- ❌ Browser `alert()` popups for errors
- ❌ White screen if React component crashes
- ❌ No user-friendly error messages
- ❌ Errors only in console

### After (New Behavior):
- ✅ Toast notifications in top-right corner
- ✅ ErrorBoundary catches React errors gracefully
- ✅ User-friendly error messages
- ✅ "Copy Error Text" button for debugging
- ✅ "Refresh Page" button to recover

## 6. Visual Verification Checklist

When testing, verify:

- [ ] Toast notifications appear (not alerts)
- [ ] Toasts are positioned top-right
- [ ] Toasts auto-dismiss after 5 seconds
- [ ] ErrorBoundary shows nice UI (not white screen)
- [ ] ErrorBoundary has working buttons
- [ ] Copy to clipboard works
- [ ] Refresh button works
- [ ] No console errors from error handling code
- [ ] Normal operation still works

## 7. Quick Test Script

Run this in browser console to test all error types:

```javascript
// Test network error
fetch('http://localhost:8000/nonexistent')
  .catch(e => console.log('Network error test:', e));

// Test 404
fetch('http://localhost:8000/conversations/99999')
  .then(r => r.json())
  .catch(e => console.log('404 test:', e));

// Test React error (triggers ErrorBoundary)
setTimeout(() => {
  throw new Error("Test React error");
}, 1000);
```

## 8. Troubleshooting

**Toasts not appearing?**
- Check `react-hot-toast` is installed: `npm list react-hot-toast`
- Check `Toaster` component is in `main.tsx`
- Check browser console for errors

**ErrorBoundary not catching errors?**
- Verify `ErrorBoundary` wraps `<App />` in `main.tsx`
- Check that error is a React render error (not async/network)

**Backend won't start?**
- Check Python version: `python --version` (need 3.12+)
- Check `.env` file exists in `backend/`
- Try: `cd backend && uv sync` to reinstall dependencies

