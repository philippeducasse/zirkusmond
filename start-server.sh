#!/usr/bin/env bash

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (python /usr/src/backend/manage.py createsuperuser --no-input)
fi

yes yes|python /usr/src/backend/manage.py collectstatic

python /usr/src/backend/manage.py migrate events
python /usr/src/backend/manage.py migrate newsletter
python /usr/src/backend/manage.py migrate rentals

gunicorn config.wsgi --pythonpath /usr/src/backend --user www-data --bind 0.0.0.0:8010 --workers 3 --timeout 240 &

nginx -g "daemon off;"

