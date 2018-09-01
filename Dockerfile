FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN pip install -r requirements.txt
ENTRYPOINT [ "/code/docker-entrypoint.sh" ]
EXPOSE 8000