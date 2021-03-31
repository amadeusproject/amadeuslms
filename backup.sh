#!/bin/bash

echo "Starting dumping data on $(date +'%Y-%m-%d %H:%M:%S')"

backup_folder="backup"
max_backup_files=5

mkdir -p $backup_folder | true

echo "Dumping data"
docker exec -t amadeuslms_db_1 pg_dumpall -c -U postgres | gzip > $backup_folder/dump_$(date +"%Y-%m-%d_%H_%M_%S").gz

count=`find $backup_folder -type f | wc -l`
if [[ $count -gt $max_backup_files ]]; then
    echo "Removing older backup from folder"
    cd $backup_folder
    rm "$(ls -t | tail -1)"
fi

echo -e "Backup finished\n\n"
