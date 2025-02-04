#!/bin/sh

n=0
while [ $n -lt 5 ]
do
    python manage.py migrate --no-input && break
    n=$((n+1))  # n 증가
    echo "Failed to migrate. Retrying in 8 seconds... ($n/5)"
    sleep 8
done

exec supervisord -n -c /etc/supervisord.conf
