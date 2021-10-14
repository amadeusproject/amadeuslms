# Amadeus

Amadeus is a LMS (Learning Management System) with a focus on analytics, usability and performance. The main goal is to provide a focused environment where students and teacher can self assess their performance.


1. Architecture Overview
2. Configuration
    - How to run locally with docker and docker compose [pt-br](https://github.com/amadeusproject/amadeuslms/wiki/Executar-projeto-com-docker-compose)
    - How to develop locally using Docker [en-us]() / [pt-br](https://github.com/amadeusproject/amadeuslms/wiki/Guia-Docker-Desenvolvimento)
    - How to deploy using Heroku (in construction)
    - How to deploy using AWS (in construction)
3. How to contribute
    - There is a contribution guide for developers [en-us]() / [pt-br](https://github.com/amadeusproject/amadeuslms/wiki/Guia-de-colabora%C3%A7%C3%A3o)
    - The contribution guide for designers [en-us]() / [pt-br](https://github.com/amadeusproject/amadeuslms/wiki/Guia-de-Design)
    - A documentation of the API [en-us](https://github.com/amadeusproject/amadeuslms/wiki/API-Docs) / [pt-br]()

** Architecture Overview **

# Backup and restore

## Backup

```bash
docker exec -t amadeuslms_db_1 pg_dumpall -c -U postgres > dump_`date +%Y-%m-%d_%H_%M_%S`.sql
```

## Backup (compressed)
```bash
docker exec -t amadeuslms_db_1 pg_dumpall -c -U postgres | gzip > ./dump_$(date +"%Y-%m-%d_%H_%M_%S").gz
```

## Restore
```bash
cat dump.sql | docker exec -i amadeuslms_db_1 psql -U postgres
```

## Restore (compressed)
```bash
gunzip < dump.gz | docker exec -i amadeuslms_db_1 psql -U postgres
```

## Automatic backup

To set automatic backup, run `crontab -e` on terminal and add the line below to the created file
```
30 2 * * * cd /root/amadeuslms && bash ./backup.sh >> cron.log
0 5 * * * cd /root/amadeuslms && bash ./jobs.sh >> cron.log
```

# TODO


** Sources of information **
pt-br: https://softwarepublico.gov.br/social/amadeus
