max=100
number_of_records=6
for l in $(seq 1 $max); do
  echo "$l"
  python monitoring/bid_and_ask/bidask_api_call.py "$1" "$number_of_records"
done
