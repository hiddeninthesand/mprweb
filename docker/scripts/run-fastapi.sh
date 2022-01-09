#!/bin/bash

CERT=/data/localhost.cert.pem
KEY=/data/localhost.key.pem

# If production.{cert,key}.pem exists, prefer them. This allows
# user customization of the certificates that FastAPI uses.
if [ -f /data/production.cert.pem ]; then
    CERT=/data/production.cert.pem
fi
if [ -f /data/production.key.pem ]; then
    KEY=/data/production.key.pem
fi

# By default, set FASTAPI_WORKERS to 2. In production, this should
# be configured by the deployer.
if [ -z ${FASTAPI_WORKERS+x} ]; then
    FASTAPI_WORKERS=2
fi

export FASTAPI_BACKEND="$1"

echo "FASTAPI_BACKEND: $FASTAPI_BACKEND"
echo "FASTAPI_WORKERS: $FASTAPI_WORKERS"

# Perform migrations.
alembic upgrade head

if [ "$1" == "uvicorn" ] || [ "$1" == "" ]; then
    exec uvicorn --reload \
        --ssl-certfile "$CERT" \
        --ssl-keyfile "$KEY" \
        --log-config /docker/logging.conf \
        --host "0.0.0.0" \
        --port 8000 \
        aurweb.asgi:app
elif [ "$1" == "gunicorn" ]; then
    exec gunicorn \
        --keyfile="$KEY" \
        --certfile="$CERT" \
        --log-config /docker/logging.conf \
        --bind "0.0.0.0:8000" \
        -w $FASTAPI_WORKERS \
        -k uvicorn.workers.UvicornWorker \
        aurweb.asgi:app
elif [ "$1" == "hypercorn" ]; then
    exec hypercorn --reload \
        --certfile "$CERT" \
        --keyfile "$KEY" \
        --log-config /docker/logging.conf \
        -b "0.0.0.0:8000" \
        aurweb.asgi:app
else
    echo "Error: Invalid \$FASTAPI_BACKEND supplied."
    echo "Valid backends: 'uvicorn', 'gunicorn', 'hypercorn'."
    exit 1
fi
