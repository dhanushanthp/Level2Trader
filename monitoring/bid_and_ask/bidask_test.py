from bidask import BidAsk
import time

file1 = open('test_data/bidask.csv', 'r')
lines = file1.readlines()
lines = lines[1:]

time_sale_obj = BidAsk(ticker='AAPL', multiple_of_10sec=6)
for line in lines:
    time.sleep(0.5)
    # Select individual price and size by the feed
    line_split = line.split(',')
    var_time = line_split[0].split(' ')[-1]
    bid_price = float(line_split[1])
    bid_size = int(line_split[2])
    ask_price = float(line_split[3])
    ask_size = int(line_split[4])
    time_sale_obj.data_generator(var_time, bid_price, bid_size, ask_price, ask_size)
