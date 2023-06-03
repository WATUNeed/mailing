#!/bin/sh

cd /app

/bin/bash -c 'source /opt/venv/bin/activate &&
alembic revision --autogenerate -m "init" &&
alembic upgrade head && python3 /app/main.py'