#!/bin/bash
code=${1:-110000}
for i in {1..1000}; do
    echo "$i"
    rm -f "bizcircle_${code}.json"
    python get_all_house.py "$code"
    sleep 1
done
