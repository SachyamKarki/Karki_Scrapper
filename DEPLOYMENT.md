# Deployment Guide

## Important: Backend Cannot Run on Vercel

Your app has **two parts**:
1. **Frontend** (React + Vite) – ✅ Can deploy to Vercel
2. **Backend** (Flask + Socket.IO + MongoDB) – ❌ Cannot run on Vercel

**Why?** Vercel uses serverless functions that don't support:
- WebSockets / Socket.IO (real-time chat)
- Long-running processes
- Scrapy/Playwright scraping

## Deployment Options

### Option A: Frontend on Vercel + Backend Elsewhere (Recommended)

1. **Deploy Backend** to Railway, Render, Fly.io, or Heroku:
   - Set env vars: `MONGO_URI`, `SECRET_KEY`, `CORS_ORIGINS`, `FLASK_ENV=production`
   - Set `CORS_ORIGINS` to your Vercel frontend URL (e.g. `https://your-app.vercel.app`)
   - Note your backend URL (e.g. `https://your-backend.railway.app`)

2. **Deploy Frontend to Vercel**:
   - Connect this repo to Vercel
   - Add env var: `VITE_API_URL` = your backend URL (e.g. `https://your-backend.railway.app`)
   - Vercel will build the frontend and deploy

3. **Backend CORS** (required for cross-origin auth):
   - Set `CORS_ORIGINS` = your Vercel URL (e.g. `https://your-app.vercel.app`)
   - This enables cookies and API calls from the frontend

### Option B: Both on Render (Blueprint)

Deploy both frontend and backend to Render using the included `render.yaml` Blueprint.

1. **Connect repo to Render**: [dashboard.render.com](https://dashboard.render.com) → New → Blueprint
2. **Link your GitHub repo** containing this project
3. **Enter secrets** when prompted:
   - `SECRET_KEY` – Flask session secret (generate: `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `MONGO_URI` – MongoDB Atlas connection string
   - `CORS_ORIGINS` – Your frontend URL (e.g. `https://scraper-frontend.onrender.com`)
   - `VITE_API_URL` (frontend) – Your backend URL (e.g. `https://scraper-backend.onrender.com`)
   - `GEMINI_API_KEY`, `SERPER_API_KEY` – Optional, for AI analysis features
4. **Deploy** – Render will create both services
5. **After first deploy**: Update `CORS_ORIGINS` on backend to match your frontend URL, and `VITE_API_URL` on frontend to match your backend URL (from the Render dashboard), then redeploy if needed

### Option C: Both on Railway

Deploy both frontend and backend to Railway as a single app. These platforms support WebSockets and long-running processes.

## Vercel Setup (Frontend Only)

1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com) → New Project → Import your repo
3. **Root Directory**: Leave as `.` (project root)
4. **Build Command**: `cd frontend && npm install && npm run build` (or use vercel.json)
5. **Output Directory**: `frontend/dist`
6. **Environment Variables**:
   - `VITE_API_URL` = `https://your-backend-url.com` (your deployed backend)

7. Deploy

## Checklist Before Deploy

- [ ] Backend deployed somewhere (Railway, Render, etc.)
- [ ] `VITE_API_URL` set (Vercel/Render frontend) to backend URL
- [ ] `CORS_ORIGINS` on backend includes your frontend URL
- [ ] `SECRET_KEY` set on backend (required in production)
- [ ] `MONGO_URI` set on backend (MongoDB Atlas or similar)
- [ ] `.env` never committed (only `.env.example`)

### Render Blueprint Checklist

- [ ] `render.yaml` at repo root
- [ ] All `sync: false` env vars set in Render dashboard after first deploy
- [ ] Backend health check at `/api/` passes

### Render Environment Variables (env)

**Backend** (scraper-backend) – Render Dashboard → Backend service → Environment:

| Variable | Required | Value |
|----------|----------|-------|
| `FLASK_ENV` | ✅ (in yaml) | `production` |
| `PORT` | ✅ (in yaml) | `10000` |
| `SECRET_KEY` | ✅ | Random secret: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `MONGO_URI` | ✅ | MongoDB Atlas connection string |
| `CORS_ORIGINS` | ✅ (in yaml) | `https://scraper-frontend.onrender.com,https://scraper-frontend-vbe2.onrender.com` |
| `GEMINI_API_KEY` | Optional | For AI analysis |
| `SERPER_API_KEY` | Optional | For Google rankings |

**Frontend** (scraper-frontend):

| Variable | Required | Value |
|----------|----------|-------|
| `VITE_API_URL` | ✅ | `https://scraper-backend.onrender.com` (your backend URL) |

### Fix "Internal Error" on Login (Render)

1. **MongoDB Atlas Network Access** – Render uses dynamic IPs. In [MongoDB Atlas](https://cloud.mongodb.com) → Network Access → Add IP Address → **Allow Access from Anywhere** (`0.0.0.0/0`). Without this, the backend cannot connect to MongoDB.

2. **Create admin in production** – The admin you created locally is in your local MongoDB. For Render, use the same `MONGO_URI` (production) and run:
   ```bash
   cd backend && python scripts/create_admin.py admin@yourdomain.com YourPassword
   ```
   Ensure `MONGO_URI` in `.env` points to your production MongoDB before running.

3. **CORS_ORIGINS** – Must include your frontend URL(s). Add **both** if you have main + preview:
   - `https://scraper-frontend.onrender.com,https://scraper-frontend-vbe2.onrender.com`
   - No trailing slash. Comma-separated list.

4. **VITE_API_URL** – **CRITICAL: Set to your BACKEND URL, not frontend!**
   - ✅ Correct: `https://scraper-backend.onrender.com`
   - ❌ Wrong: `https://scraper-frontend.onrender.com` (that's the frontend – API calls will fail)
   - Redeploy frontend after setting.
