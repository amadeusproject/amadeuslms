#!/bin/bash

docker-compose -f docker-compose.prod.yml build
bash ./backup.sh
docker-compose -f docker-compose.prod.yml up -d
