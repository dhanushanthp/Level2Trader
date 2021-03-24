from time_and_sales import TimeAndSales
import time

file1 = open('test_data/last.csv', 'r')
lines = file1.readlines()
lines = lines[1:]

time_sale_obj = TimeAndSales(ticker='AAPL', last_x_min=2)
for line in lines:
    time.sleep(0.5)
    # Select individual price and size by the feed
    line_split = line.split(',')
    var_time = line_split[0].split(' ')[-1]
    var_value = float(line_split[1])
    var_size = int(line_split[2])
    var_exchange = line_split[3]
    time_sale_obj.data_generator(var_time, var_value, var_size, var_exchange)
