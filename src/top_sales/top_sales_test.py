from src.top_sales.tape_reader_top_sales import TapeReader
import time

file1 = open('data/test_data/2021040522_XELB.csv', 'r')
lines = file1.readlines()

time_sale_obj = TapeReader(ticker='TEST', data_writer=False)

start_time = '22:09:08'
enabler = False

for line in lines:
    # Select individual price and size by the feed

    line_split = line.split(',')
    tick_time = line_split[0].split(' ')[-1]
    if tick_time == start_time:
        enabler = True

    if enabler:
        bid_price = float(line_split[1])
        bid_size = int(line_split[2])
        ask_price = float(line_split[3])
        ask_size = int(line_split[4])
        last_price = float(line_split[5])
        last_size = int(line_split[6])
        call_src = str(line_split[7]).replace('\n', '')

        if call_src == 'l2':
            # Call L2
            time_sale_obj.level_ii_api_call(tick_time, bid_price, bid_size, ask_price, ask_size, last_price, last_size)
        else:
            time_sale_obj.time_sales_api_call(tick_time, bid_price, bid_size, ask_price, ask_size, last_price, last_size, 'EXCHANGE')
        time.sleep(0.03)