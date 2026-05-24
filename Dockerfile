FROM python:3.10

RUN apt-get update && apt-get install nginx vim npm -y --no-install-recommends
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log


WORKDIR /usr/src

# Copy start-server script
COPY start-server.sh .
RUN chmod +x start-server.sh
# Copy and install backend
COPY backend ./backend
RUN pip install -r backend/requirements.txt

# Build frontend
COPY frontend ./frontend
RUN cd frontend && npm install && npm run tailwind && npm run build

# Copy node_modules dependencies to static for HTML references
RUN mkdir -p /usr/src/backend/static/media/dist/@glidejs && \
    cp -r /usr/src/frontend/node_modules/@glidejs /usr/src/backend/static/media/dist/

COPY ./nginx.default /etc/nginx/sites-available/default

RUN mkdir -p /srv/data/static /srv/data/media

EXPOSE 8000

CMD ["/usr/src/start-server.sh"]

# FROM python:3.10-slim

# RUN apt-get update && apt-get install -y --no-install-recommends \
#     nginx nodejs npm \
#     && rm -rf /var/lib/apt/lists/*

# RUN ln -sf /dev/stdout /var/log/nginx/access.log \
#     && ln -sf /dev/stderr /var/log/nginx/error.log

# WORKDIR /usr/src

# COPY start-server.sh .
# RUN chmod +x start-server.sh

# # pip cache layer
# COPY backend/requirements.txt ./backend/requirements.txt
# RUN pip install --no-cache-dir -r backend/requirements.txt

# # npm cache layer
# COPY frontend/package*.json ./frontend/
# RUN cd frontend && npm ci

# # Now copy full source
# COPY backend ./backend
# COPY frontend ./frontend

# RUN cd frontend && npm run tailwind && npm run build

# RUN mkdir -p /usr/src/backend/static/media/dist/@glidejs && \
#     cp -r /usr/src/frontend/node_modules/@glidejs /usr/src/backend/static/media/dist/

# COPY ./nginx.default /etc/nginx/sites-available/default
# RUN mkdir -p /srv/data/static /srv/data/media

# EXPOSE 8000
# CMD ["/usr/src/start-server.sh"]