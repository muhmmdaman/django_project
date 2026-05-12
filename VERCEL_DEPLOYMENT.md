# Vercel Deployment Guide for Academic Intelligence System

## Quick Setup (5 minutes)

### 1. Install Vercel CLI (Optional)
```bash
npm install -g vercel
```

### 2. Connect GitHub Repository
- Go to https://vercel.com/new
- Click "Import Git Repository"
- Select your GitHub repo
- Vercel will auto-detect Django and configure it

### 3. Set Environment Variables
In Vercel Dashboard → Settings → Environment Variables, add:

```
DJANGO_SECRET_KEY=your-long-random-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-project-name.vercel.app
DATABASE_URL=postgresql://user:password@host/dbname
```

### 4. Deploy
Push to GitHub:
```bash
git push origin main
```
Vercel will automatically deploy!

---

## Files Created for Vercel Compatibility

| File | Purpose |
|------|---------|
| `wsgi.py` | Root WSGI entrypoint (Vercel requirement) |
| `pyproject.toml` | Python project config with Vercel settings |
| `vercel.json` | Vercel-specific build and routing configuration |
| `.vercelignore` | Files to exclude from Vercel deployment |

---

## How It Works

1. **wsgi.py** - Exposes Django application at root level where Vercel can find it
2. **pyproject.toml** - Tells Vercel where to find the WSGI application
3. **vercel.json** - Configures build process and routing
4. **requirements.txt** - Already configured, Vercel installs automatically

---

## Environment Variables on Vercel

Required variables to set in Vercel Dashboard:

| Variable | Example | Description |
|----------|---------|-------------|
| DJANGO_SECRET_KEY | `django-insecure-xyz...` | Generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| DJANGO_DEBUG | False | Always False in production |
| DJANGO_ALLOWED_HOSTS | your-app.vercel.app | Your Vercel domain |
| DATABASE_URL | postgresql://... | If using external database |

---

## For PostgreSQL Database

### Option 1: Use External Database
- Get PostgreSQL URL from service (AWS RDS, Railway, Heroku Postgres, etc.)
- Add as DATABASE_URL environment variable

### Option 2: Use SQLite (Default)
- Database file is stored in `/tmp` (ephemeral storage)
- Data persists only during build
- **Recommended**: Use external PostgreSQL for production

---

## Static Files

- Already configured with WhiteNoise middleware
- Static files automatically collected during build
- Images, CSS, JS served correctly

---

## Common Issues & Fixes

### Issue: "No Django entrypoint found"
✓ Fixed by creating `wsgi.py` and `pyproject.toml`

### Issue: Database not found
✓ Set DATABASE_URL in Vercel environment variables

### Issue: Static files not loading
✓ Already configured with WhiteNoise, should work

### Issue: 502 Bad Gateway
✓ Check build logs in Vercel Dashboard
✓ Ensure all environment variables are set

---

## Deployment Steps

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add Vercel configuration"
   git push origin main
   ```

2. **Connect to Vercel**:
   - Go to https://vercel.com
   - Click "New Project"
   - Import your GitHub repository

3. **Configure Environment Variables**:
   - Project Settings → Environment Variables
   - Add all required variables
   - Save

4. **Deploy**:
   - Click Deploy
   - Wait for build to complete (~2-3 minutes)
   - Get your live URL!

---

## Your Live URL

After deployment:
```
https://your-project-name.vercel.app
```

---

## Monitoring & Logs

View deployment logs in Vercel Dashboard:
- Deployments tab → Select deployment → Logs
- Shows build process and any errors

---

## Next Steps

1. Test all features on live site
2. Update DNS (if using custom domain)
3. Set up error tracking (optional)
4. Monitor performance

Your app is live! 🚀
