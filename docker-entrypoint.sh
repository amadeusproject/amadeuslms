#!/bin/bash
set -e

# update the staticfiles directory
python3 manage.py collectstatic --no-input
python3 manage.py makemigrations
python3 manage.py migrate 
python3 manage.py compilemessages
gunicorn --bind :$PORT amadeus.wsgi:application