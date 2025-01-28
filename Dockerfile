# Step 1: Frontend Build
FROM node:22 AS frontend-build

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Step 2: Backend Build
FROM python:3.11-slim

WORKDIR /app
COPY backend/ /app/

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libc-dev \
    supervisor && \
    pip install --upgrade pip && \
    pip install -r /app/requirements.txt && \
    apt-get purge -y gcc libffi-dev libc-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /var/log/supervisor

COPY --from=frontend-build /backend/dist /app/dist

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

COPY supervisord.conf /etc/supervisord.conf
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
