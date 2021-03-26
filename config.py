import configparser


class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('Config.ini')

    def get_bidask_timerange(self):
        self.config.get('BIDASK', 'timerange')

    def get_bidask_price_range(self):
        """
        The range of price moment from the current ask and bid price
        :return:
        """
        return self.config.getint('BID_ASK', 'price_range')

    def get_timesales_price_range(self):
        return self.config.getint('TIME_SALES', 'price_range')

    def get_slot_size(self):
        """
        Stock size representation in the table. Where each size will be divided by block size for normalization
        :return:
        """
        return self.config.getint('PRICE', 'slot_size')

    def get_hist_blk_size(self):
        """
        Representation of each bar in histogram. This blk size will devide the totol size to count the number of bars
        :return:
        """
        return self.config.getint('PRICE', 'hist_blk_size')

    def get_timesales_timeticks(self):
        """
        Limit the time ticks the last x period
        :return:
        """
        return self.config.getint('TIME_SALES', 'max_time_ticks')
