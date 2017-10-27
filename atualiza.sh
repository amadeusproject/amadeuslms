#!/bin/bash

# variáveis
asgi=amadeus.asgi # endereço de onde está o asgi do projeto
wsgi=amadeus.wsgi # endereço de onde está o wsgi do projeto
env=../env/bin/activate # endereço de onde está o virtualenv
port=6379 # porta onde vai ser aberto para o websocket
requeriments=requirements.txt # localização do arquivo de requeriments


kill -9 `ps -ef | grep -i gunicorn | awk '{print $2}'` # matar o gunicorn se ele estiver executando
kill -9 `ps -ef | grep -i daphne | awk '{print $2}'` # matar o daphne se ele estiver executando
source $env # ativar o virtualenv
git pull # baixar as atualização do git
pip install -r $requeriments # instalar ou requeriments adicionandos
python manage.py migrate --no-input # dá migrate no banco de dados
python manage.py compilemessages # atualizar as mensagens traduzidas
python manage.py collectstatic --no-input # atualizar os arquivos estaticos
daphne -p $port $asgi:channel_layer & # executar o daphne na port $port
gunicorn -D $wsgi:application # executar o gunicorn em backgraund
