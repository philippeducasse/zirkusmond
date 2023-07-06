#!/usr/bin/env bash

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (python /usr/src/manage.py createsuperuser --no-input)
fi
ln -s /usr/src/zirkusmond .
yes yes|python /usr/src/manage.py collectstatic
python /usr/src/manage.py makemigrations events
# python /usr/src/manage.py migrate
chown www-data:www-data -R .
chown www-data:www-data db.sqlite3
gunicorn zirkusmond.wsgi --user www-data --bind 0.0.0.0:8010 --workers 3 &
nginx -g "daemon off;"
