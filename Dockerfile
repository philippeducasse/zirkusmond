FROM python:3.10

RUN apt-get update && apt-get install nginx vim npm -y --no-install-recommends
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log


WORKDIR /usr/src

# Copy and install backend
COPY backend ./backend
RUN pip install -r backend/requirements.txt

# Build frontend
COPY frontend ./frontend
RUN cd frontend && npm install && npm run tailwind && npm run build

COPY ./nginx.default /etc/nginx/sites-available/default

EXPOSE 8000

EXPOSE 8020

CMD ["/usr/src/start-server.sh"]
