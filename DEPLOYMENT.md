# Deployment Guide

## Frontend on Vercel + Backend on Render (Recommended)

Your app has **two parts**:
1. **Frontend** (React + Vite) – ✅ Deploy to **Vercel**
2. **Backend** (Flask + Socket.IO + MongoDB) – ✅ Deploy to **Render**

**Why split?** Vercel doesn't support WebSockets, long-running processes, or Scrapy. Render does.

---

## Step 1: Deploy Backend to Render

1. Go to [dashboard.render.com](https://dashboard.render.com) → **New** → **Blueprint**
2. Connect your GitHub repo
3. Render will detect `render.yaml` and create **scraper-backend** only
4. When prompted, set:
   - `SECRET_KEY` – `python -c "import secrets; print(secrets.token_hex(32))"`
   - `MONGO_URI` – Your MongoDB Atlas connection string
   - `CORS_ORIGINS` – Your Vercel URL (e.g. `https://your-app.vercel.app`) – set after Vercel deploy
   - `GEMINI_API_KEY`, `SERPER_API_KEY` – Optional
5. Deploy and note your backend URL: `https://scraper-backend.onrender.com`

---

## Step 2: Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com) → **New Project** → Import your repo
2. **Root Directory**: `.` (project root)
3. **Build & Output**: `vercel.json` handles this (builds `frontend/`, outputs `frontend/dist`)
4. **Environment Variables** → Add:
   - `VITE_API_URL` = `https://scraper-backend.onrender.com` (your Render backend URL)
5. Deploy
6. Note your Vercel URL: `https://your-app.vercel.app`

---

## Step 3: Connect Backend to Frontend

1. **Render** → scraper-backend → **Environment** → Set `CORS_ORIGINS` = `https://your-app.vercel.app`
2. Redeploy backend
3. Done – frontend and backend are connected

---

## Other Options

### Both on Render

Use `render.yaml` with both services (add frontend back to render.yaml if needed).

### Both on Railway

Deploy both to Railway. Supports WebSockets and long-running processes.

## Checklist

- [ ] Backend on Render (scraper-backend)
- [ ] Frontend on Vercel
- [ ] `VITE_API_URL` on Vercel = `https://scraper-backend.onrender.com`
- [ ] `CORS_ORIGINS` on Render = `https://your-app.vercel.app` (your Vercel URL)
- [ ] `SECRET_KEY`, `MONGO_URI` set on Render backend
- [ ] MongoDB Atlas Network Access: Allow `0.0.0.0/0` for Render IPs

## Environment Variables

**Render (Backend)** – `SECRET_KEY`, `MONGO_URI`, `CORS_ORIGINS` (your Vercel URL)

**Vercel (Frontend)** – `VITE_API_URL` = `https://scraper-backend.onrender.com`

## Troubleshooting

**MongoDB connection failed** – Add `0.0.0.0/0` to MongoDB Atlas → Network Access

**CORS / Login fails** – Set `CORS_ORIGINS` on Render to your exact Vercel URL (e.g. `https://karki-scrappernew.vercel.app`)

**Backend slow / timeout** – Render free tier spins down after 15 min. First request may take 30–60s to wake up. Wait and retry.

**Create admin** – Run locally with production MONGO_URI: `cd backend && python scripts/create_admin.py admin@example.com YourPassword`

**Check backend** – Visit `https://scraper-backend.onrender.com/api/health` – should return `{"status":"ok"}` when running
