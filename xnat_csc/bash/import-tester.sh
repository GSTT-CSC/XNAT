#!/usr/bin/env bash
LINE=$(docker ps | egrep xnat-web1 | cut -c1-12)
echo "$LINE"
#docker exec -it "$LINE" /bin/bash  
CSV=$1
PROJECT=$2
PACS=$3
DESC=$4

docker exec -it "$LINE" dos2unix /data/scripts/import-dqr/*
docker exec -it "$LINE" python3 /data/scripts/import-dqr/import-tester.py /data/scripts/import-dqr/$CSV $PROJECT $PACS $DESC 
