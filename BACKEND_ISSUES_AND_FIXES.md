# Backend Issues Found and Fixes Required

## ✅ Good News: Backend Endpoint Exists
The `/api/v1/ingest/upload` endpoint is properly defined in the backend:
- **Location**: `backend/app/api/v1/ingest.py` (line 9)
- **Full Path**: `/api/v1/ingest/upload`
- **Method**: POST
- **Parameters**: `file`, `user_id`, `dataset_id` (optional)

## 🚨 Critical Issue #1: Missing CORS Configuration

### Problem
The backend **DOES NOT** have CORS (Cross-Origin Resource Sharing) middleware configured. This means:
- Requests from Vercel (frontend) to Render (backend) will be **BLOCKED** by the browser
- You'll see CORS errors in the browser console
- The frontend won't be able to communicate with the backend

### Evidence
`backend/app/main.py` has NO CORS middleware:
```python
# No CORSMiddleware configured!
app = FastAPI(title="Backend API", version="0.1.0")
app.middleware('http')(auth_middleware)
app.include_router(get_api_router(minimal=minimal), prefix="/api/v1")
```

### Solution Required
Add CORS middleware to allow requests from your Vercel frontend domain.

---

## ⚠️ Issue #2: Authentication Token Configuration

### Problem
The backend requires Bearer token authentication for all non-public endpoints (including `/api/v1/ingest/upload`).

**Backend expects**: `Authorization: Bearer <token>` header
**Public endpoints (no auth required)**:
- `/api/v1/health`
- `/api/v1/livez`
- `/api/v1/readyz`
- `/api/v1/metrics`

### What to Check
1. **Backend on Render**: Ensure `AUTH_BEARER_TOKEN` environment variable is set
2. **Frontend on Vercel**: Ensure one of these environment variables is set:
   - `BACKEND_BEARER_TOKEN`
   - `BACKEND_AUTH_BEARER_TOKEN`
   - `NEXT_PUBLIC_BACKEND_BEARER_TOKEN`
   - `AUTH_BEARER_TOKEN`
   - `NEXT_PUBLIC_AUTH_BEARER_TOKEN`

3. **Important**: The token value must MATCH on both frontend and backend!

---

## 🔧 Required Fixes

### Fix #1: Add CORS Middleware to Backend

**File to modify**: `backend/app/main.py`

Add this code:

```python
from fastapi.middleware.cors import CORSMiddleware

def create_app(*, minimal: bool | None = None) -> FastAPI:
    # ... existing code ...
    
    app = FastAPI(title="Backend API", version="0.1.0")
    
    # ADD THIS: Configure CORS
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
    if not allowed_origins or allowed_origins == [""]:
        # Default to allow all in development, specific origins in production
        if os.getenv("ENVIRONMENT", "development") == "production":
            allowed_origins = [
                "https://your-app.vercel.app",  # Replace with your actual domain
                "https://*.vercel.app",
            ]
        else:
            allowed_origins = ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Existing middleware
    app.middleware('http')(auth_middleware)
    
    # ... rest of existing code ...
```

**Environment Variable to Set on Render**:
```
ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-app-preview.vercel.app
```

Replace `your-app` with your actual Vercel app name.

---

### Fix #2: Verify Environment Variables

#### On Render (Backend)
Set these environment variables:
```bash
ENVIRONMENT=production
AUTH_BEARER_TOKEN=<your-secure-token-here>
ALLOWED_ORIGINS=https://your-app.vercel.app
SUPABASE_URL=<your-supabase-url>
SUPABASE_ANON_KEY=<your-supabase-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-supabase-service-key>
OPENAI_API_KEY=<your-openai-key>
```

#### On Vercel (Frontend)
Set these environment variables:
```bash
BACKEND_URL=https://your-backend.onrender.com
BACKEND_BEARER_TOKEN=<same-token-as-backend>
NEXT_PUBLIC_BACKEND_URL=https://your-backend.onrender.com
```

---

## 🎯 Additional Backend Recommendations

### 1. Add Health Check Endpoint Verification
Test that your health endpoint works:
```bash
curl https://your-backend.onrender.com/api/v1/health
```

### 2. Test Upload Endpoint with Auth
```bash
curl -X POST https://your-backend.onrender.com/api/v1/ingest/upload \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@test.csv" \
  -F "user_id=test-user"
```

### 3. Check Render Logs
Look for these types of errors:
- ❌ `401 Unauthorized` - Token mismatch or missing
- ❌ CORS errors - Missing CORS middleware
- ❌ `500 Internal Server Error` - Backend service issues (DB, OpenAI, etc.)

---

## 🚀 Deployment Steps

### Step 1: Update Backend Code (CORS Fix)
```bash
cd /workspace/backend
# Make the changes to app/main.py as shown above
```

### Step 2: Commit and Deploy to Render
```bash
git add backend/app/main.py
git commit -m "fix: Add CORS middleware for cross-origin requests"
git push
```

Render should automatically deploy the changes.

### Step 3: Verify Environment Variables
- Go to Render Dashboard → Your Service → Environment
- Verify all required env vars are set
- Click "Save Changes" to restart the service

### Step 4: Test Backend Directly
```bash
# Test health endpoint (no auth required)
curl https://your-backend.onrender.com/api/v1/health

# Test upload endpoint (auth required)
curl -X POST https://your-backend.onrender.com/api/v1/ingest/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.csv" \
  -F "user_id=test"
```

### Step 5: Test Frontend → Backend Integration
After both frontend and backend are deployed:
1. Open your Vercel app
2. Go to Upload tab
3. Try uploading a file
4. Check browser DevTools → Network tab for any errors

---

## 📊 Debug Checklist

When troubleshooting 404 or connection errors:

### Backend (Render)
- [ ] CORS middleware is added to `main.py`
- [ ] `AUTH_BEARER_TOKEN` env var is set
- [ ] `ALLOWED_ORIGINS` env var includes your Vercel domain
- [ ] Service is running (check Render dashboard)
- [ ] `/api/v1/health` endpoint responds successfully
- [ ] Check Render logs for errors

### Frontend (Vercel)
- [ ] `vercel.json` is updated (from previous fix)
- [ ] `BACKEND_URL` env var points to Render URL
- [ ] `BACKEND_BEARER_TOKEN` matches backend token
- [ ] Latest deployment includes all changes
- [ ] Check browser console for CORS errors
- [ ] Check Network tab for actual HTTP response codes

### Token Configuration
- [ ] Frontend token = Backend token (exactly!)
- [ ] No extra spaces or quotes in environment variables
- [ ] Token is not empty or undefined

---

## 🔍 Common Error Scenarios

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| 404 Not Found | Frontend routing issue | Update `vercel.json` (already done) |
| 401 Unauthorized | Token mismatch | Verify env vars match |
| 403 Forbidden | Auth logic blocking request | Check auth middleware |
| CORS Error | No CORS middleware | Add CORS config to backend |
| 500 Internal Server Error | Backend service error | Check Render logs, verify DB/OpenAI keys |
| Network Error | Backend is down | Check Render service status |
| Timeout | Slow cold start on Render | Wait or upgrade Render plan |

---

## 🎓 Why This Happens

### CORS (Cross-Origin Resource Sharing)
- **Frontend**: `https://your-app.vercel.app` (Origin A)
- **Backend**: `https://your-backend.onrender.com` (Origin B)
- Without CORS, browsers BLOCK requests from Origin A to Origin B for security
- CORS middleware tells browsers: "It's okay to allow requests from these specific origins"

### Authentication
- The backend requires a Bearer token to prevent unauthorized access
- The token acts like a password that the frontend includes in every request
- Both sides must use the EXACT same token

---

## 📝 Summary

**2 Main Issues Found:**
1. ✅ **Frontend Issue** (FIXED): `vercel.json` routing config - ALREADY FIXED
2. 🚨 **Backend Issue** (NEEDS FIX): Missing CORS middleware - REQUIRES CODE CHANGE

**Next Steps:**
1. Add CORS middleware to backend (code change required)
2. Verify environment variables on both Render and Vercel
3. Deploy backend changes to Render
4. Test the integration

After these fixes, your `/api/ingest/upload` endpoint should work correctly!
