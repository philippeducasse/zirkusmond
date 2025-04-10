FROM python:3.10

RUN apt-get update && apt-get install nginx vim npm -y --no-install-recommends
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log


WORKDIR /usr/src/zirkusmond
COPY requirements.txt .
RUN pip install -r requirements.txt
ADD . .
COPY manage.py ..

COPY nginx.default /etc/nginx/sites-available/default

EXPOSE 8000
WORKDIR /srv/data

EXPOSE 8020

RUN ln -s /usr/src/zirkusmond /srv/data/zirkusmond
CMD ["/usr/src/zirkusmond/start-server.sh"]



#
# from django.db import migrations, connection
#from django.utils import timezone
#
#def mark_migration_as_applied(app_label, migration_name):
#    with connection.cursor() as cursor:
#        cursor.execute(
#            """
#            INSERT INTO django_migrations (app, name, applied)
#            VALUES (%s, %s, %s)
#            """,
#            [app_label, migration_name, timezone.now()]
#        )
#        print(f"Marked {app_label}.{migration_name} as applied.")

