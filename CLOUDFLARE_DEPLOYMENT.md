# 🚀 Cloudflare Deployment Guide

## Overview
This project is now configured to deploy on **Cloudflare Pages** (frontend) and **Cloudflare Workers** (API).

---

## 📋 Prerequisites

1. **Cloudflare Account** (free): https://dash.cloudflare.com/sign-up
2. **Node.js** 18+ installed: https://nodejs.org/
3. **npm** or **pnpm** package manager
4. **Wrangler CLI** (Cloudflare's deployment tool)

---

## 🔧 Setup Steps

### Step 1: Install Dependencies

```bash
cd web
npm install
```

### Step 2: Install Wrangler CLI

```bash
npm install -g wrangler
```

### Step 3: Login to Cloudflare

```bash
wrangler login
```

This will open your browser to authenticate with Cloudflare.

---

## 🌐 Deploy the API (Cloudflare Workers)

### 1. Navigate to API directory

```bash
cd ../api
```

### 2: Deploy the Worker

```bash
wrangler deploy
```

This will:
- Create a new Cloudflare Worker
- Deploy your ML prediction API
- Give you a URL like: `https://regional-income-api.your-username.workers.dev`

### 3. Test the API

```bash
curl https://your-worker-url.workers.dev/api/health
```

You should get a response with model information.

---

## 🎨 Deploy the Frontend (Cloudflare Pages)

### Option 1: Deploy via GitHub (Recommended)

1. **Push your code to GitHub** (already done!)

2. **Go to Cloudflare Dashboard**:
   - Visit: https://dash.cloudflare.com/
   - Click "Workers & Pages"
   - Click "Create application"
   - Choose "Pages" tab
   - Click "Connect to Git"

3. **Connect Repository**:
   - Select "GitHub"
   - Choose `Vibhor2702/regional-income-prediction`
   - Click "Begin setup"

4. **Configure Build**:
   - Project name: `regional-income-prediction`
   - Production branch: `main`
   - Build command: `cd web && npm install && npm run build`
   - Build output directory: `web/out`

5. **Environment Variables**:
   - Add: `NEXT_PUBLIC_API_URL` = `https://your-worker-url.workers.dev/api/predict`
   - (Replace with your actual Worker URL from Step 2)

6. **Click "Save and Deploy"**

Your app will be live at: `https://regional-income-prediction.pages.dev`

### Option 2: Deploy via CLI

```bash
cd web
npm run build
npx wrangler pages deploy out --project-name=regional-income-prediction
```

---

## 🔗 Update API URL

After deploying the Worker, update the frontend to use the correct API URL:

### Create `.env.local` file in `web/` directory:

```env
NEXT_PUBLIC_API_URL=https://regional-income-api.YOUR_USERNAME.workers.dev/api/predict
```

Replace `YOUR_USERNAME` with your actual Cloudflare username.

Then redeploy the frontend.

---

## ✅ Verify Deployment

1. **Test API Health**:
   ```bash
   curl https://your-worker-url.workers.dev/api/health
   ```

2. **Test Prediction**:
   ```bash
   curl -X POST https://your-worker-url.workers.dev/api/predict \
     -H "Content-Type: application/json" \
     -d '{"zipcode": "10001"}'
   ```

3. **Visit your website**:
   ```
   https://regional-income-prediction.pages.dev
   ```

---

## 🎯 Custom Domain (Optional)

### Add Custom Domain to Cloudflare Pages:

1. Go to your Pages project
2. Click "Custom domains"
3. Add your domain (e.g., `income.yourdomain.com`)
4. Update DNS records as instructed
5. SSL certificate is automatic!

---

## 🔄 Automatic Deployments

Once connected to GitHub, Cloudflare Pages will automatically deploy:
- **Production** when you push to `main` branch
- **Preview** for every pull request

---

## 📊 What Gets Deployed

### Frontend (Cloudflare Pages):
- ✅ Next.js static export
- ✅ Tax-themed UI
- ✅ Interactive prediction calculator
- ✅ Responsive design
- ✅ Optimized assets

### API (Cloudflare Workers):
- ✅ Serverless prediction endpoint
- ✅ Edge computing (fast globally)
- ✅ CORS enabled
- ✅ Health check endpoint
- ✅ Batch predictions support

---

## 🚀 Performance Benefits

### Cloudflare Pages:
- 🌍 **Global CDN**: Your site loads fast worldwide
- ⚡ **Edge caching**: Sub-100ms response times
- 🔒 **Free SSL**: HTTPS enabled automatically
- 💰 **Free tier**: Unlimited bandwidth

### Cloudflare Workers:
- 🚀 **Edge compute**: API runs in 200+ cities worldwide
- ⚡ **0ms cold starts**: Always instant
- 📈 **Auto-scaling**: Handles any traffic
- 💰 **100K requests/day free**

---

## 🛠️ Local Development

### Run frontend locally:

```bash
cd web
npm run dev
```

Visit: http://localhost:3000

### Test Worker locally:

```bash
cd api
wrangler dev
```

API available at: http://localhost:8787

---

## 📝 Environment Variables

### Frontend (.env.local):
```env
NEXT_PUBLIC_API_URL=https://regional-income-api.YOUR_USERNAME.workers.dev/api/predict
```

### Worker (wrangler.toml):
```toml
[env.production]
vars = { ENVIRONMENT = "production" }
```

---

## 🐛 Troubleshooting

### Build fails on Cloudflare Pages

1. Check build command: `cd web && npm install && npm run build`
2. Check output directory: `web/out`
3. Check Node.js version (should be 18+)

### API returns errors

1. Check Worker logs: `wrangler tail`
2. Verify CORS headers
3. Test with curl first

### Frontend can't connect to API

1. Verify API URL in environment variables
2. Check browser console for CORS errors
3. Ensure Worker is deployed and accessible

---

## 📦 Project Structure

```
regional-income-prediction/
├── web/                    # Next.js frontend
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx       # Main UI
│   │   └── globals.css
│   ├── package.json
│   └── next.config.js
├── api/                    # Cloudflare Worker
│   ├── worker.ts          # API endpoints
│   └── wrangler.toml      # Worker config
└── models/                 # Trained ML models
```

---

## 🎉 You're Done!

Your Regional Income Prediction app is now deployed on Cloudflare's global network!

**Live URLs:**
- Frontend: `https://regional-income-prediction.pages.dev`
- API: `https://regional-income-api.YOUR_USERNAME.workers.dev`

Share your project with the world! 🌟

---

## 📚 Additional Resources

- [Cloudflare Pages Docs](https://developers.cloudflare.com/pages/)
- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- [Next.js on Cloudflare](https://developers.cloudflare.com/pages/framework-guides/deploy-a-nextjs-site/)
- [Wrangler CLI Reference](https://developers.cloudflare.com/workers/wrangler/)
