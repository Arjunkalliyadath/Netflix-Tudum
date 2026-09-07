#!/usr/bin/env bash
# Render build script.
# In the Render dashboard, set:
#   Build Command: ./build.sh
#   Start Command: gunicorn config.wsgi:application
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py seed_shows
