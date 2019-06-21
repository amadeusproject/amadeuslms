FROM python:3.7-slim
ENV PYTHONUNBUFFERED 1
ARG requirements=requirement_files/development_requirement.txt
RUN apt-get update && apt-get install -y gcc libpq-dev gettext
#RUN echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories
#RUN apk add --no-cache --virtual .build-deps \
#    ca-certificates gcc postgresql-dev linux-headers musl-dev \
#    libffi-dev jpeg-dev zlib-dev bash g++
#RUN apk --no-cache --update-cache add gfortran python python-dev gettext
#RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
#RUN apk add libjpeg-turbo-dev zlib-dev
#RUN apk add postgresql-libs libxslt-dev
ENV PIP_DEFAULT_TIMEOUT=100
ADD /${requirements} /code/${requirements}
RUN pip install -r /code/${requirements}
WORKDIR /code
ADD . /code/
ENTRYPOINT [ "/code/docker-entrypoint.sh" ]
EXPOSE 8000