max=100
for l in $(seq 1 $max); do
  echo "$l"
  python src/top_sales/tape_reader_api_call.py "$1"
done
