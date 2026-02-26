#!/bin/sh

granian \
    --interface asgi \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1 \
    --loop uvloop \
    --backlog 4096 \
    --no-ws \
    app.main:app
