max=100
number_of_records=25
for l in $(seq 1 $max); do
  echo "$l"
  python monitoring/time_and_sales/time_and_sales_api_call.py "$1" "$number_of_records"
done
