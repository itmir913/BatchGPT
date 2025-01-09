# Step 1: Frontend Build
FROM node:16-alpine AS frontend-build

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Step 2: Backend Build
FROM python:3.10-alpine

WORKDIR /app
COPY backend/ /app/

# Alpine 패키지 관리자를 사용하여 필요한 패키지 설치 및 pip 종속성 설치
RUN apk update && apk add --no-cache gcc libffi-dev musl-dev supervisor && \
    pip install --upgrade pip && \
    pip install -r /app/requirements.txt && \
    rm -rf /var/cache/apk/* && \
    mkdir -p /var/log/supervisor

# Backend 소스 및 Frontend 빌드 결과 복사
COPY --from=frontend-build /backend/dist /app/dist

# Supervisor 설정 파일 복사
COPY supervisord.conf /etc/supervisord.conf

# Supervisor 실행
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
