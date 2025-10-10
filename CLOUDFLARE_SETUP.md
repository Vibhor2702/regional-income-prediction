# Cloudflare Pages Deployment Setup

## ⚠️ CRITICAL: Cloudflare Configuration Required

If you're seeing the **OLD single-button interface** instead of the **NEW 4-button interface**, your Cloudflare Pages project is misconfigured.

## The Problem

Cloudflare Pages is likely:
1. Deploying from the **wrong directory** (root instead of `/web`)
2. Using the **wrong build command**
3. Not finding the updated `page.tsx` file

## The Solution

### Step 1: Access Cloudflare Dashboard
1. Go to: https://dash.cloudflare.com/
2. Navigate to: **Pages** → **regional-income-prediction**
3. Click: **Settings** → **Builds & deployments**

### Step 2: Update Build Configuration

Set these values **EXACTLY**:

```
Framework preset: Next.js
Build command: cd web && npm install && npm run build
Build output directory: web/.next
Root directory: web
```

**OR if Root directory doesn't work:**

```
Framework preset: Next.js  
Build command: npm install && npm run build
Build output directory: .next
Root directory: web
```

### Step 3: Add Environment Variables

Click **Environment variables** and add:

```
NODE_VERSION = 18
NPM_VERSION = 9
```

### Step 4: Trigger Rebuild

After saving settings:
1. Go to **Deployments** tab
2. Click **Retry deployment** on the latest deployment
3. Wait 3-5 minutes for rebuild

### Step 5: Clear Browser Cache

Once deployment completes:
1. Press **Ctrl + Shift + R** (Windows) or **Cmd + Shift + R** (Mac)
2. Or clear all browser cache for the site
3. Refresh the page

## Verification

After successful deployment, you should see:

### ✅ NEW 4-Button Interface:
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Traditional │     ML      │   Hybrid    │ Compare All │
│   (Blue)    │   (Green)   │   (Gold)    │  (Purple)   │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

### ❌ OLD Interface (Wrong):
```
Single button: "Calculate Income Prediction"
```

## Quick Test

After deployment, test the API endpoints directly:

```bash
# Traditional Method
curl https://regional-income-prediction.pages.dev/api/predict-traditional?zipcode=10001

# ML Method
curl https://regional-income-prediction.pages.dev/api/predict-ml?zipcode=10001

# Hybrid Method
curl https://regional-income-prediction.pages.dev/api/predict-hybrid?zipcode=10001

# Compare All
curl https://regional-income-prediction.pages.dev/api/compare-methods?zipcode=10001
```

All 4 endpoints should return JSON responses with predictions.

## Alternative: Manual Deployment

If automatic deployment fails, deploy manually:

```bash
cd web
npm install
npm run build
npx wrangler pages deploy .next --project-name=regional-income-prediction
```

## Still Not Working?

1. **Check deployment logs** in Cloudflare Dashboard → Deployments → [latest] → View logs
2. **Verify the commit** being deployed matches latest GitHub commit (aa5cd50)
3. **Check build output** - should show "Building Next.js app..." not "No build command"
4. **Contact support** if logs show errors

## Expected File Structure

Cloudflare should be deploying from:
```
web/
  ├── app/
  │   └── page.tsx           ← Contains 4-button selector code
  ├── functions/
  │   └── api/
  │       ├── predict-traditional.ts
  │       ├── predict-ml.ts
  │       ├── predict-hybrid.ts
  │       └── compare-methods.ts
  ├── .next/                 ← Build output (deployed to Pages)
  └── package.json
```

## Files That MUST Be Deployed

- `web/app/page.tsx` (785 lines) - Contains 4-button UI
- `web/functions/api/predict-traditional.ts` - Traditional econometric model
- `web/functions/api/predict-ml.ts` - ML stacked ensemble model  
- `web/functions/api/predict-hybrid.ts` - Hybrid weighted model
- `web/functions/api/compare-methods.ts` - Comparison API

If any of these are missing from deployment, the configuration is wrong.
