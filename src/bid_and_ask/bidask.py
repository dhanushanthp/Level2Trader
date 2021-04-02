import itertools
from terminaltables import AsciiTable
from colorclass import Color
import numpy as np
from colr import color
from src.util import price_util
from config import Config


class BidAsk:
    def __init__(self, ticker, multiple_of_10sec=6, length=6):
        self.bid_time_accumulator = dict()
        self.ask_time_accumulator = dict()
        self.last_x_min = multiple_of_10sec
        self.ticker = ticker
        self.length = length
        # white,white, yellow,yellow,green
        self.colors_bid = [(255, 255, 255), (255, 255, 255), (255, 255, 0), (255, 255, 0), (0, 255, 0)]
        # white,white, yellow,yellow,red
        self.colors_ask = [(255, 255, 255), (255, 255, 255), (255, 255, 0), (255, 255, 0), (255, 0, 0)]
        self.pu = price_util.PriceUtil()
        self.config = Config()

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

    def add_space_ask(self, string: str):
        string = str(string)
        string_length = len(string)
        change = self.length - string_length
        if change > 0:
            return string.ljust(self.length)
        else:
            return string

    def add_space_bid(self, string: str):
        string = str(string)
        string_length = len(string)
        change = self.length - string_length
        if change > 0:
            return string.rjust(self.length)
        else:
            return string

    def data_generator(self, var_time: str, bid_price: float, bid_size: int, ask_price: float, ask_size: int):
        # Adjust for 10 sec
        var_time = var_time[:-1]
        bid_price = round(bid_price, 2)
        ask_price = round(ask_price, 2)

        """
        time accumulator dictionary is a dictionary of dictionary data structure. 
        Dictionary: Key: Time, value: Dictionary(key: price, value: size)
        The value will be updated through the iteration process by finding time and price accordingly
        """
        # Generate bid dictionary
        if var_time in self.bid_time_accumulator:
            if bid_price in self.bid_time_accumulator[var_time]:
                # Get the value dictionary and update the size
                self.bid_time_accumulator[var_time][bid_price] = self.bid_time_accumulator[var_time][bid_price] + bid_size
            else:
                self.bid_time_accumulator[var_time][bid_price] = bid_size
        else:
            # Create value dictionary with size
            value_dict = dict()
            value_dict[bid_price] = bid_size
            # Create time dictionary with value
            self.bid_time_accumulator[var_time] = value_dict

        # Generate ask dictionary
        if var_time in self.ask_time_accumulator:
            if ask_price in self.ask_time_accumulator[var_time]:
                # Get the value dictionary and update the size
                self.ask_time_accumulator[var_time][ask_price] = self.ask_time_accumulator[var_time][ask_price] + ask_size
            else:
                self.ask_time_accumulator[var_time][ask_price] = ask_size
        else:
            # Create value dictionary with size
            value_dict = dict()
            value_dict[ask_price] = ask_size
            # Create time dictionary with value
            self.ask_time_accumulator[var_time] = value_dict

        # Call function to generate table
        print(chr(27) + "[2J")
        print(self.data_table_generator(bid_price, ask_price) + '\n')

    def data_table_generator(self, bid_price: float, ask_price: float):
        """
        Visualize the table
        :return: table data
        """
        # Time
        lst_time = sorted(self.bid_time_accumulator.keys())[-self.last_x_min:]
        # value
        bid_lst_price = sorted(list((set(itertools.chain.from_iterable([list(self.bid_time_accumulator[i].keys()) for i in lst_time])))))
        ask_lst_price = sorted(list((set(itertools.chain.from_iterable([list(self.ask_time_accumulator[i].keys()) for i in lst_time])))))

        # Pick the sizes which are visible in the time frame
        bid_sizes = sorted(set(itertools.chain.from_iterable([self.bid_time_accumulator[i].values() for i in lst_time])))
        # Pick the sizes which are visible in the time frame
        ask_sizes = sorted(set(itertools.chain.from_iterable([self.ask_time_accumulator[i].values() for i in lst_time])))

        # Creation of color dictionary
        bid_colour_dictionary = self.get_colour_by_bid(bid_sizes)
        ask_colour_dictionary = self.get_colour_by_ask(ask_sizes)

        lst_price = sorted(list(set(bid_lst_price + ask_lst_price)), reverse=True)
        # Balance the price range
        bid_index = None
        ask_index = None
        try:
            bid_index = lst_price.index(bid_price)
            ask_index = lst_price.index(ask_price)
            min_range = 0 if bid_index - self.config.get_bidask_price_range() < 0 else bid_index - self.config.get_bidask_price_range()
            max_range = ask_index + self.config.get_bidask_price_range()
            lst_price = lst_price[min_range:max_range]
        except ValueError:
            print(bid_price)
            print(ask_price)
            print(lst_price)

        """
        Create terminal table for visual
        """
        table_data = []
        for ele_time in lst_time:
            value_data = []
            for ele_price in lst_price:
                # PriceUtil from both bid and ask
                if ele_price in self.bid_time_accumulator[ele_time] and ele_price in self.ask_time_accumulator[ele_time]:
                    bid_size = self.bid_time_accumulator[ele_time][ele_price]
                    ask_size = self.ask_time_accumulator[ele_time][ele_price]
                    value_data.append(
                        color(self.add_space_bid(self.pu.slot_convertor(bid_size)),
                              fore=bid_colour_dictionary[bid_size], back=(0, 0, 0)) +
                        ' ➜ ' +
                        color(self.add_space_ask(self.pu.slot_convertor(ask_size)),
                              fore=ask_colour_dictionary[ask_size], back=(0, 0, 0)))

                # PriceUtil exist in BID but Not in ASK
                elif ele_price in self.bid_time_accumulator[ele_time] and ele_price not in self.ask_time_accumulator[ele_time]:
                    # Add the volume size

                    bid_size = self.bid_time_accumulator[ele_time][ele_price]
                    value_data.append(
                        color(self.add_space_bid(self.pu.slot_convertor(bid_size)),
                              fore=bid_colour_dictionary[bid_size], back=(0, 0, 0)) +
                        f' ➜ {self.add_space_ask("0")}')

                # PriceUtil exist in ASK but Not in BID
                elif ele_price not in self.bid_time_accumulator[ele_time] and \
                        ele_price in self.ask_time_accumulator[ele_time]:
                    # Add the volume size
                    ask_size = self.ask_time_accumulator[ele_time][ele_price]
                    value_data.append(f'{self.add_space_bid("0")} ➜ ' +
                                      color(self.add_space_ask(self.pu.slot_convertor(ask_size)),
                                            fore=ask_colour_dictionary[ask_size],
                                            back=(0, 0, 0)))
                else:
                    value_data.append('')
            table_data.append(value_data)

        # Add current price pointer
        lst_price = ['{:0.2f}'.format(i) for i in lst_price]
        # '\033[1m'  add the boldness the text
        try:
            lst_price[bid_index] = Color('{autogreen}' + '\033[1m' + str(bid_price) + '{/autogreen}')
            lst_price[ask_index] = Color('{autored}' + '\033[1m' + str(ask_price) + '{/autored}')
        except IndexError:
            print(bid_index, bid_price, ask_index, ask_price)
            pass

        table_data.append(lst_price)
        table_data = list(map(list, zip(*table_data)))
        table_data.insert(0, lst_time + [''])

        # Create table instance
        table_instance = AsciiTable(table_data, f'****  {self.ticker}  ****')
        # table_instance = SingleTable(table_data, f'****  {self.ticker}  ****')
        table_instance.inner_heading_row_border = False
        table_instance.inner_row_border = True
        table_instance.inner_column_border = False
        table_instance.justify_columns = {0: 'center', 1: 'center', 2: 'center'}
        return table_instance.table
