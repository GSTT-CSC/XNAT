#!/usr/bin/env bash
LINE=$(docker ps | egrep xnat-web1 | cut -c1-12)
echo "$LINE"
CSV=$1
PACS=$2
OUTPUT=$3

docker exec -i "$LINE" dos2unix /data/scripts/import-dqr/*
docker exec -i "$LINE" python3 /data/scripts/import-dqr/REST-api-get-data.py /data/scripts/import-dqr/$CSV $PACS /data/scripts/import-dqr/$OUTPUT
