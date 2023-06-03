#!/bin/sh

cd /app

/bin/bash -c 'source /opt/venv/bin/activate &&
celery --app=tasks.tasks:celery worker -l INFO'