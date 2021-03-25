import itertools
from terminaltables import AsciiTable
from colorclass import Color
import numpy as np
from colr import color


class TimeSalesBidAsk:
    def __init__(self, ticker, multiple_of_10sec=6):
        self.time_accumulator_on_bid = dict()
        self.time_accumulator_on_ask = dict()
        self.time_accumulator_on_mid = dict()
        self.last_x_min = multiple_of_10sec
        self.ticker = ticker
        # white, yellow,blue,green,red
        self.colors = [(255, 255, 255), (255, 255, 0), (0, 255, 255), (0, 255, 0), (255, 0, 0)]
        # white,white, yellow,yellow,green
        self.colors_bid = [(255, 255, 255), (255, 255, 255), (255, 255, 0), (255, 255, 0), (0, 255, 0)]
        # white,white, yellow,yellow,red
        self.colors_ask = [(255, 255, 255), (255, 255, 255), (255, 255, 0), (255, 255, 0), (255, 0, 0)]

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

    def get_colour_by_range(self, sizes: list) -> dict:
        colour_mapping = dict()
        values = np.array_split(np.array(sizes), 5)
        for i, val_lst in enumerate(values):
            for size in val_lst:
                colour_mapping[size] = self.colors[i]
        return colour_mapping

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

        if closest_price is bid_price:
            # price on bid
            if time in self.time_accumulator_on_bid:
                # If time already exist in dictionary
                if closest_price in self.time_accumulator_on_bid[time]:
                    # Get the value dictionary by time and price and update the size
                    self.time_accumulator_on_bid[time][closest_price] = self.time_accumulator_on_bid[time][
                                                                            closest_price] + last_size
                else:
                    # Time exist but the price is not exist, create a element with price and size
                    self.time_accumulator_on_bid[time][closest_price] = last_size

            else:
                # New element creation with time, price and size
                # Create value dictionary with size
                value_dict = dict()
                value_dict[closest_price] = last_size
                # Create time dictionary with value
                self.time_accumulator_on_bid[time] = value_dict
        elif closest_price is ask_price:
            # price on ask
            if time in self.time_accumulator_on_ask:
                # If time already exist in dictionary
                if closest_price in self.time_accumulator_on_ask[time]:
                    # Get the value dictionary by time and price and update the size
                    self.time_accumulator_on_ask[time][closest_price] = self.time_accumulator_on_ask[time][
                                                                            closest_price] + last_size
                else:
                    # Time exist but the price is not exist, create a element with price and size
                    self.time_accumulator_on_ask[time][closest_price] = last_size

            else:
                # New element creation with time, price and size
                # Create value dictionary with size
                value_dict = dict()
                value_dict[closest_price] = last_size
                # Create time dictionary with value
                self.time_accumulator_on_ask[time] = value_dict
        else:
            # price in middle
            if time in self.time_accumulator_on_mid:
                # If time already exist in dictionary
                if closest_price in self.time_accumulator_on_mid[time]:
                    # Get the value dictionary by time and price and update the size
                    self.time_accumulator_on_mid[time][closest_price] = self.time_accumulator_on_mid[time][
                                                                            closest_price] + last_size
                else:
                    # Time exist but the price is not exist, create a element with price and size
                    self.time_accumulator_on_mid[time][closest_price] = last_size

            else:
                # New element creation with time, price and size
                # Create value dictionary with size
                value_dict = dict()
                value_dict[closest_price] = last_size
                # Create time dictionary with value
                self.time_accumulator_on_mid[time] = value_dict

        # Call function to generate table
        # print(chr(27) + "[2J")
        # print(self.time_accumulator_on_bid)
        print(self.data_table_generator(closest_price, bid_price, ask_price) + '\n')

    def data_table_generator(self, current_price: float, bid_price: float, ask_price: float):
        """
        Visualize the table
        :return: table data
        """

        """
        
        
        BID Price
        
        
        """
        # Time, select the range of few minutes of data
        bid_lst_time = sorted(self.time_accumulator_on_bid.keys())[-self.last_x_min:]

        # reversed price. Low to High
        bid_lst_price = sorted(
            list(
                (set(itertools.chain.from_iterable(
                    [list(self.time_accumulator_on_bid[i].keys()) for i in bid_lst_time])))),
            reverse=True)

        # Pick the sizes which are visible in the time frame
        bid_sizes = sorted(
            set(itertools.chain.from_iterable([self.time_accumulator_on_bid[i].values() for i in bid_lst_time])))

        # get the colour for each order size
        bid_colour_dictionary = self.get_colour_by_bid(bid_sizes)

        """
        
        
        ASK Price
        
        
        """
        # Time, select the range of few minutes of data
        ask_lst_time = sorted(self.time_accumulator_on_ask.keys())[-self.last_x_min:]

        # reversed price. Low to High
        ask_lst_price = sorted(
            list(
                (set(itertools.chain.from_iterable(
                    [list(self.time_accumulator_on_ask[i].keys()) for i in ask_lst_time])))),
            reverse=True)

        # Pick the sizes which are visible in the time frame
        # print(self.time_accumulator_on_ask)
        ask_sizes = sorted(
            set(itertools.chain.from_iterable([self.time_accumulator_on_ask[i].values() for i in ask_lst_time])))

        # get the colour for each order size
        ask_colour_dictionary = self.get_colour_by_ask(ask_sizes)

        # Combine the time range
        common_time = sorted(set(bid_lst_time + ask_lst_time))

        # Price histogram generation
        bid_price_size = [self.time_accumulator_on_bid[i] for i in bid_lst_time]
        ask_price_size = [self.time_accumulator_on_ask[i] for i in ask_lst_time]

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
        # price_index = lst_price.index(current_price)
        # min_range = 0 if price_index - 20 < 0 else price_index - 20
        # max_range = price_index + 20
        # lst_price = lst_price[min_range:max_range]

        # New filtered price by range
        bid_price_hist_agg = [round(bid_price_size_agg[i] / 1000) * '*' for i in bid_lst_price]
        ask_price_hist_agg = [round(ask_price_size_agg[i] / 1000) * '*' for i in ask_lst_price]

        table_data = []
        for ele_time in bid_lst_time:
            value_data = []
            for ele_price in bid_lst_price:
                if ele_price in self.time_accumulator_on_bid[ele_time]:
                    # Add the volume size
                    # value_data.append(self.color_size(self.time_accumulator_on_bid[ele_time][ele_price]))
                    size = self.time_accumulator_on_bid[ele_time][ele_price]
                    value_data.append(color(size, fore=bid_colour_dictionary[size], back=(0, 0, 0)))
                else:
                    value_data.append('')
            table_data.append(value_data)

        # Add current price pointer
        # try:
        #     lst_price[price_index] = Color('{autored}' + '\033[1m' + str(current_price) + '{/autored}')
        # except IndexError:
        #     print(price_index, current_price)
        #     pass

        # Add price and time accordingly as header and index
        table_data.append(bid_lst_price)
        table_data.append(bid_price_hist_agg)
        table_data = list(map(list, zip(*table_data)))
        table_data.insert(0, bid_lst_time + [''])

        # Create table instance
        table_instance = AsciiTable(table_data, f'****  {self.ticker}  ****')
        # table_instance = SingleTable(table_data, f'****  {self.ticker}  ****')
        table_instance.inner_heading_row_border = False
        table_instance.inner_row_border = True
        table_instance.inner_column_border = False
        table_instance.justify_columns = {0: 'center', 1: 'center', 2: 'center'}
        return table_instance.table
