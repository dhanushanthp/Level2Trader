from monitoring.time_sales_on_bid_ask.time_and_sales_on_bid_ask import TimeSalesBidAsk
import time

file1 = open('test_data/bid_ask_last.csv', 'r')
lines = file1.readlines()
lines = lines[1:]

time_sale_obj = TimeSalesBidAsk(ticker='AAPL', multiple_of_10sec=12)

for line in lines:
    time.sleep(0.1)
    # Select individual price and size by the feed
    line_split = line.split(',')
    tick_time = line_split[0].split(' ')[-1]
    bid_price = float(line_split[1])
    bid_size = int(line_split[2])
    ask_price = float(line_split[3])
    ask_size = int(line_split[4])
    last_price = float(line_split[5])
    last_size = int(line_split[6])
    time_sale_obj.data_generator(tick_time, bid_price, bid_size, ask_price, ask_size, last_price, last_size)
