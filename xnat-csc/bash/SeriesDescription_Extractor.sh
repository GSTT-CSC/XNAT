#!/usr/bin/env bash
LINE=$(docker ps | egrep xnat-web1 | cut -c1-12)
echo "$LINE"
PATH=$1
OUTPUT=$2

docker exec -i "$LINE" python3 /data/scripts/import-dqr/SeriesDescription_Extractor.py $PATH /data/scripts/import-dqr/$OUTPUT
