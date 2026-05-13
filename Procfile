release: cd Django-Project/config && python manage.py migrate
web: cd Django-Project/config && gunicorn --bind 0.0.0.0:$PORT --workers 4 config.wsgi
