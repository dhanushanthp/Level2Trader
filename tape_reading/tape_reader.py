import itertools
from terminaltables import AsciiTable
from colorclass import Color
import numpy as np
from colr import color
from util import price_util
from config import Config
import os


class TapeReader:
    def __init__(self, ticker):
        """
        We don't track the actual price of last price here. rather we find the most close bid and ask price for the last price.
        The goal is to find the price on bid and price on ask for bullish and bearish signals.
        :param ticker:
        """
        # Price and size w.r.t BID and last, Bearish signal
        self.dict_last_size_on_bid = dict()
        # Price and size w.r.t ASK and last, Bullish signal
        self.dict_last_size_on_ask = dict()
        # Price and size w.r.t BID only, Higher Bids Holding, Bullish signal
        self.dict_bid_size_on_bid = dict()
        # Price and size w.r.t ASK only, Higher Asks Holding, Bearish signal
        self.dict_ask_size_on_ask = dict()
        # Counter of concurrent bid calls
        self.concurrent_bids = 0
        # Counter of concurrent bid calls
        self.concurrent_asks = 0
        # Clear Terminal
        self.clear = lambda: os.system('clear')
        self.counter = 0

        # Dynamic Histogram block size, Default 100, Find the max transaction size and update accordingly
        self.histogram_block_size = 100

        # Most high price on ask, Bullish
        self.top_sales_on_ask = None
        # Most hit price on bids, Bearish
        self.top_sales_on_bid = None

        # Ticker by each second, So the size aggregation will be done by seconds
        self.ticker = ticker
        # green,green,yellow,yellow,white,white,
        self.colors_bullish = [(0, 255, 0), (0, 255, 0), (255, 255, 0), (255, 255, 0), (255, 255, 255), (255, 255, 255)]
        # red,red,yellow,yellow,white,white,
        self.colors_bearish = [(255, 0, 0), (255, 0, 0), (255, 255, 0), (255, 255, 0), (255, 255, 255), (255, 255, 255)]

        self.pu = price_util.PriceUtil()
        self.config = Config()
        self.time_ticks_filter = self.config.get_timesales_timeticks()

    @staticmethod
    def find_closest(bid: float, ask: float, last: float) -> float:
        """
        Find the closest value to the bid and ask compare to last value
        :param bid: bid price, level II first tier only
        :param ask: ask price, level II first tier only
        :param last: last price, Time & Sales
        :return: Closest possible to bid or ask
        """
        return min([bid, ask], key=lambda x: abs(x - last))

    def get_colour_by_bullish(self, sizes: list) -> dict:
        """
        Generate color shades w.r.t range of size
        :param sizes: listed trade size w.r.t bid price on time ans sales
        :return: dictionary of colors [key: size, value: color]
        """
        colour_mapping = dict()
        sizes = sorted(sizes, reverse=True)
        values = np.array_split(np.array(sizes), len(self.colors_bullish))
        for i, val_lst in enumerate(values):
            for size in val_lst:
                colour_mapping[size] = self.colors_bullish[i]
        # Create colour for size 0
        colour_mapping[0] = self.colors_bullish[5]

        return colour_mapping

    def get_colour_by_bearish(self, sizes: list) -> dict:
        """
        Generate color shades w.r.t range of size
        :param sizes: listed tratde size w.r.t ask price on time ans sales
        :return: dictionary of colors [key: size, value: color]
        """
        colour_mapping = dict()
        sizes = sorted(sizes, reverse=True)
        values = np.array_split(np.array(sizes), len(self.colors_bearish))
        for i, val_lst in enumerate(values):
            for size in val_lst:
                colour_mapping[size] = self.colors_bearish[i]
        # Create colour for size 0
        colour_mapping[0] = self.colors_bearish[5]
        return colour_mapping

    def data_generator(self, tick_time: str, bid_price, bid_size, ask_price, ask_size, last_price, last_size):
        """
        1. Aggregate the size of trades w.r.t to bid price, ask price and last price.
        2. Tag last price w.r.t bid and ask values by finding most possible or closest prices
        :param tick_time: Time of ticker
        :param bid_price: bid price, level II first tier only
        :param bid_size: bid size, level II first tier only
        :param ask_price: ask price, level II first tier only
        :param ask_size: ask size, level II first tier only
        :param last_price: last price, time & sales
        :param last_size: last size, time & sales
        :return:
        """

        # Adjust for 10 sec
        tick_time = tick_time
        # Find the closest price w.r.t to last price on bid or ask
        closest_price = self.find_closest(bid_price, ask_price, last_price)

        # Find the biggest transaction size for histogram block size and update, Not exceed 10k sales
        if (last_size > self.histogram_block_size) and (self.histogram_block_size < 10000):
            self.histogram_block_size = last_size

        """
        Time accumulator dictionary is a dictionary of, dictionary data structure. 
        Dictionary: {Key: Time, value: Dictionary(key: price, value: size)}
        The size will be updated and aggregated through the iteration process by finding time and price accordingly
        """

        """
        Last size w.r.t BID price
        Find the closest price for last price. If the closest price match to bid price. Then the transaction considered as "Trade on BID", 
        Bearish Signal
        """
        if tick_time in self.dict_last_size_on_bid:
            # If time already exist in dictionary
            if closest_price in self.dict_last_size_on_bid[tick_time]:
                if closest_price == bid_price:
                    '''
                    Get the value from the dictionary by time and price and update the size. If the price don't match to bid price. Then it will be 
                    caught in ask price
                    '''
                    self.dict_last_size_on_bid[tick_time][closest_price] = self.dict_last_size_on_bid[tick_time][closest_price] + last_size
            else:
                if closest_price == bid_price:
                    # Time exist but the price is not exist, create a element with price and size
                    self.dict_last_size_on_bid[tick_time][closest_price] = last_size
        else:
            # New element creation with time, price and size
            # Create value dictionary with size
            value_dict = dict()
            if closest_price == bid_price:
                value_dict[closest_price] = last_size

            # Create time dictionary with value
            self.dict_last_size_on_bid[tick_time] = value_dict

        """
        BID size w.r.t BID price
        Collect bid price regardless of last price.
        """
        if tick_time in self.dict_bid_size_on_bid:
            # If time already exist in dictionary
            # Regardless of last price. We will add the bid price.
            # Time exist but the price is not exist, create a element with price and size
            self.dict_bid_size_on_bid[tick_time][bid_price] = bid_size
        else:
            # New element creation with time, price and size
            # Create value dictionary with size
            value_dict = dict()
            value_dict[bid_price] = bid_size

            # Create time dictionary with value
            self.dict_bid_size_on_bid[tick_time] = value_dict

        """
        Last size w.r.t ASK price
        Find the closest price for last price. If the closes price match to ask price. Then the transaction considered as "Trade on ASK",
        Bullish Signal
        """
        if tick_time in self.dict_last_size_on_ask:
            # If time already exist in dictionary
            if closest_price in self.dict_last_size_on_ask[tick_time]:
                if closest_price == ask_price:
                    # Get the value dictionary by time and price and update the size
                    self.dict_last_size_on_ask[tick_time][closest_price] = self.dict_last_size_on_ask[tick_time][closest_price] + last_size
            else:
                if closest_price == ask_price:
                    # Time exist but the price is not exist, create a element with price and size
                    self.dict_last_size_on_ask[tick_time][closest_price] = last_size
        else:
            # New element creation with time, price and size
            # Create value dictionary with size
            value_dict = dict()
            if closest_price == ask_price:
                value_dict[closest_price] = last_size

            # Create time dictionary with value
            self.dict_last_size_on_ask[tick_time] = value_dict

        """
        ASK size w.r.t ASK
        Collect ask price regardless of last price.
        """
        if tick_time in self.dict_ask_size_on_ask:
            # If time already exist in dictionary
            self.dict_ask_size_on_ask[tick_time][ask_price] = ask_size
        else:
            # New element creation with time, price and size
            # Create value dictionary with size
            value_dict = dict()
            value_dict[ask_price] = ask_size

            # Create time dictionary with value
            self.dict_ask_size_on_ask[tick_time] = value_dict

        """
        Create dummy bid price tag with 0 size
        Only for last price related dictionaries because, the bid and ask price based dictionary will be filled always
        """
        if bid_price not in self.dict_last_size_on_bid[tick_time]:
            self.dict_last_size_on_bid[tick_time][bid_price] = 0

        if ask_price not in self.dict_last_size_on_bid[tick_time]:
            self.dict_last_size_on_bid[tick_time][ask_price] = 0

        if bid_price not in self.dict_last_size_on_ask[tick_time]:
            self.dict_last_size_on_ask[tick_time][bid_price] = 0

        if ask_price not in self.dict_last_size_on_ask[tick_time]:
            self.dict_last_size_on_ask[tick_time][ask_price] = 0

        # Call function to generate table, Refresh rate of terminal
        self.counter = self.counter + 1
        if self.counter == self.config.get_refresh_rate():
            # Clear each 2 min
            self.clear()
            self.counter = 0
            # Reset histogram block size on every terminal clear command
            self.histogram_block_size = 100

        print(self.data_table_generator(closest_price, bid_price, ask_price) + '\n\n\n\n')

    def data_table_generator(self, closest_price: float, bid_price: float, ask_price: float):
        """
        Generate table for terminal outputs
        :param closest_price: The price closest to bid or ask w.r.t last price. Which may not be an actual last price
        :param bid_price: bid price, level II first tier only
        :param ask_price: ask price, level II first tier only
        :return: table for terminal visualisation
        """

        # Limit the moving time, take bid as reference because the time across dictionary will be same. That how the data aggregation has been done
        global_time_limit = sorted(self.dict_last_size_on_bid.keys())[-self.time_ticks_filter:]

        """
        Price and Size w.r.t BID
        """
        # Time, select the range of last few ticks of data
        # reversed price. Low to High
        last_bid_prices = sorted(
            list((set(itertools.chain.from_iterable([list(self.dict_last_size_on_bid[i].keys()) for i in global_time_limit])))), reverse=True)

        # Pick the sizes which are visible in the time frame
        last_bid_sizes = sorted(set(itertools.chain.from_iterable([self.dict_last_size_on_bid[i].values() for i in global_time_limit])))

        # Mean size transaction on bid
        max_last_bid_size = np.mean(last_bid_sizes)

        # get the colour for each order size, Bearish Signal, RED color as main
        last_bid_colour_dictionary = self.get_colour_by_bearish(last_bid_sizes)

        # Pick the sizes which are visible in the time frame
        bid_bid_sizes = sorted(set(itertools.chain.from_iterable([self.dict_bid_size_on_bid[i].values() for i in global_time_limit])))

        # get the colour for each order size, Higher Bids and hold Bullish
        bid_bid_colour_dictionary = self.get_colour_by_bullish(bid_bid_sizes)

        # BID on BID
        # reversed price. Low to High
        bid_bid_lst_price = sorted(
            list((set(itertools.chain.from_iterable([list(self.dict_bid_size_on_bid[i].keys()) for i in global_time_limit])))), reverse=True)

        """        
        Price and Size w.r.t ASK
        """
        # Time, select the range of few minutes of data
        # reversed price. Low to High
        ask_lst_price = sorted(
            list(
                (set(itertools.chain.from_iterable(
                    [list(self.dict_last_size_on_ask[i].keys()) for i in global_time_limit])))),
            reverse=True)

        # Pick the sizes which are visible in the time frame
        # print(self.dict_last_size_on_ask)
        last_ask_sizes = sorted(
            set(itertools.chain.from_iterable([self.dict_last_size_on_ask[i].values() for i in global_time_limit])))

        # Mean size transaction on bid
        max_last_ask_size = np.mean(last_ask_sizes)

        ask_ask_sizes = sorted(
            set(itertools.chain.from_iterable([self.dict_ask_size_on_ask[i].values() for i in global_time_limit])))

        # get the colour for each order size, Price on Ask Bullish
        last_ask_colour_dictionary = self.get_colour_by_bullish(last_ask_sizes)
        # Higher Asks, Bearish
        ask_ask_colour_dictionary = self.get_colour_by_bearish(ask_ask_sizes)

        # ASK on ASK
        # reversed price. Low to High
        ask_ask_lst_price = sorted(
            list((set(itertools.chain.from_iterable([list(self.dict_ask_size_on_ask[i].keys()) for i in global_time_limit])))), reverse=True)

        # Price histogram generation
        bid_price_size = [self.dict_last_size_on_bid[i] for i in global_time_limit]  # Price on Bid, Bearish Signal
        ask_price_size = [self.dict_last_size_on_ask[i] for i in global_time_limit]  # Price on Ask, Bullish Signal

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
        # bid_index = None
        # ask_index = None
        lst_price = sorted(set(last_bid_prices + ask_lst_price + bid_bid_lst_price + ask_ask_lst_price), reverse=True)

        try:
            bid_index = lst_price.index(bid_price)
            ask_index = lst_price.index(ask_price)

            # Add the range of moment for the table
            if self.config.get_price_range_enabler():
                min_range = 0 if bid_index - self.config.get_timesales_price_range() < 0 else bid_index - self.config.get_timesales_price_range()
                max_range = ask_index + self.config.get_timesales_price_range()
                lst_price = lst_price[min_range:max_range]
        except ValueError as e:
            """
            It's perfectly fine pass this exception. Because we may have cases like below
            1. Currently we read only the last price after the completion. Therefore we may not able to find,
                1. Ask price on current price list. which may not be executed so far
                2. Bid price on current price list. which may not be executed so far
                
            So we don't need to track if those prices are out of rance
            """
            raise e
            pass

        # Find the average of sales on mean of bid and ask, Keep the block size consistanct across bid and ask to see the trend
        self.histogram_block_size = round((max_last_bid_size + max_last_ask_size)/2)

        # Price on ask bullish
        ask_price_hist_agg = [round(ask_price_size_agg[i] / self.histogram_block_size) * color('↑', fore=(0, 255, 0), back=(0, 0, 0)) for i in
                              lst_price]
        # Price on bid bearish
        bid_price_hist_agg = [round(bid_price_size_agg[i] / self.histogram_block_size) * color('↓', fore=(255, 0, 0), back=(0, 0, 0)) for i in
                              lst_price]

        """
        Used the bid time and price. Since both will be consistent in bid and ask dictionaries by time. Handled in dictionary
        generation
        """
        table_data = []
        for ele_time in global_time_limit:
            value_data = []
            for ele_price in lst_price:
                # Price both bid and ask
                if ele_price in self.dict_last_size_on_bid[ele_time] and \
                        ele_price in self.dict_last_size_on_ask[ele_time]:

                    # Select sizes for each price and time
                    last_bid_size = self.dict_last_size_on_bid[ele_time][ele_price]
                    last_ask_size = self.dict_last_size_on_ask[ele_time][ele_price]
                    try:
                        bid_bid_size = self.dict_bid_size_on_bid[ele_time][ele_price]
                    except KeyError:
                        bid_bid_size = 0
                    try:
                        ask_ask_size = self.dict_ask_size_on_ask[ele_time][ele_price]
                    except KeyError:
                        ask_ask_size = 0

                    # Define colors so we can change dynamically based on conditions
                    clr_front_last_bid = last_bid_colour_dictionary[last_bid_size]
                    clr_front_bid_bid = bid_bid_colour_dictionary[bid_bid_size]
                    clr_front_last_ask = last_ask_colour_dictionary[last_ask_size]
                    clr_front_ask_ask = ask_ask_colour_dictionary[ask_ask_size]

                    clr_back_bid = (0, 0, 0)
                    clr_back_ask = (0, 0, 0)

                    # Hidden Buyer, Logic: Transaction on BID in T&S is higher than the BID on level II
                    if last_bid_size > bid_bid_size:
                        clr_back_bid = (0, 100, 0)

                    # Hidden Seller, Logic: Transaction on ASK in T&S is higher than the ASK on level II
                    if last_ask_size > ask_ask_size:
                        clr_back_ask = (139, 0, 0)

                    normal_transaction = '[' + \
                                         color(self.pu.slot_convertor(last_bid_size), fore=clr_front_last_bid, back=clr_back_bid) + \
                                         color('/', fore=(255, 255, 255), back=clr_back_bid) + \
                                         color(self.pu.slot_convertor(bid_bid_size), fore=clr_front_bid_bid, back=clr_back_bid) + \
                                         ' ➜ ' + \
                                         color(self.pu.slot_convertor(last_ask_size), fore=clr_front_last_ask, back=clr_back_ask) + \
                                         color('/', fore=(255, 255, 255), back=clr_back_ask) + \
                                         color(self.pu.slot_convertor(ask_ask_size), fore=clr_front_ask_ask, back=clr_back_ask) + \
                                         ']'

                    value_data.append(normal_transaction)

                # Price exist in BID but Not in ASK
                elif ele_price in self.dict_last_size_on_bid[ele_time] and ele_price not in self.dict_last_size_on_ask[ele_time]:

                    # Add the volume size
                    last_bid_size = self.dict_last_size_on_bid[ele_time][ele_price]
                    bid_bid_size = self.dict_bid_size_on_bid[ele_time][ele_price]

                    # Define colors so we can change dynamically based on conditions
                    clr_front_last_bid = last_bid_colour_dictionary[last_bid_size]
                    clr_front_bid_bid = bid_bid_colour_dictionary[bid_bid_size]

                    clr_back_bid = (0, 0, 0)

                    # Hidden Buyer, Logic: Transaction on BID in T&S is higher than the BID on level II
                    if last_bid_size > bid_bid_size:
                        clr_back_bid = (0, 100, 0)

                    value_data.append(
                        color(self.pu.slot_convertor(last_bid_size), fore=clr_front_last_bid, back=clr_back_bid) +
                        color('/', fore=(255, 255, 255), back=clr_back_bid) +
                        color(self.pu.slot_convertor(bid_bid_size), fore=clr_front_bid_bid, back=clr_back_bid)
                        + f' ➜ {"0"}')

                # Price exist in ASK but Not in BID
                elif ele_price not in self.dict_last_size_on_bid[ele_time] and ele_price in self.dict_last_size_on_ask[ele_time]:
                    # Add the volume size
                    last_ask_size = self.dict_last_size_on_ask[ele_time][ele_price]
                    ask_ask_size = self.dict_ask_size_on_ask[ele_time][ele_price]

                    clr_front_last_ask = last_ask_colour_dictionary[last_ask_size]
                    clr_front_ask_ask = ask_ask_colour_dictionary[ask_ask_size]

                    clr_back_ask = (0, 0, 0)

                    if last_ask_size > ask_ask_size:
                        clr_back_ask = (139, 0, 0)

                    value_data.append(
                        f'{"0"} ➜ '
                        + color(self.pu.slot_convertor(last_ask_size), fore=clr_front_last_ask, back=clr_back_ask) +
                        color('/', fore=(255, 255, 255), back=clr_back_ask) +
                        color(self.pu.slot_convertor(ask_ask_size), fore=clr_front_ask_ask, back=clr_back_ask))
                else:
                    value_data.append('')

            table_data.append(value_data)

        # Add current price pointer
        lst_price = ['{:0.2f}'.format(i) for i in lst_price]

        if bid_index is not None:
            try:
                if closest_price == bid_price:
                    # Increase the count if the price is on bid and reset the ask
                    self.concurrent_bids = self.concurrent_bids + 1
                    self.concurrent_asks = 0
                    # marker to the current price if it match to bid
                    lst_price[bid_index] = Color('{autored}' + '→ ' + str(bid_price) + '{/autored}')
                else:
                    lst_price[bid_index] = Color('{autored}' + str(bid_price) + '{/autored}')
            except IndexError:
                pass

        if ask_index is not None:
            try:
                if closest_price == ask_price:
                    # Increase the count if the price is on ask and reset bid
                    self.concurrent_asks = self.concurrent_asks + 1
                    self.concurrent_bids = 0
                    # marker to the current price if it match to ask
                    lst_price[ask_index] = Color('{autogreen}' + '→ ' + str(ask_price) + '{/autogreen}')
                else:
                    lst_price[ask_index] = Color('{autogreen}' + str(ask_price) + '{/autogreen}')
            except IndexError:
                pass

        # Show concurrent bids and ask count
        concon_asks = Color('{autogreen}On Ask (' + str(self.concurrent_asks) + '){/autogreen}')
        concon_bids = Color('{autored}On Bid (' + str(self.concurrent_bids) + '){/autored}')

        # Add price and time accordingly as header and index
        table_data.append(lst_price)
        table_data.append(ask_price_hist_agg)
        table_data.append(bid_price_hist_agg)
        table_data = list(map(list, zip(*table_data)))
        table_data.insert(0, global_time_limit + ['Price', concon_asks, concon_bids])

        # Create table instance
        table_instance = AsciiTable(table_data,
                                    f'  {self.ticker}       Spread: {round(ask_price - bid_price, 2)}       H.Blocks: {self.histogram_block_size}')
        table_instance.inner_heading_row_border = False
        table_instance.inner_row_border = True
        table_instance.inner_column_border = False

        # Align text for price column
        time_length = len(global_time_limit)
        table_instance.justify_columns = {time_length: 'right'}
        return table_instance.table
