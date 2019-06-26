web: gunicorn fimdb_api_grouplens.wsgi --log-file -
worker: celery worker -A fimdb_api_grouplens -E -l debug
