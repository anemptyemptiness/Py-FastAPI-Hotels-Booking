#!/bin/bash

if [ "${1}" == "celery_app" ]; then
  celery -app=app.tasks.celery_app:celery_app worker -l INFO
elif [ "${1}" == "flower" ]; then
  celery -app=app.tasks.celery_app:celery_app flower
fi