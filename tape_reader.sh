max=100
for l in $(seq 1 $max); do
  echo "$l"
  python src/main/tape_reader_api_call.py "$1"
done
