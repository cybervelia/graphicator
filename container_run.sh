#!/bin/sh
cd /app
python /app/graphicator.py "$@" && echo "Webserver listening, port 80" && zip -r /tmp/all.zip /app/reqcache /app/reqcache-intro /app/reqcache-queries && mv /tmp/all.zip /app && python -m http.server 80

