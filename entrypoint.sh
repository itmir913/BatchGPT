#!/bin/sh

python manage.py makemigrations
python manage.py migrate

python /app/manage.py runserver 0.0.0.0:8000

#exec gunicorn backend.wsgi:application --bind 0.0.0.0:8000
