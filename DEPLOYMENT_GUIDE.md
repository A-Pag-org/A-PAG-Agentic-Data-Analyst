# Complete Deployment Guide

This guide will help you deploy your Agentic Data Analyst application with the frontend on Vercel and backend on Render.

## 🎯 Quick Summary of Fixes

### Frontend (Vercel) - ✅ FIXED
- **Issue**: Invalid `vercel.json` routing configuration causing 404 errors
- **Fix Applied**: Updated `vercel.json` to use proper Next.js monorepo configuration
- **Status**: ✅ Ready to deploy

### Backend (Render) - ✅ FIXED
- **Issue**: Missing CORS middleware preventing cross-origin requests
- **Fix Applied**: Added CORS middleware to `backend/app/main.py`
- **Status**: ✅ Ready to deploy

---

## 📋 Prerequisites

Before deploying, ensure you have:
- [ ] GitHub repository with your code
- [ ] Vercel account (https://vercel.com)
- [ ] Render account (https://render.com)
- [ ] Supabase project (https://supabase.com)
- [ ] OpenAI API key (https://platform.openai.com)

---

## 🚀 Step-by-Step Deployment

### Step 1: Deploy Backend to Render

#### 1.1 Create New Web Service
1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your repository

#### 1.2 Configure Service
- **Name**: `agentic-data-analyst-backend` (or your choice)
- **Region**: Choose closest to your users
- **Branch**: `main` (or your default branch)
- **Root Directory**: `backend`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Plan**: Starter ($7/month) or higher (Free tier has cold starts)

#### 1.3 Set Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add these:

**Required Variables:**
```bash
ENVIRONMENT=production
PYTHON_VERSION=3.11
AUTH_BEARER_TOKEN=<generate-a-secure-random-token>
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=<your-supabase-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-supabase-service-key>
OPENAI_API_KEY=sk-<your-openai-api-key>
```

**CORS Configuration:**
```bash
# You'll update this after deploying frontend
ALLOWED_ORIGINS=*
```

**Optional but Recommended:**
```bash
CHROMA_BACKEND=persistent
CHROMA_AUTOSAVE=true
EMBEDDING_MODEL=text-embedding-3-large
USE_SEMANTIC_CHUNKING=true
CHUNK_SIZE=512
CHUNK_OVERLAP=50
```

#### 1.4 Deploy Backend
1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. Note your backend URL: `https://your-backend.onrender.com`

#### 1.5 Test Backend
```bash
# Test health endpoint
curl https://your-backend.onrender.com/api/v1/health

# Expected response: {"status":"ok"} or similar
```

---

### Step 2: Deploy Frontend to Vercel

#### 2.1 Import Project
1. Go to https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository

#### 2.2 Configure Project
- **Framework Preset**: Next.js (should auto-detect)
- **Root Directory**: Leave empty (vercel.json handles this)
- **Build Command**: (leave default) `npm run build`
- **Output Directory**: (leave default) `.next`
- **Install Command**: (leave default) `npm install`

#### 2.3 Set Environment Variables

Add these environment variables:

**Required:**
```bash
BACKEND_URL=https://your-backend.onrender.com
BACKEND_BEARER_TOKEN=<same-token-as-backend>
NEXT_PUBLIC_BACKEND_URL=https://your-backend.onrender.com
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<your-supabase-anon-key>
```

⚠️ **IMPORTANT**: The `BACKEND_BEARER_TOKEN` must EXACTLY match the `AUTH_BEARER_TOKEN` you set on Render!

#### 2.4 Deploy Frontend
1. Click **"Deploy"**
2. Wait for deployment (2-5 minutes)
3. Note your frontend URL: `https://your-app.vercel.app`

---

### Step 3: Update CORS Configuration

Now that you have your frontend URL, update the backend:

#### 3.1 Update Render Environment Variable
1. Go to Render Dashboard → Your Backend Service
2. Go to **"Environment"** tab
3. Find `ALLOWED_ORIGINS` variable
4. Update its value to your Vercel URL:
   ```
   https://your-app.vercel.app
   ```
   
   Or for multiple environments:
   ```
   https://your-app.vercel.app,https://your-app-*.vercel.app
   ```

5. Click **"Save Changes"**
6. Service will automatically redeploy (1-2 minutes)

---

### Step 4: Verify Everything Works

#### 4.1 Test Backend Health
```bash
curl https://your-backend.onrender.com/api/v1/health
```
Expected: `{"status": "ok"}` or similar

#### 4.2 Test Backend Upload (with auth)
```bash
# Create test CSV file
cat > test.csv << EOF
id,product,sales
1,Widget,1000
2,Gadget,1500
EOF

# Test upload
curl -X POST https://your-backend.onrender.com/api/v1/ingest/upload \
  -H "Authorization: Bearer YOUR_BACKEND_TOKEN" \
  -F "file=@test.csv" \
  -F "user_id=test-user"
```

Expected: Success response with chunks created

#### 4.3 Test Frontend
1. Open your Vercel URL: `https://your-app.vercel.app`
2. Go to **"Upload"** tab
3. Select a CSV file
4. Click **"Upload Data"**
5. Should see success message

#### 4.4 Test Full Flow
1. Upload a data file
2. Go to **"Analyze"** tab
3. Ask a question about your data
4. Should see results and visualizations

---

## 🐛 Troubleshooting

### Problem: 404 Not Found on `/api/ingest/upload`

**On Frontend (Vercel):**
- ✅ Ensure `vercel.json` has been updated (this is already done)
- ✅ Redeploy frontend after committing changes
- Check Vercel build logs for errors

**On Backend (Render):**
- ✅ Ensure CORS middleware is added (this is already done)
- Check Render deployment logs
- Test backend health endpoint directly

### Problem: CORS Error in Browser

**Symptoms**: Browser console shows:
```
Access to fetch at 'https://backend...' from origin 'https://frontend...' 
has been blocked by CORS policy
```

**Solution**:
1. Verify `ALLOWED_ORIGINS` is set on Render
2. Ensure it includes your exact Vercel URL
3. Redeploy backend after changes
4. Hard refresh browser (Ctrl+Shift+R / Cmd+Shift+R)

### Problem: 401 Unauthorized

**Symptoms**: Upload fails with 401 error

**Solution**:
1. Check that `AUTH_BEARER_TOKEN` is set on Render
2. Check that `BACKEND_BEARER_TOKEN` is set on Vercel
3. **Verify they are EXACTLY the same** (no extra spaces, quotes, etc.)
4. Redeploy both frontend and backend

### Problem: 500 Internal Server Error

**Symptoms**: Backend returns 500 error

**Solution**:
1. Check Render logs: Dashboard → Service → Logs
2. Common causes:
   - Missing `OPENAI_API_KEY`
   - Missing `SUPABASE_URL` or keys
   - Database connection issues
   - Out of OpenAI credits
3. Fix missing environment variables
4. Redeploy backend

### Problem: Render Service "Cold Starts"

**Symptoms**: First request takes 30+ seconds

**Solution**:
- Free tier services spin down after 15 minutes of inactivity
- Upgrade to Starter ($7/month) or higher for always-on service
- Or accept occasional cold starts on free tier

---

## 📊 Monitoring & Logs

### View Vercel Logs
1. Dashboard → Your Project → Deployments
2. Click on a deployment → View Function Logs
3. Real-time logs for API routes

### View Render Logs
1. Dashboard → Your Service → Logs
2. Real-time logs for backend
3. Filter by error level

---

## 🔐 Security Best Practices

### Generate Secure Tokens
```bash
# Generate a secure random token for AUTH_BEARER_TOKEN
openssl rand -hex 32

# Or use Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Environment Variables Checklist
- [ ] Never commit `.env` files to git
- [ ] Use different tokens for dev/staging/production
- [ ] Rotate tokens periodically
- [ ] Keep `SUPABASE_SERVICE_ROLE_KEY` secret (never expose to browser)
- [ ] Set `ALLOWED_ORIGINS` to specific domains in production

---

## 🎉 Success Checklist

After deployment, verify:
- [ ] Frontend loads at Vercel URL
- [ ] Backend health endpoint responds
- [ ] Can upload CSV files successfully
- [ ] Can analyze data and get results
- [ ] Visualizations render correctly
- [ ] No CORS errors in browser console
- [ ] No 401/404 errors in Network tab

---

## 📚 Additional Resources

### Documentation
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Vercel Documentation](https://vercel.com/docs)
- [Render Documentation](https://render.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

### Monitoring (Optional)
- [Sentry](https://sentry.io) - Error tracking
- [Vercel Analytics](https://vercel.com/analytics) - Performance monitoring
- [Render Metrics](https://render.com/docs/metrics) - Service monitoring

---

## 💡 Tips for Production

1. **Use Custom Domains**
   - Add custom domain to Vercel
   - Update `ALLOWED_ORIGINS` with custom domain

2. **Enable Caching**
   - Set up Redis on Render for faster responses
   - Configure `REDIS_URL` environment variable

3. **Scale Backend**
   - Upgrade Render plan for better performance
   - Enable auto-scaling if needed

4. **Database**
   - Use Render PostgreSQL for persistent storage
   - Set `DATABASE_URL` for pgvector features

5. **Monitor Costs**
   - Track OpenAI API usage
   - Monitor Render/Vercel usage
   - Set up billing alerts

---

## 🆘 Need Help?

If you're still experiencing issues after following this guide:

1. Check the detailed error logs on both platforms
2. Review `BACKEND_ISSUES_AND_FIXES.md` for backend-specific issues
3. Review `404_FIX_SUMMARY.md` for frontend-specific issues
4. Verify all environment variables are set correctly
5. Ensure both services are running and healthy

---

## 📝 Deployment Summary

**Files Modified:**
- ✅ `vercel.json` - Fixed frontend routing
- ✅ `backend/app/main.py` - Added CORS middleware

**Files Created:**
- 📄 `backend/.env.example` - Backend environment template
- 📄 `frontend/.env.example` - Frontend environment template
- 📄 `render.yaml` - Render blueprint (optional)
- 📄 `test-upload-endpoint.sh` - Testing script

**Environment Variables Required:**
- **Backend (Render)**: 10+ variables including AUTH_BEARER_TOKEN, OPENAI_API_KEY, SUPABASE keys
- **Frontend (Vercel)**: 5+ variables including BACKEND_URL, BACKEND_BEARER_TOKEN

**Estimated Setup Time:** 30-45 minutes

---

Good luck with your deployment! 🚀
