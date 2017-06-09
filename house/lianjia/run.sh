#!/bin/bash
code=${1:-110000}
dir=${2:-./}
for i in {1..100}; do
    echo "$i"
    rm -f "bizcircle_${code}.json"
    python get_all_house.py "$code" --output-dir "$dir" && break
    ret=$?
    sleep 1
done
exit "$ret"
