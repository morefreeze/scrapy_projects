#!/bin/bash
dir=${1:-bj}
for i in ${dir}/[0-9].json; do
    echo "$i"
    while read -r line; do
        echo "$line" | jq --compact-output --raw-output '.data.list' | mongoimport -d lianjia -c "$dir" --jsonArray --mode=upsert --upsertFields=house_code
    done < "$i"
done
