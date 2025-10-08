# 🚀 Quick Fix Reference Card

## What Was Fixed

| Component | Issue | Status |
|-----------|-------|--------|
| Frontend (Vercel) | 404 on `/api/ingest/upload` | ✅ FIXED |
| Backend (Render) | Missing CORS middleware | ✅ FIXED |

---

## 🔧 Files Modified

```bash
✏️  vercel.json                    # Fixed routing
✏️  backend/app/main.py           # Added CORS
```

---

## ⚡ Deploy Now

```bash
# 1. Commit changes
git add vercel.json backend/app/main.py
git commit -m "fix: Add CORS middleware and update Vercel config"
git push

# 2. Both services will auto-deploy
# Vercel: ~2-5 minutes
# Render: ~5-10 minutes
```

---

## 🔑 Required Environment Variables

### Render (Backend)
```bash
AUTH_BEARER_TOKEN=<your-secure-token>
ALLOWED_ORIGINS=https://your-app.vercel.app
SUPABASE_URL=<url>
SUPABASE_ANON_KEY=<key>
SUPABASE_SERVICE_ROLE_KEY=<key>
OPENAI_API_KEY=<key>
```

### Vercel (Frontend)
```bash
BACKEND_URL=https://your-backend.onrender.com
BACKEND_BEARER_TOKEN=<same-as-above>
NEXT_PUBLIC_BACKEND_URL=https://your-backend.onrender.com
```

⚠️ **Token must match exactly on both platforms!**

---

## 🧪 Test After Deployment

```bash
# 1. Test backend
curl https://your-backend.onrender.com/api/v1/health

# 2. Test frontend
./test-upload-endpoint.sh https://your-app.vercel.app

# 3. Browser test
# Open app → Upload tab → Upload CSV file
```

---

## 📖 Full Documentation

- **`DEPLOYMENT_GUIDE.md`** - Complete deployment steps
- **`FIX_SUMMARY.md`** - Detailed explanation
- **`BACKEND_ISSUES_AND_FIXES.md`** - Backend details

---

## 🆘 Quick Troubleshooting

| Error | Fix |
|-------|-----|
| 404 | Ensure `vercel.json` is deployed |
| CORS | Check `ALLOWED_ORIGINS` on Render |
| 401 | Verify tokens match exactly |
| 500 | Check Render logs, verify API keys |

---

## 📞 Support Files

```
/workspace/
├── vercel.json                      # ✅ Updated
├── backend/
│   ├── app/main.py                  # ✅ Updated
│   └── .env.example                 # 📄 Template
├── frontend/
│   └── .env.example                 # 📄 Template
├── render.yaml                      # 📄 Deployment config
├── test-upload-endpoint.sh          # 🧪 Testing script
├── DEPLOYMENT_GUIDE.md              # 📖 Full guide
├── FIX_SUMMARY.md                   # 📊 Complete summary
└── QUICK_FIX_REFERENCE.md          # ⚡ This file
```

---

## ✅ Checklist

- [ ] Committed changes to git
- [ ] Pushed to GitHub
- [ ] Set env vars on Render
- [ ] Set env vars on Vercel
- [ ] Verified tokens match
- [ ] Updated ALLOWED_ORIGINS
- [ ] Tested health endpoint
- [ ] Tested upload endpoint
- [ ] Tested in browser
- [ ] No errors in console

---

**Time to Fix:** 5 minutes  
**Time to Deploy:** 30-45 minutes  
**Confidence:** High ✅
