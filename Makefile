ARGS=web

stop:
	docker container stop $$(docker container ls -q) | true

stop-containers:
	docker-compose stop $$ARGS | true

remove-containers: stop-containers
	docker-compose rm -f $$ARGS | true

build:
	docker-compose build

up:
	docker-compose up -d

logs:
	docker-compose logs -f --tail=100 $(ARGS)

restart:
	docker-compose restart $(ARGS)

bash:
	docker-compose exec $(ARGS) bash

ps:
	docker-compose ps
