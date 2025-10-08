# 404 Error Fix Summary

## Problem
The `/api/ingest/upload` endpoint was returning a 404 error when deployed on Vercel.

## Root Cause
The `vercel.json` configuration had a problematic routing setup:
```json
{
  "builds": [
    { "src": "frontend/package.json", "use": "@vercel/next" }
  ],
  "routes": [
    { "src": "/(.*)", "dest": "frontend/$1" }
  ]
}
```

This custom routing configuration was interfering with Next.js App Router's automatic API route handling.

## Solution Applied
Updated `vercel.json` to use the proper monorepo configuration:
```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "buildCommand": "cd frontend && npm run build",
  "installCommand": "cd frontend && npm install",
  "framework": "nextjs",
  "outputDirectory": "frontend/.next"
}
```

### Key Changes:
1. **Removed custom routes**: The `routes` array was deleted as Next.js handles routing automatically
2. **Removed old builds config**: Replaced with explicit build commands
3. **Added framework specification**: Explicitly tells Vercel this is a Next.js project
4. **Proper monorepo setup**: Commands navigate to the `frontend` directory before running

## Next Steps

### 1. Redeploy to Vercel
You need to trigger a new deployment for the changes to take effect:

**Option A: Via Git (Recommended)**
```bash
git add vercel.json
git commit -m "fix: Update Vercel config to fix API route 404 errors"
git push
```

**Option B: Via Vercel CLI**
```bash
vercel --prod
```

**Option C: Via Vercel Dashboard**
- Go to your Vercel project dashboard
- Navigate to the Deployments tab
- Click "Redeploy" on the latest deployment

### 2. Verify the Fix
After deployment, test the endpoint:
```bash
curl -X POST https://your-app.vercel.app/api/ingest/upload \
  -F "file=@test.csv" \
  -F "user_id=test-user"
```

### 3. Alternative: Configure Root Directory in Vercel Dashboard
If you prefer, you can also set the root directory in the Vercel project settings:
1. Go to Project Settings → General
2. Set "Root Directory" to `frontend`
3. This would allow you to simplify `vercel.json` or remove it entirely

## API Route Structure (Verified Correct)
```
frontend/
  app/
    api/
      analyze/route.ts          → /api/analyze
      health/route.ts           → /api/health
      ingest/
        upload/route.ts         → /api/ingest/upload  ✓
      export/
        pdf/route.ts            → /api/export/pdf
        image/route.ts          → /api/export/image
```

All routes are properly structured and export the correct HTTP method handlers.

## Technical Details

### Why the Old Config Failed
The `"routes": [{ "src": "/(.*)", "dest": "frontend/$1" }]` configuration was trying to do static routing, but Next.js App Router needs dynamic routing to handle API routes. The custom route rule was overriding Next.js's internal routing mechanism.

### How the New Config Works
- **Build Command**: `cd frontend && npm run build` ensures Next.js builds from the correct directory
- **Framework Detection**: `"framework": "nextjs"` tells Vercel to use Next.js-specific deployment logic
- **Output Directory**: `"outputDirectory": "frontend/.next"` tells Vercel where to find the build output
- Vercel automatically handles routing for Next.js API routes without explicit route rules

## Verification Checklist
After redeployment, verify:
- [ ] `/api/ingest/upload` returns proper response (not 404)
- [ ] `/api/analyze` still works
- [ ] `/api/health` still works
- [ ] `/api/export/pdf` still works
- [ ] `/api/export/image` still works
- [ ] Frontend pages still load correctly

## Additional Notes

### Environment Variables
Ensure these environment variables are set in Vercel:
- `BACKEND_URL` or `NEXT_PUBLIC_BACKEND_URL`
- `BACKEND_BEARER_TOKEN` or similar auth token variables

### Runtime Configuration
All API routes are configured with:
- `runtime: 'nodejs'` - Uses Node.js runtime
- `dynamic: 'force-dynamic'` - Disables caching for dynamic responses
- `preferredRegion: ['iad1', 'cdg1']` - (for some routes) Specifies deployment regions

## Support
If the issue persists after redeployment:
1. Check Vercel build logs for errors
2. Verify environment variables are set correctly
3. Ensure the backend service is accessible from Vercel's network
4. Check for any custom middleware that might be blocking requests
