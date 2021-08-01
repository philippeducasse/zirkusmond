FROM python

RUN apt-get update && apt-get install nginx vim npm -y --no-install-recommends
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log


WORKDIR /usr/src/zirkusmond
COPY requirements.txt .
RUN pip install -r requirements.txt
ADD . .
COPY manage.py ..

#RUN python ../manage.py makemigrations
#RUN python ../manage.py makemigrations events
#RUN python ../manage.py migrate
#RUN python ../manage.py collectstatic

COPY nginx.default /etc/nginx/sites-available/default

EXPOSE 8000
WORKDIR /srv/data
#CMD ["python", "/usr/src/manage.py", "runserver", "0.0.0.0:8000"]
EXPOSE 8020
#STOPSIGNAL SIGTERM
RUN ln -s /usr/src/zirkusmond /srv/data/zirkusmond
CMD ["/usr/src/zirkusmond/start-server.sh"]
