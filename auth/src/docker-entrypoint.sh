#!/bin/sh

alembic upgrade head
python -m cli service init-service-accounts

if [ "$1" = "debug" ]; then
    echo "DEBUG MODE"
    uvicorn auth_app.main:app --host 0.0.0.0 --port 80 --reload
else
    echo "RELEASE MODE"
    gunicorn auth_app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:80 --proxy-allow-from nginx
fi