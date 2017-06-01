#!/bin/bash
dir=${1:-bj}
dir=${dir%/}
for i in ${dir}/[0-9]*.json; do
    echo "$i"
    while read -r line; do
        echo "$line" | jq --compact-output --raw-output '.data.list' | mongoimport -d lianjia -c "$dir" --jsonArray --mode=upsert --upsertFields=house_code
    done < "$i"
    jq --compact-output --raw-output '.data' "$dir/bizcircle_*.json" | mongoimport -d lianjia -c "${dir}_community" --jsonArray --mode=upsert --upsertFields=community_id
done
