#!/bin/bash

if [[ "${1}" == "celery" ]]; then
    celery --app=src.app.tasks.celery:celery worker -l INFO
elif [[ "${1}" == "flower" ]]; then
    celery --app=src.app.tasks.celery:celery flower
else
    echo "Usage: $0 {celery|flower}"
    exit 1
fi
