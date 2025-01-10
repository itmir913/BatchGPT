# Step 1: Frontend Build
FROM node:22-alpine AS frontend-build

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Step 2: Backend Build
FROM python:3.12-alpine

WORKDIR /app
COPY backend/ /app/

RUN apk update && apk add --no-cache gcc libffi-dev musl-dev supervisor && \
    pip install --upgrade pip && \
    pip install -r /app/requirements.txt && \
    rm -rf /var/cache/apk/* && \
    mkdir -p /var/log/supervisor

COPY --from=frontend-build /backend/dist /app/dist

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

COPY supervisord.conf /etc/supervisord.conf
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
