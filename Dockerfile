FROM python:3.8-slim

WORKDIR /code
ADD requirement_files/development.txt requirement_files/development.txt

RUN apt-get update -y \
    && apt-get install -y \
    libpq-dev \
    gcc \
    gettext \
    && pip install -r /code/requirement_files/development.txt

ADD . .

EXPOSE 8000

# ENTRYPOINT bash /code/docker-entrypoint.sh
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
ENTRYPOINT [ "tail", "-f", "/dev/null" ]
