from src.main.tape_reader import TapeReader
from config import Config
import time

file_name = 'data/test_data/2021041321_LYL.csv'
file1 = open(file_name, 'r')
lines = file1.readlines()

config = Config()
ticker = f"TEST: {file_name.split('/')[-1].split('_')[-1].split('.')[0]}"

time_sale_obj = TapeReader(ticker=ticker, data_writer=False, time_frequency=config.get_time_frequency())

start_time = '21:22:09'
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

        if call_src == config.get_bid_ask_source_name():
            # Call L2
            time_sale_obj.level_ii_api_call(tick_time, bid_price, bid_size, ask_price, ask_size, last_price, last_size)
        else:
            time_sale_obj.time_sales_api_call(tick_time, bid_price, bid_size, ask_price, ask_size, last_price, last_size, 'EXCHANGE')
        time.sleep(0.04)
