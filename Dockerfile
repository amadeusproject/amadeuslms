FROM python:3.8-slim

WORKDIR /code
ADD requirement_files/development.txt requirement_files/development.txt

RUN apt-get update -y \
    && apt-get install -y \
    libpq-dev \
    gcc \
    gettext \
    cron \
    && pip install -r /code/requirement_files/development.txt

ADD . .

ENTRYPOINT ["bash", "./docker-entrypoint.sh"]
