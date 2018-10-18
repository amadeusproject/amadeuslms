#!/bin/bash
set -e

python3 manage.py makemigrations
python3 manage.py migrate --noinput
#python3 initadmin.py
python3 manage.py runserver 0.0.0.0:8000