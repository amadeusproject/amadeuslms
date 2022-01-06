FROM python:3.8-slim

WORKDIR /code
ADD requirement_files/development.txt requirement_files/development.txt

# packages needed to build packages from source
RUN apt-get update -y && apt-get install -y libtiff5-dev libjpeg62-turbo-dev libopenjp2-7-dev zlib1g-dev \
    libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk \
    libharfbuzz-dev libfribidi-dev libxcb1-dev libssl-dev
RUN apt-get install -y \
    libpq-dev \
    gcc \
    gettext \
    cron \
    && pip install -r /code/requirement_files/development.txt

ADD . .

ENTRYPOINT ["bash", "./docker-entrypoint.sh"]
