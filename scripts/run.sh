#!/bin/sh

# If any command fails, stop the script
set -e

# Django setup
python manage.py wait_for_db
python manage.py collectstatic --noinput  # collect static files
python manage.py migrate

# Run on TCP socket port 9000, set uwsgi daemon as master thread, module runs /app/app/wsgi.py
uwsgi --socket :9000 --workers 4 --master --enable-threads --module app.wsgi
