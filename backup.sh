#!/bin/bash

echo "Starting dumping data on $(date +'%Y-%m-%d %H:%M:%S')"

backup_folder="backup"
max_backup_files=5

mkdir -p "$backup_folder/dump" | true
mkdir -p "$backup_folder/uploads" | true
current_folder="$(pwd)"

echo "Dumping data"
docker exec -t amadeuslms_db_1 pg_dumpall -c -U postgres | gzip > "$backup_folder"/dump/dump_$(date +"%Y-%m-%d_%H_%M_%S").gz
tar -cvzf "$backup_folder"/uploads/uploads_$(date +"%Y-%m-%d_%H_%M_%S").tar.gz amadeus/uploads/

count=`find "$backup_folder/dump" -type f | wc -l`
if [[ $count -gt $max_backup_files ]]; then
    echo "Removing older dump backup from folder"
    cd "$backup_folder/dump"
    rm "$(ls -t | tail -1)"
    cd "$current_folder"
fi

count=`find "$backup_folder/uploads" -type f | wc -l`
if [[ $count -gt $max_backup_files ]]; then
    echo "Removing older uploads backup from folder"
    cd "$backup_folder/uploads"
    rm "$(ls -t | tail -1)"
    cd "$current_folder"
fi

echo -e "Backup finished\n\n"
