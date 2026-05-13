# PythonAnywhere Quick Reference

## 30-Second Summary

1. Create PythonAnywhere account
2. Clone repo → Install dependencies
3. Set up PostgreSQL database
4. Configure environment variables (.env)
5. Run migrations & collect static files
6. Update WSGI configuration
7. Configure web app settings
8. Reload and test

## Essential Commands

```bash
# Clone and setup
git clone https://github.com/your-username/academic-system.git
cd academic-system
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Database setup
cd Django-Project/config
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput

# Test server (local)
python manage.py runserver
```

## Environment Variables (.env)

```
DJANGO_SECRET_KEY=your-50-char-random-key
DEBUG=False
DATABASE_URL=postgresql://user:pass@host/dbname
ALLOWED_HOSTS=your-username.pythonanywhere.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Key Paths (PythonAnywhere)

| Item | Path |
|------|------|
| Project Home | `/home/your_username/academic-system` |
| Virtual Env | `/home/your_username/academic-system/venv` |
| WSGI File | `/var/www/your_username_pythonanywhere_com_wsgi.py` |
| Static Files | `Django-Project/config/staticfiles/` |
| Media Files | `Django-Project/config/media/` |
| Error Log | `/var/www/your_username_pythonanywhere_com_wsgi.py` |

## WSGI File Template

```python
import os, sys
project_home = '/home/your_username/academic-system'
sys.path.insert(0, project_home)
sys.path.insert(0, os.path.join(project_home, 'Django-Project', 'config'))
sys.path.insert(0, os.path.join(project_home, 'venv', 'lib', 'python3.11', 'site-packages'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
os.environ['HOME'] = '/home/your_username'

import django
from django.core.wsgi import get_wsgi_application
django.setup()
application = get_wsgi_application()
```

## Web App Configuration (Web Tab)

- **Virtualenv:** `/home/your_username/academic-system/venv`
- **Source code:** `/home/your_username/academic-system`
- **Working directory:** `/home/your_username/academic-system`

**Static files:**
- URL: `/static/` → Directory: `Django-Project/config/staticfiles/`
- URL: `/media/` → Directory: `Django-Project/config/media/`

## Common Issues & Fixes

| Problem | Fix |
|---------|-----|
| ModuleNotFoundError | Check virtualenv path, pip install requirements |
| Database error | Verify DATABASE_URL, check credentials |
| Static files missing | Run collectstatic, check path in Web settings |
| Host not valid | Add domain to ALLOWED_HOSTS in .env |
| 500 error | Check error.log, set DEBUG=True temporarily |

## Useful Links

- [Full Deployment Guide](./PYTHONANYWHERE_DEPLOYMENT.md)
- [Pre-Deployment Checklist](./PYTHONANYWHERE_CHECKLIST.md)
- [PythonAnywhere Help](https://help.pythonanywhere.com/)
- [Django Docs](https://docs.djangoproject.com/en/6.0/)

---

**Project:** Academic Intelligence System
**Updated:** May 13, 2026
