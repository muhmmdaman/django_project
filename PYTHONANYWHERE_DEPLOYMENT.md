# PythonAnywhere Deployment Guide - Academic Intelligence System

This guide provides step-by-step instructions to deploy the Django Academic Intelligence System on PythonAnywhere.

## Prerequisites

- PythonAnywhere account (free or paid)
- Git repository access
- PostgreSQL database (recommended for production)
- Domain name (optional, for custom domains)

## Step 1: Create PythonAnywhere Account & Web App

### 1.1 Sign Up
1. Go to [www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Click "Sign up" and create your account
3. Choose the appropriate plan (Beginner/Hacker/Pro)

### 1.2 Create Web App
1. In Dashboard, click "Add a new web app"
2. Choose "Manual configuration"
3. Select **Python 3.11** (or latest available)
4. Click "Next" and complete setup

## Step 2: Clone Your Repository

### 2.1 Open Bash Console
1. Go to "Consoles" → Open a Bash console
2. Navigate to your app directory:
```bash
cd /home/your_username
```

### 2.2 Clone Repository
```bash
git clone https://github.com/your-username/academic-system.git
cd academic-system
```

## Step 3: Set Up Virtual Environment

### 3.1 Create Virtual Environment
```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 3.2 Upgrade pip
```bash
pip install --upgrade pip
```

### 3.3 Install Requirements
```bash
pip install -r requirements.txt
```

## Step 4: Configure Database

### 4.1 Option A: Use PostgreSQL (Recommended)

#### If using PythonAnywhere PostgreSQL:
1. Go to "Databases" tab in your account
2. Click "Create a PostgreSQL database"
3. Set password and note your connection details
4. Connection string format: `postgresql://username:password@postgres.pythonanywhere-services.com/username$database_name`

#### If using external PostgreSQL:
- Ensure your hosting provider allows external connections
- Get your DATABASE_URL connection string

### 4.2 Option B: Use SQLite (Simple, but not recommended for production)
- SQLite will work but has limitations for concurrent users
- Database file: `Django-Project/config/db.sqlite3`

## Step 5: Configure Environment Variables

### 5.1 Create .env File
```bash
nano /home/your_username/academic-system/.env
```

### 5.2 Add Configuration
```bash
# Django Configuration
DJANGO_SETTINGS_MODULE=config.settings
DJANGO_SECRET_KEY=your-very-long-random-secret-key-min-50-chars-change-me
DEBUG=False

# Database
DATABASE_URL=postgresql://username:password@postgres.pythonanywhere-services.com/username$database_name

# Allowed Hosts
ALLOWED_HOSTS=your-username.pythonanywhere.com,your-domain.com

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

**Note:** Replace `your-username`, `your-domain.com`, and database credentials with your actual values.

### 5.3 Generate Secret Key
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Step 6: Initialize Database

### 6.1 Run Migrations
```bash
cd /home/your_username/academic-system/Django-Project/config
python manage.py migrate
```

### 6.2 Create Superuser
```bash
python manage.py createsuperuser
```

### 6.3 Collect Static Files
```bash
python manage.py collectstatic --noinput
```

## Step 7: Configure WSGI File

### 7.1 Open Web App Configuration
1. Go to "Web" tab
2. Click on your web app
3. Under "Code" section, update "WSGI configuration file"

### 7.2 Edit WSGI File
```bash
nano /var/www/your_username_pythonanywhere_com_wsgi.py
```

### 7.3 Replace Content
```python
import os
import sys
from pathlib import Path

# Add project directory to path
project_home = '/home/your_username/academic-system'
sys.path.insert(0, project_home)
sys.path.insert(0, os.path.join(project_home, 'Django-Project', 'config'))

# Activate virtual environment
venv_path = os.path.join(project_home, 'venv', 'lib', 'python3.11', 'site-packages')
sys.path.insert(0, venv_path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
os.environ['HOME'] = '/home/your_username'

# Setup Django
import django
from django.core.wsgi import get_wsgi_application

django.setup()
application = get_wsgi_application()
```

**Important:** Replace `your_username` and `python3.11` with your actual values.

## Step 8: Configure Web App Settings

### 8.1 Web Tab Configuration
1. Go to "Web" tab
2. Under "Virtualenv", set path to: `/home/your_username/academic-system/venv`
3. Under "Source code", set: `/home/your_username/academic-system`
4. Under "Working directory", set: `/home/your_username/academic-system`

### 8.2 Static Files Configuration
1. In "Static files" section, add:
   - **URL:** `/static/`
   - **Directory:** `/home/your_username/academic-system/Django-Project/config/staticfiles`
2. Add media files (if needed):
   - **URL:** `/media/`
   - **Directory:** `/home/your_username/academic-system/Django-Project/config/media`

## Step 9: Reload Web App

### 9.1 Reload Application
1. Go to "Web" tab
2. Click the green "Reload" button
3. Wait for it to complete (usually 2-3 seconds)

### 9.2 Check Status
```
Site running at: https://your_username.pythonanywhere.com
```

## Step 10: Verify Deployment

### 10.1 Test Application
1. Open browser and navigate to: `https://your_username.pythonanywhere.com`
2. Admin panel: `https://your_username.pythonanywhere.com/admin`
3. Login with superuser credentials created in Step 6.2

### 10.2 Check Error Logs
1. Go to "Web" tab
2. Scroll down to "Log files"
3. Review `error.log` for any issues:
```bash
tail -f /var/www/your_username_pythonanywhere_com_wsgi.py
```

## Step 11: Set Up Custom Domain (Optional)

### 11.1 Configure Domain
1. Go to "Web" tab
2. Under "Domains", add your custom domain
3. Update DNS records with PythonAnywhere's nameservers (if using their DNS)

### 11.2 SSL Certificate
- PythonAnywhere provides free SSL certificates via Let's Encrypt
- Automatic renewal included with paid plans

## Step 12: Enable Auto-Reload on Git Updates (Optional)

### 12.1 Set Up Git Hook
```bash
nano /home/your_username/academic-system/.git/hooks/post-merge
```

### 12.2 Add Reload Script
```bash
#!/bin/bash
curl -X POST https://www.pythonanywhere.com/api/v0/user/your_username/webapps/your_username.pythonanywhere.com/reload/ \
  -H "Authorization: Token YOUR_API_TOKEN"
```

Generate API token in "Account" → "API token".

## Troubleshooting

### Problem: "ModuleNotFoundError" or "ImportError"
**Solution:**
1. Check virtualenv path in Web settings
2. Verify Python version matches requirements
3. Run: `pip install -r requirements.txt`

### Problem: Database Connection Error
**Solution:**
1. Verify DATABASE_URL in .env
2. Check database credentials and IP whitelist
3. For external DB: ensure PythonAnywhere IP is whitelisted

### Problem: Static Files Not Loading
**Solution:**
1. Run: `python manage.py collectstatic --noinput`
2. Verify static files path in Web settings
3. Check file permissions: `chmod -R 755 staticfiles/`

### Problem: "Allowed host not valid"
**Solution:**
1. Update ALLOWED_HOSTS in .env
2. Include your domain: `your-domain.com,www.your-domain.com`
3. Reload web app

### Problem: 500 Internal Server Error
**Solution:**
1. Check error.log for detailed error message
2. Set `DEBUG=True` temporarily in .env to see full traceback
3. Verify all settings and dependencies are correct
4. Restart bash console and reload web app

## Maintenance & Updates

### Update Code
```bash
cd /home/your_username/academic-system
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
python Django-Project/config/manage.py migrate
python Django-Project/config/manage.py collectstatic --noinput
```

### Reload Web App
- Web tab → Click "Reload" button
- Or via API using your token

### Database Backups
- PythonAnywhere PostgreSQL: automatic daily backups (paid plans)
- Manual backup: `pg_dump` command via bash console

## Security Checklist

- ✅ Set strong DJANGO_SECRET_KEY
- ✅ DEBUG=False in production
- ✅ Use HTTPS (SSL certificate configured)
- ✅ SECURE_SSL_REDIRECT=True
- ✅ ALLOWED_HOSTS configured correctly
- ✅ Database credentials secured in .env
- ✅ Regular security updates for Django packages
- ✅ Enable 2FA on PythonAnywhere account
- ✅ Regular database backups

## Performance Tips

1. **Use PostgreSQL** instead of SQLite for better concurrency
2. **Enable caching** - configure Redis if available
3. **Optimize queries** - use Django Debug Toolbar in development
4. **Compress static files** - enabled by default (WhiteNoise)
5. **Monitor logs** - check error.log regularly
6. **Set appropriate SECURE_HSTS_SECONDS** for HTTPS enforcement

## Useful Commands

```bash
# SSH into PythonAnywhere
ssh your_username@ssh.pythonanywhere.com

# View logs in real-time
tail -f /var/www/your_username_pythonanywhere_com_wsgi.py

# Check disk usage
df -h

# List running processes
ps aux

# Restart Python shell
source /home/your_username/academic-system/venv/bin/activate
```

## Support & Resources

- [PythonAnywhere Documentation](https://help.pythonanywhere.com/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/)
- [PythonAnywhere Help Forum](https://www.pythonanywhere.com/forums/)

---

**Last Updated:** May 13, 2026
**Django Version:** 6.0.3
**Python Version:** 3.11+
