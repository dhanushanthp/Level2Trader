import itertools
from terminaltables import AsciiTable
from colorclass import Color
import numpy as np
from colr import color
from util import price_util
from config import Config


class TimeSalesBidAsk:
    def __init__(self, ticker, multiple_of_10sec=6):
        self.dict_last_size_on_bid = dict()
        self.dict_last_size_on_ask = dict()
        self.dict_bid_size_on_bid = dict()
        self.dict_ask_size_on_ask = dict()
        self.time_accumulator_on_mid = dict()
        self.last_x_min = multiple_of_10sec
        self.ticker = ticker
        # white,white, yellow,yellow,green
        self.colors_bid = [(255, 255, 255), (255, 255, 255), (255, 255, 0), (255, 255, 0), (0, 255, 0)]
        # white,white, yellow,yellow,red
        self.colors_ask = [(255, 255, 255), (255, 255, 255), (255, 255, 0), (255, 255, 0), (255, 0, 0)]
        self.pu = price_util.PriceUtil()
        self.config = Config()

    @staticmethod
    def find_closest(bid, ask, last):
        """
        Find the cloesst value to the bid and ask compare to last value
        :param bid:
        :param ask:
        :param last:
        :return:
        """
        return min([bid, ask], key=lambda x: abs(x - last))

    def get_colour_by_bid(self, sizes: list) -> dict:
        colour_mapping = dict()
        values = np.array_split(np.array(sizes), len(self.colors_bid))
        for i, val_lst in enumerate(values):
            for size in val_lst:
                colour_mapping[size] = self.colors_bid[i]
        return colour_mapping

    def get_colour_by_ask(self, sizes: list) -> dict:
        colour_mapping = dict()
        values = np.array_split(np.array(sizes), len(self.colors_ask))
        for i, val_lst in enumerate(values):
            for size in val_lst:
                colour_mapping[size] = self.colors_ask[i]
        return colour_mapping

    def data_generator(self, time, bid_price, bid_size, ask_price, ask_size, last_price, last_size):

        # Adjust for 10 sec
        time = time[:-1]
        # Find the closest price w.r.t to last price
        closest_price = self.find_closest(bid_price, ask_price, last_price)

        """
        time accumulator dictionary is a dictionary of dictionary data structure. 
        Dictionary: Key: Time, value: Dictionary(key: price, value: size)
        The value will be updated through the iteration process by finding time and price accordingly
        """

        """
        Create dummy entry for time and prices to maintains the keys across bid and ask dictionary
        """
        # Last size w.r.t BID price
        if time in self.dict_last_size_on_bid:
            # If time already exist in dictionary
            if closest_price in self.dict_last_size_on_bid[time]:
                if closest_price == bid_price:
                    # Get the value dictionary by time and price and update the size
                    self.dict_last_size_on_bid[time][closest_price] = self.dict_last_size_on_bid[time][closest_price] + last_size
                else:
                    # Get the value dictionary by time and price and update the size
                    self.dict_last_size_on_bid[time][closest_price] = self.dict_last_size_on_bid[time][closest_price] + 0
            else:
                if closest_price == bid_price:
                    # Time exist but the price is not exist, create a element with price and size
                    self.dict_last_size_on_bid[time][closest_price] = last_size
                else:
                    # Time exist but the price is not exist, create a element with price and size
                    self.dict_last_size_on_bid[time][closest_price] = 0
        else:
            # New element creation with time, price and size
            # Create value dictionary with size
            value_dict = dict()
            if closest_price == bid_price:
                value_dict[closest_price] = last_size
            else:
                value_dict[closest_price] = 0

            # Create time dictionary with value
            self.dict_last_size_on_bid[time] = value_dict

        # BID size w.r.t BID price
        if time in self.dict_bid_size_on_bid:
            # If time already exist in dictionary
            if closest_price in self.dict_bid_size_on_bid[time]:
                if closest_price == bid_price:
                    # Get the value dictionary by time and price and update the size
                    self.dict_bid_size_on_bid[time][closest_price] = self.dict_bid_size_on_bid[time][closest_price] + bid_size
                else:
                    # Get the value dictionary by time and price and update the size
                    self.dict_bid_size_on_bid[time][closest_price] = self.dict_bid_size_on_bid[time][closest_price] + 0
            else:
                if closest_price == bid_price:
                    # Time exist but the price is not exist, create a element with price and size
                    self.dict_bid_size_on_bid[time][closest_price] = bid_size
                else:
                    # Time exist but the price is not exist, create a element with price and size
                    self.dict_bid_size_on_bid[time][closest_price] = 0
        else:
            # New element creation with time, price and size
            # Create value dictionary with size
            value_dict = dict()
            if closest_price == bid_price:
                value_dict[closest_price] = bid_size
            else:
                value_dict[closest_price] = 0

            # Create time dictionary with value
            self.dict_bid_size_on_bid[time] = value_dict

        # Last size w.r.t ASK
        if time in self.dict_last_size_on_ask:
            # If time already exist in dictionary
            if closest_price in self.dict_last_size_on_ask[time]:
                if closest_price == ask_price:
                    # Get the value dictionary by time and price and update the size
                    self.dict_last_size_on_ask[time][closest_price] = self.dict_last_size_on_ask[time][
                                                                     closest_price] + last_size
                else:
                    # Get the value dictionary by time and price and update the size
                    self.dict_last_size_on_ask[time][closest_price] = self.dict_last_size_on_ask[time][
                                                                     closest_price] + 0
            else:
                if closest_price == ask_price:
                    # Time exist but the price is not exist, create a element with price and size
                    self.dict_last_size_on_ask[time][closest_price] = last_size
                else:
                    # Time exist but the price is not exist, create a element with price and size
                    self.dict_last_size_on_ask[time][closest_price] = 0
        else:
            # New element creation with time, price and size
            # Create value dictionary with size
            value_dict = dict()
            if closest_price == ask_price:
                value_dict[closest_price] = last_size
            else:
                value_dict[closest_price] = 0

            # Create time dictionary with value
            self.dict_last_size_on_ask[time] = value_dict

        # ASK size w.r.t ASK
        if time in self.dict_ask_size_on_ask:
            # If time already exist in dictionary
            if closest_price in self.dict_ask_size_on_ask[time]:
                if closest_price == ask_price:
                    # Get the value dictionary by time and price and update the size
                    self.dict_ask_size_on_ask[time][closest_price] = self.dict_ask_size_on_ask[time][
                                                                     closest_price] + last_size
                else:
                    # Get the value dictionary by time and price and update the size
                    self.dict_ask_size_on_ask[time][closest_price] = self.dict_ask_size_on_ask[time][
                                                                     closest_price] + 0
            else:
                if closest_price == ask_price:
                    # Time exist but the price is not exist, create a element with price and size
                    self.dict_ask_size_on_ask[time][closest_price] = last_size
                else:
                    # Time exist but the price is not exist, create a element with price and size
                    self.dict_ask_size_on_ask[time][closest_price] = 0
        else:
            # New element creation with time, price and size
            # Create value dictionary with size
            value_dict = dict()
            if closest_price == ask_price:
                value_dict[closest_price] = last_size
            else:
                value_dict[closest_price] = 0

            # Create time dictionary with value
            self.dict_ask_size_on_ask[time] = value_dict

        # Call function to generate table
        # print(chr(27) + "[2J")
        print(self.data_table_generator(closest_price, bid_price, ask_price) + '\n')

    def data_table_generator(self, current_price: float, bid_price: float, ask_price: float):
        """
        Visualize the table
        :return: table data
        """

        """
        BID PriceUtil
        """
        # Time, select the range of few minutes of data
        bid_lst_time = sorted(self.dict_last_size_on_bid.keys())[-self.last_x_min:]

        # reversed price. Low to High
        bid_lst_price = sorted(
            list(
                (set(itertools.chain.from_iterable(
                    [list(self.dict_last_size_on_bid[i].keys()) for i in bid_lst_time])))),
            reverse=True)

        # Pick the sizes which are visible in the time frame
        bid_sizes = sorted(
            set(itertools.chain.from_iterable([self.dict_last_size_on_bid[i].values() for i in bid_lst_time])))

        # get the colour for each order size
        bid_colour_dictionary = self.get_colour_by_bid(bid_sizes)

        """        
        ASK PriceUtil
        """
        # Time, select the range of few minutes of data
        ask_lst_time = sorted(self.dict_last_size_on_ask.keys())[-self.last_x_min:]

        # reversed price. Low to High
        ask_lst_price = sorted(
            list(
                (set(itertools.chain.from_iterable(
                    [list(self.dict_last_size_on_ask[i].keys()) for i in ask_lst_time])))),
            reverse=True)

        # Pick the sizes which are visible in the time frame
        # print(self.dict_last_size_on_ask)
        ask_sizes = sorted(
            set(itertools.chain.from_iterable([self.dict_last_size_on_ask[i].values() for i in ask_lst_time])))

        # get the colour for each order size
        ask_colour_dictionary = self.get_colour_by_ask(ask_sizes)

        # PriceUtil histogram generation
        bid_price_size = [self.dict_last_size_on_bid[i] for i in bid_lst_time]
        ask_price_size = [self.dict_last_size_on_ask[i] for i in ask_lst_time]

        bid_price_size_agg = dict()
        for ps in bid_price_size:
            for p in ps.keys():
                if p in bid_price_size_agg:
                    bid_price_size_agg[p] = bid_price_size_agg[p] + ps[p]
                else:
                    bid_price_size_agg[p] = ps[p]

        ask_price_size_agg = dict()
        for ps in ask_price_size:
            for p in ps.keys():
                if p in ask_price_size_agg:
                    ask_price_size_agg[p] = ask_price_size_agg[p] + ps[p]
                else:
                    ask_price_size_agg[p] = ps[p]

        # Balance the price range
        bid_index = None
        ask_index = None
        current_index = None
        lst_price = bid_lst_price

        try:
            bid_index = bid_lst_price.index(bid_price)
            ask_index = ask_lst_price.index(ask_price)
            current_index = bid_lst_price.index(current_price)
            # Add the range of moment for the table
            min_range = 0 if bid_index - self.config.get_timesales_price_range() < 0 else bid_index - self.config.get_timesales_price_range()
            max_range = ask_index + self.config.get_timesales_price_range()
            lst_price = lst_price[min_range:max_range]
        except ValueError as e:
            """
            It's perfectly fine pass this exception. Because we may have cases like below
            1. Currenly we read only the last price after the completion. Therefore we may not able to find,
                1. Ask price on current price list. which may not be executed so far
                2. Bid price on current price list. which may not be executed so far
            
            So we don't need to track if thouse prices are out of rance
            """
            pass

        # New filtered price by range
        bid_price_hist_agg = [round(bid_price_size_agg[i] / self.config.get_hist_blk_size()) * '+' for i in lst_price]
        ask_price_hist_agg = [round(ask_price_size_agg[i] / self.config.get_hist_blk_size()) * '|' for i in lst_price]

        """
        Used the bid time and price. Since both will be consistent in bid and ask dictionaries. Handled in dictionary
        generation
        """
        table_data = []
        for ele_time in bid_lst_time:
            value_data = []
            for ele_price in lst_price:
                # PriceUtil from both bid and ask
                if ele_price in self.dict_last_size_on_bid[ele_time] and \
                        ele_price in self.dict_last_size_on_ask[ele_time]:
                    bid_size = self.dict_last_size_on_bid[ele_time][ele_price]
                    ask_size = self.dict_last_size_on_ask[ele_time][ele_price]
                    value_data.append(
                        color(self.pu.slot_convertor(bid_size), fore=bid_colour_dictionary[bid_size], back=(0, 0, 0)) +
                        ' ➜ ' +
                        color(self.pu.slot_convertor(ask_size), fore=ask_colour_dictionary[ask_size], back=(0, 0, 0)))

                # PriceUtil exist in BID but Not in ASK
                elif ele_price in self.dict_last_size_on_bid[ele_time] and \
                        ele_price not in self.dict_last_size_on_ask[ele_time]:
                    # Add the volume size

                    bid_size = self.dict_last_size_on_bid[ele_time][ele_price]
                    value_data.append(
                        color(self.pu.slot_convertor(bid_size), fore=bid_colour_dictionary[bid_size], back=(0, 0, 0)) +
                        f' ➜ {"0"}')

                    # value_data.append(self.color_size(self.bid_time_accumulator[ele_time][ele_price], 0))
                # PriceUtil exist in ASK but Not in BID
                elif ele_price not in self.dict_last_size_on_bid[ele_time] and \
                        ele_price in self.dict_last_size_on_ask[ele_time]:
                    # Add the volume size
                    ask_size = self.dict_last_size_on_ask[ele_time][ele_price]
                    value_data.append(f'{"0"} ➜ ' +
                                      color(self.pu.slot_convertor(ask_size), fore=ask_colour_dictionary[ask_size],
                                            back=(0, 0, 0)))
                    # value_data.append(self.color_size(0, self.ask_time_accumulator[ele_time][ele_price]))
                else:
                    value_data.append('')

            table_data.append(value_data)

        # Add current price pointer
        lst_price = ['{:0.2f}'.format(i) for i in lst_price]

        # Only show the indicators if they are in valid range
        # '\033[1m'  add the boldness the text
        if bid_index:
            try:
                lst_price[bid_index] = Color('{autogreen}' + '\033[1m' + str(bid_price) + '{/autogreen}')
            except IndexError:
                pass
        if ask_index:
            try:
                lst_price[ask_index] = Color('{autored}' + '\033[1m' + str(ask_price) + '{/autored}')
            except IndexError:
                pass
        if current_index:
            try:
                lst_price[current_index] = Color('{autoyellow}' + '\033[1m' + str(ask_price) + '{/autoyellow}')
            except IndexError:
                pass

        # Add price and time accordingly as header and index
        table_data.append(lst_price)
        table_data.append(bid_price_hist_agg)
        table_data.append(ask_price_hist_agg)
        table_data = list(map(list, zip(*table_data)))
        table_data.insert(0, bid_lst_time + ['price', 'bid', 'ask'])

        # Create table instance
        table_instance = AsciiTable(table_data, f'****  {self.ticker}  ****')
        # table_instance = SingleTable(table_data, f'****  {self.ticker}  ****')
        table_instance.inner_heading_row_border = False
        table_instance.inner_row_border = True
        table_instance.inner_column_border = False
        table_instance.justify_columns = {0: 'center', 1: 'center', 2: 'center'}
        return table_instance.table
