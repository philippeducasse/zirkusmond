#!/usr/bin/env bash

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (python /usr/src/backend/manage.py createsuperuser --no-input)
fi

yes yes|python /usr/src/backend/manage.py collectstatic

cp -r /usr/src/backend/staticfiles/* /srv/data/static/ 2>/dev/null || true

python /usr/src/backend/manage.py migrate


gunicorn config.wsgi --pythonpath /usr/src/backend --user www-data --bind 0.0.0.0:8010 --workers 3 --timeout 240 &

nginx -g "daemon off;"

