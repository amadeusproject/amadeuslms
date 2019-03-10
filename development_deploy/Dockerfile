FROM python:3.6-alpine
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ARG requirements=requirement_files/development_requirement.txt
RUN echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories
RUN apk add --no-cache --virtual .build-deps \
    ca-certificates gcc postgresql-dev linux-headers musl-dev \
    libffi-dev jpeg-dev zlib-dev bash g++
RUN apk --no-cache --update-cache add gfortran python python-dev gettext
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
RUN apk add libjpeg-turbo-dev zlib-dev
RUN apk add postgresql-libs libxslt-dev
ADD /${requirements} /code/${requirements}
RUN pip install -r /code/${requirements}
ADD . /code/
ENTRYPOINT [ "/code/docker-entrypoint.sh" ]
EXPOSE 8000