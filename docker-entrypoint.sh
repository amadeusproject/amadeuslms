#!/bin/bash

service cron start
python3 manage.py makemigrations
python3 manage.py migrate users
python3 manage.py migrate
python3 manage.py compilemessages
python3 manage.py collectstatic --no-input
python3 manage.py crontab add
python3 manage.py runserver 0.0.0.0:8000
