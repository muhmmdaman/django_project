# Academic Intelligence System - Deployment Guide

## Deployment Options

### Option 1: Heroku (Recommended - Easy & Free Tier Available)

1. **Install Heroku CLI**: https://devcenter.heroku.com/articles/heroku-cli

2. **Create Heroku App**:
```bash
heroku login
heroku create your-app-name
```

3. **Add PostgreSQL Database**:
```bash
heroku addons:create heroku-postgresql:mini
```

4. **Set Environment Variables**:
```bash
heroku config:set DJANGO_SECRET_KEY="your-secret-key"
heroku config:set DJANGO_DEBUG="False"
heroku config:set DJANGO_ALLOWED_HOSTS="your-app-name.herokuapp.com"
```

5. **Deploy**:
```bash
git push heroku main
heroku run python manage.py migrate
```

6. **Access**: https://your-app-name.herokuapp.com

---

### Option 2: Docker + Cloud Run (Google Cloud)

1. **Install Google Cloud SDK**: https://cloud.google.com/sdk/docs/install

2. **Authenticate**:
```bash
gcloud auth login
gcloud config set project YOUR-PROJECT-ID
```

3. **Build and Push**:
```bash
docker build -t gcr.io/YOUR-PROJECT-ID/academic-system .
docker push gcr.io/YOUR-PROJECT-ID/academic-system
```

4. **Deploy**:
```bash
gcloud run deploy academic-system \
  --image gcr.io/YOUR-PROJECT-ID/academic-system \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

### Option 3: Docker Compose (Self-hosted/VPS)

**Requirements**: Docker and Docker Compose installed

1. **Update docker-compose.yml** with your settings

2. **Run**:
```bash
docker-compose up -d
```

3. **Access**: http://your-server-ip:8000

---

### Option 4: PythonAnywhere (Beginner-Friendly)

1. Visit: https://www.pythonanywhere.com

2. Upload your code

3. Create web app with Django configuration

4. Get your live URL

---

## Pre-Deployment Checklist

- ✓ WSGI application configured (`config/wsgi.py`)
- ✓ Static files configured (WhiteNoise middleware)
- ✓ Requirements.txt created
- ✓ Environment variables support added
- ✓ Database migrations ready
- ✓ Procfile created (Heroku)
- ✓ Dockerfile created (Docker)
- ✓ docker-compose.yml created (Docker Compose)

## Environment Variables Required

```
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

## Quick Start - Local Docker Testing

```bash
docker-compose up
# Access at http://localhost:8000
```

---

**Recommended**: Use Heroku (Option 1) for quickest deployment with free tier!
