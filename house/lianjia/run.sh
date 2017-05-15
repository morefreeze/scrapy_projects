code=${1:-110000}
for ((i=0;i < 1000; i++)); do
    echo "$i"
    rm -f "bizcircle_${code}.json"
    python get_all_house.py "$@"
    sleep 1
done
