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

    def get_price_range_enabler(self):
        return self.config.getboolean('TIME_SALES', 'enable_price_range')

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

    def get_top_sales_mon_period(self):
        """
        Define the period for top sales monitoring
        :return:
        """
        return self.config.getint('TIME_SALES', 'top_sale_mon_period')

    def get_time_frequency(self):
        """
        define the frequency of time in seconds
        :return:
        """
        return self.config.getint('TIME_SALES', 'time_frequency')

    def get_refresh_rate(self):
        """
        Get the terminal refresh rate
        :return:
        """
        return self.config.getint('TERMINAL', 'refresh_rate')

    def get_can_write_data(self):
        """
        Enable write the data to file
        :return:
        """
        return self.config.getboolean('DATA', 'write_data')

    def get_port_number(self):
        """
        Get the port number from TWS service
        :return:
        """
        return self.config.getint('SYSTEM', 'port_number')

    def get_time_sales_source_name(self):
        return 'T&S'

    def get_bid_ask_source_name(self):
        return 'B&A'
