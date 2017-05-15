#!/bin/bash
dir=${1:-bj}
for i in ${dir}/*.json; do
    echo "$i"
    jq --compact-output --raw-output '.data.list' "$i" | mongoimport -d lianjia -c bj --jsonArray --mode=upsert --upsertFields=house_code
done
