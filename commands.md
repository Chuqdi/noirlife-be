python manage.py runserver 0.0.0.0:8000
celery -A BE worker -l info
celery -A BE beat -l info