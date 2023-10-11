#!/usr/bin/env bash
LINE=$(docker ps | egrep xnat-web | cut -c1-12)
echo "$LINE"
 
CSV=$1
PROJECT=$2
PACS=$3

docker exec -it "$LINE" dos2unix /data/scripts/import-dqr/*
docker exec -it "$LINE" python3 /data/scripts/import-dqr/import-via-restapi.py /data/scripts/import-dqr/$CSV $PROJECT $PACS 
