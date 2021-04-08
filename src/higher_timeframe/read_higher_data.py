from src.main.tape_reader import TapeReader
import time


class HigherScale:
    def __init__(self):
        self.file = 'data/tape_data/tape_data_higher_frame.csv'
        self.time_sale_obj = TapeReader(ticker='HigerFrame', data_writer=False, time_frequency=30)

    def read_data(self):
        file1 = open(self.file, 'r')
        lines = file1.readlines()
        return lines

    def generate_output(self):
        lines = self.read_data()
        for line in lines:
            line_split = line.split(',')
            tick_time = line_split[0].split(' ')[-1]
            bid_price = float(line_split[1])
            bid_size = int(line_split[2])
            ask_price = float(line_split[3])
            ask_size = int(line_split[4])
            last_price = float(line_split[5])
            last_size = int(line_split[6])
            call_src = str(line_split[7]).replace('\n', '')

            if call_src == 'l2':
                # Call L2
                self.time_sale_obj.level_ii_api_call(tick_time, bid_price, bid_size, ask_price, ask_size, last_price, last_size)
            else:
                self.time_sale_obj.time_sales_api_call(tick_time, bid_price, bid_size, ask_price, ask_size, last_price, last_size, 'EXCHANGE')


if __name__ == '__main__':
    hs = HigherScale()
    hs.generate_output()
