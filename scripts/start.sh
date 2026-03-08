#!/bin/sh

granian \
    --interface asgi \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1 \
    --loop uvloop \
    --no-ws \
    --respawn-failed-workers \
    app.main:app
