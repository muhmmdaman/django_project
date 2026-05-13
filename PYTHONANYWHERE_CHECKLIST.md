# PythonAnywhere Pre-Deployment Checklist

Use this checklist to verify your project is ready for deployment on PythonAnywhere.

## Code & Repository

- [ ] All code is committed to git
- [ ] `.gitignore` includes virtual environments (`venv/`, `.venv`)
- [ ] `.gitignore` includes `*.sqlite3` and database files
- [ ] `.gitignore` includes `.env` and `.env.local`
- [ ] `.gitignore` includes `__pycache__/` and `*.pyc`
- [ ] `.gitignore` includes `media/` and `staticfiles/`
- [ ] Repository is public or accessible (for cloning)
- [ ] No sensitive data in commits (secrets, API keys, passwords)

## Requirements & Dependencies

- [ ] `requirements.txt` exists and is up to date
- [ ] All dependencies are listed in `requirements.txt`
- [ ] Run `pip freeze > requirements.txt` to ensure accuracy
- [ ] Package versions are compatible with Python 3.11+
- [ ] Test: `pip install -r requirements.txt` works locally
- [ ] No OS-specific packages (use `--platform` if needed)

## Django Configuration

- [ ] `settings.py` uses environment variables for configuration
- [ ] `DEBUG=False` in production settings
- [ ] `SECRET_KEY` is configured from environment variable
- [ ] `ALLOWED_HOSTS` is configured from environment variable
- [ ] Database configuration supports `DATABASE_URL` environment variable
- [ ] Static files configuration includes:
  - `STATIC_URL = "/static/"`
  - `STATIC_ROOT = BASE_DIR / "staticfiles"`
  - `STATICFILES_STORAGE` is configured (WhiteNoise recommended)
- [ ] Media files configuration (if applicable):
  - `MEDIA_URL = "/media/"`
  - `MEDIA_ROOT = BASE_DIR / "media"`
- [ ] Logging is configured
- [ ] Email configuration uses environment variables
- [ ] CSRF and CORS settings are production-ready

## Security Settings

- [ ] `SECURE_SSL_REDIRECT = True` (when not DEBUG)
- [ ] `SESSION_COOKIE_SECURE = True` (when not DEBUG)
- [ ] `CSRF_COOKIE_SECURE = True` (when not DEBUG)
- [ ] `SECURE_HSTS_SECONDS` is configured
- [ ] `SECURE_HSTS_INCLUDE_SUBDOMAINS = True` (when not DEBUG)
- [ ] `SECURE_HSTS_PRELOAD = True` (when not DEBUG)
- [ ] HTTPS is enforced
- [ ] X-Frame-Options is set (default: DENY)

## Database & Migrations

- [ ] All migrations are created: `python manage.py makemigrations`
- [ ] All migrations are committed to git
- [ ] Test migrations locally work: `python manage.py migrate`
- [ ] Database schema is documented (migrations are self-documenting)
- [ ] No missing migration files
- [ ] Production database plan confirmed (PostgreSQL recommended)

## Static & Media Files

- [ ] All static files are organized in `static/` directory
- [ ] WhiteNoise or similar is configured for static file serving
- [ ] Test: `python manage.py collectstatic --noinput` works locally
- [ ] No broken static file references in templates
- [ ] Media files directory exists (if needed): `media/`
- [ ] Static files directory is in `.gitignore`
- [ ] Staticfiles directory is in `.gitignore`

## Environment Configuration

- [ ] `.env.example` exists with all required variables
- [ ] `.env` is in `.gitignore` (never commit sensitive data)
- [ ] All required environment variables are documented
- [ ] Example values in `.env.example` are safe to share
- [ ] `DJANGO_SECRET_KEY` has a strong value (50+ chars, random)
- [ ] `ALLOWED_HOSTS` includes PythonAnywhere domain
- [ ] Database credentials are prepared but NOT in code

## WSGI Configuration

- [ ] `wsgi.py` exists in project root
- [ ] WSGI file correctly imports from Django project
- [ ] WSGI file sets `DJANGO_SETTINGS_MODULE`
- [ ] WSGI file calls `django.setup()`
- [ ] WSGI file returns WSGI application
- [ ] Test: WSGI file works locally

## Testing & Validation

- [ ] Run Django checks: `python manage.py check`
- [ ] Run tests: `python manage.py test` (if tests exist)
- [ ] Test login functionality
- [ ] Test admin panel access
- [ ] Test main features work locally
- [ ] Check for SQL injection vulnerabilities
- [ ] Check for XSS vulnerabilities
- [ ] Verify CSRF protection is working

## Documentation

- [ ] `PYTHONANYWHERE_DEPLOYMENT.md` is created
- [ ] README.md includes project overview
- [ ] Setup instructions are clear
- [ ] Dependencies are listed
- [ ] Contributing guidelines exist

## PythonAnywhere Account Setup

- [ ] PythonAnywhere account created
- [ ] Account plan chosen (appropriate for your needs)
- [ ] API token generated (for automation)
- [ ] Payment method added (if paid plan)
- [ ] Account security settings configured

## Before Deployment

- [ ] Repository link is accessible: `https://github.com/username/repo`
- [ ] All changes are committed
- [ ] No uncommitted changes remain
- [ ] Remote repository is up to date
- [ ] Database backup plan is in place (for existing data)
- [ ] Rollback plan is documented
- [ ] Monitoring/logging plan is confirmed

## Deployment Day

1. [ ] Follow `PYTHONANYWHERE_DEPLOYMENT.md` step by step
2. [ ] Verify each step completes successfully
3. [ ] Check error logs after each major step
4. [ ] Test application in web browser
5. [ ] Verify admin panel works
6. [ ] Test user login (if applicable)
7. [ ] Check static files are loading
8. [ ] Verify database connectivity
9. [ ] Monitor error logs for 30 minutes post-deployment
10. [ ] Document any issues encountered

## Post-Deployment

- [ ] Verify HTTPS certificate is valid
- [ ] Test all major features work in production
- [ ] Set up monitoring alerts (if available)
- [ ] Plan regular backup schedule
- [ ] Set up error tracking (e.g., error.log monitoring)
- [ ] Document production domain and access details
- [ ] Create incident response procedure
- [ ] Schedule security audit if needed
- [ ] Set up automated update reminders for dependencies

---

**Project:** Academic Intelligence System - Django 6.0
**Deployment Target:** PythonAnywhere
**Last Updated:** May 13, 2026
