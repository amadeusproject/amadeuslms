#!/bin/bash

docker-compose -f docker-compose.prod.yml exec web /usr/local/bin/python3 /code/manage.py crontab run 999f535ae0c282b1c0f65803587eb1ed
docker-compose -f docker-compose.prod.yml exec web /usr/local/bin/python3 /code/manage.py crontab run d92ed41e39a0402c057836e8aae5f98b
