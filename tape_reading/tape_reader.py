import itertools
from terminaltables import AsciiTable
from colorclass import Color
import numpy as np
from colr import color
from config import Config
import os
from numerize.numerize import numerize
from util import price_util
from datetime import datetime


class TapeReader:
    def __init__(self, ticker, data_writer: bool):
        """
        We don't track the actual price of last price here. rather we find the most close bid and ask price for the last price.
        The goal is to find the price on bid and price on ask for bullish and bearish signals.
        :param ticker:
        """
        self.pu = price_util.PriceUtil()

        # Price and size w.r.t BID and last, Bearish signal
        self.dict_last_size_on_bid = dict()

        # Price and size w.r.t ASK and last, Bullish signal
        self.dict_last_size_on_ask = dict()

        # Price and size w.r.t BID only, Higher Bids Holding, Bullish signal
        self.dict_bid_size_on_bid = dict()

        # Price and size w.r.t ASK only, Higher Asks Holding, Bearish signal
        self.dict_ask_size_on_ask = dict()

        # Counter of concurrent bid calls
        self.count_concurrent_sales_on_bid = 0

        # Counter of concurrent bid calls
        self.count_concurrent_sales_on_ask = 0

        # Clear Terminal
        self.clear = lambda: os.system('clear')
        self.clear_counter = 0

        # Dynamic Histogram block size, Default 100, Find the max transaction size and update accordingly
        self.histogram_block_size = 100

        # Most high price on ask, Bullish within the price range
        self.top_sales_on_ask = dict()

        # Most hit price on bids, Bearish within the price range
        self.top_sales_on_bid = dict()

        # Default 100
        self.top_sales_block_size = 100

        # Ticker by each second, So the size aggregation will be done by seconds
        self.ticker_name = ticker

        # green,green,yellow,yellow,white,white,
        self.colors_bullish = [(0, 255, 0), (0, 255, 0), (255, 255, 0), (255, 255, 0), (255, 255, 255), (255, 255, 255)]

        # red,red,yellow,yellow,white,white,
        self.colors_bearish = [(255, 0, 0), (255, 0, 0), (255, 255, 0), (255, 255, 0), (255, 255, 255), (255, 255, 255)]

        self.pu = price_util.PriceUtil()
        self.config = Config()
        self.time_ticks_filter = self.config.get_timesales_timeticks()

        self.DATE = datetime.today().strftime('%Y%m%d%H')

        self.data_writer = data_writer

        # Track previous bid and ask prices.
        self.previous_bid_price = 0
        self.previous_ask_price = 0

        # Track the previous time to print every second
        self.previous_time = None

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
        :param sizes: listed trade size w.r.t ask price on time ans sales
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

    @staticmethod
    def find_closest(bid: float, ask: float, last: float) -> float:
        """
        Find the closest price w.r.t to bid and ask compare to last value
        :param bid: bid price, level II first tier only
        :param ask: ask price, level II first tier only
        :param last: last price, Time & Sales
        :return: Closest possible to bid or ask
        """
        return min([bid, ask], key=lambda x: abs(x - last))

    def find_top_sales(self, ask_price, bid_price, closest_price, last_size):
        """
        Keep track of price on BID w.r.t highest size
        :param ask_price:
        :param bid_price:
        :param closest_price:
        :param last_size:
        :return:
        """
        if closest_price == bid_price:
            if closest_price in self.top_sales_on_bid:
                if self.top_sales_on_bid[closest_price] < last_size:
                    self.top_sales_on_bid[closest_price] = self.pu.round_size(last_size)
            else:
                self.top_sales_on_bid[closest_price] = self.pu.round_size(last_size)
        """
        Keep track of price on ASK w.r.t highest size
        """
        if closest_price == ask_price:
            if closest_price in self.top_sales_on_ask:
                if self.top_sales_on_ask[closest_price] < last_size:
                    self.top_sales_on_ask[closest_price] = self.pu.round_size(last_size)
            else:
                self.top_sales_on_ask[closest_price] = self.pu.round_size(last_size)

    def level_ii_bids_asks(self, ask_price, ask_size, bid_price, bid_size, tick_time):
        """
        This is one of the critical task. Because we need to track the previous bid and ask price as well to check whether the price is holding or not

        :param tick_time: Time of ticker
        :param bid_price: bid price, level II first tier only
        :param bid_size: bid size, level II first tier only
        :param ask_price: ask price, level II first tier only
        :param ask_size: ask size, level II first tier only
        :return:
        """

        """
        BID size w.r.t BID price
        Collect bid price regardless of last executed price. If time already exist in dictionary, Regardless of last price UPDATE the CURRENT 
        bid price and size
        """
        if tick_time in self.dict_bid_size_on_bid:
            """    
            Update the previous bid size, if it's not holding. If we don't do this, then in table the price will shows as holding
            """
            if self.previous_bid_price == bid_price:
                self.dict_bid_size_on_bid[tick_time][bid_price] = bid_size
            else:
                if self.previous_bid_price != 0:
                    # If the previous price is not holding the bid
                    self.dict_bid_size_on_bid[tick_time][self.previous_bid_price] = 0
        else:
            # Current new bid price and size
            self.dict_bid_size_on_bid[tick_time] = {bid_price: bid_size}

        # Track current bid price for the next iteration as previous bid price
        self.previous_bid_price = bid_price

        """
        ASK size w.r.t ASK
        Collect ask price regardless of last price.
        """
        if tick_time in self.dict_ask_size_on_ask:
            """    
            Update the previous ask size, if it's not holding. If we don't do this, then in table the price will shows as holding
            """
            if self.previous_ask_price == ask_price:
                self.dict_ask_size_on_ask[tick_time][ask_price] = ask_size
            else:
                if self.previous_ask_price != 0:
                    # If the previous price is not holding the ask
                    self.dict_ask_size_on_ask[tick_time][self.previous_ask_price] = 0
        else:
            # Current new ask price and size
            self.dict_ask_size_on_ask[tick_time] = {ask_price: ask_size}

        # Track current ask price for the next iteration as previous ask price
        self.previous_ask_price = ask_price

    def data_dictionary_generator(self, tick_time: str, bid_price: float, bid_size: int, ask_price: float, ask_size: int, closest_price: float,
                                  last_size: int):
        """
        This function will udpate the values in dictionary regardless of 1sec table print on terminal.
        :param tick_time: Time of ticker
        :param bid_price: bid price, level II first tier only
        :param bid_size: bid size, level II first tier only
        :param ask_price: ask price, level II first tier only
        :param ask_size: ask size, level II first tier only
        :param closest_price: price close to bid or ask
        :param last_size: last size, time & sales
        :return:
        """

        self.find_top_sales(ask_price, bid_price, closest_price, last_size)

        self.level_ii_bids_asks(ask_price, ask_size, bid_price, bid_size, tick_time)

        """
        Time based accumulator dictionary is a dictionary of, dictionary data structure. 
        Dictionary: {Key: Time, value: Dictionary(key: price, value: size)}
        The size will be updated and aggregated through the iteration process by finding time and price accordingly
        """
        if tick_time in self.dict_last_size_on_bid:
            """
            Last size w.r.t BID price
            Find the closest price for last price. If the closest price match to bid price. Then the transaction considered as "Trade on BID", 
            Bearish Signal
            
            If the API call is from level II, then the "last size will be 0"
            """
            if closest_price == bid_price:
                # If the close price is not already created from time and sales API call, If already exist, Not need to worry
                if closest_price in self.dict_last_size_on_bid[tick_time]:
                    # Sales on bid, If the call is from Level II then the last size will be 0
                    self.dict_last_size_on_bid[tick_time][bid_price] = self.dict_last_size_on_bid[tick_time][bid_price] + last_size
                else:
                    self.dict_last_size_on_bid[tick_time][bid_price] = last_size
            else:
                if bid_price not in self.dict_last_size_on_bid[tick_time]:
                    # Dummy bid price entry based on level II
                    self.dict_last_size_on_bid[tick_time][bid_price] = 0

            if ask_price not in self.dict_last_size_on_bid[tick_time]:
                # Dummy ask price in "dict_last_size_on_bid" dictionary, Because the the price is on bid
                self.dict_last_size_on_bid[tick_time][ask_price] = 0
        else:
            # If tick time not exist, Create entry for bid and dummy for price on ask
            if closest_price == bid_price:
                self.dict_last_size_on_bid[tick_time] = {bid_price: last_size, ask_price: 0}
            else:
                self.dict_last_size_on_bid[tick_time] = {bid_price: 0, ask_price: 0}

        if tick_time in self.dict_last_size_on_ask:
            """
            Last size w.r.t ASK price
            Find the closest price for last price. If the closes price match to ask price. Then the transaction considered as "Trade on ASK",
            Bullish Signal
            
            If the API call is from level II, then the "last size will be 0"
            """
            if closest_price == ask_price:
                # If the close price is not already created from time and sales API call, If already exist, Not need to worry
                if closest_price in self.dict_last_size_on_ask[tick_time]:
                    # Sales on ask
                    self.dict_last_size_on_ask[tick_time][ask_price] = self.dict_last_size_on_ask[tick_time][ask_price] + last_size
                else:
                    self.dict_last_size_on_ask[tick_time][ask_price] = last_size
            else:
                # Which is bid price, Where we shold have entry on "dict_last_size_on_bid" dictionary
                if ask_price not in self.dict_last_size_on_ask[tick_time]:
                    self.dict_last_size_on_ask[tick_time][ask_price] = 0

            if bid_price not in self.dict_last_size_on_ask[tick_time]:
                # Dummy bid price in "dict_last_size_on_ask" dictionary, Because the the price is on ask
                self.dict_last_size_on_ask[tick_time][bid_price] = 0

        else:
            # If tick time not exist
            if closest_price == ask_price:
                self.dict_last_size_on_ask[tick_time] = {ask_price: last_size, bid_price: 0}
            else:
                self.dict_last_size_on_ask[tick_time] = {ask_price: 0, bid_price: 0}

    def level_ii_api_call(self, tick_time: str, bid_price, bid_size, ask_price, ask_size, last_price, last_size):
        """
        Update table when the level II api triggered in "middle of" time and sales calls

        Tackle Use case:
            call: last
            call: bid and ask
            call: bid and ask
            call: bid and ask
            call: last

        When we get multiple bid and ask calls before the "last" call. we will not update the table. Since we were only calling the table update
        function only when "last" is called. "data_generator_level_ii_call" function will update bid and ask values with the above use case. Here
        we don't do any aggregation. We just update the bid and ask values when ever the level II data function get triggered

        :param tick_time: Time of ticker
        :param bid_price: bid price, level II first tier only
        :param bid_size: bid size, level II first tier only
        :param ask_price: ask price, level II first tier only
        :param ask_size: ask size, level II first tier only
        :param last_price: last price, time & sales
        :param last_size: last size, time & sales
        :return: None, Show table in terminal
        """

        if self.previous_time is None:
            # Set current time as previous time if it's none
            self.previous_time = tick_time

        # Write data to file
        if self.data_writer:
            with open(f'test_data/{self.DATE}_{self.ticker_name}.csv', 'a') as file_writer:
                file_writer.write(f'{tick_time},{bid_price},{bid_size},{ask_price},{ask_size},{last_price},{last_size},l2\n')

        # Find the closest price w.r.t to last price on bid or ask
        closest_price = self.find_closest(bid_price, ask_price, last_price)

        # Update the level II bid and ask with sizes
        self.data_dictionary_generator(tick_time, bid_price, bid_size, ask_price, ask_size, closest_price, last_size)

        # Don't initiate the print until we get the api call in last to update the dictionary
        if (bool(self.dict_last_size_on_ask)) and (bool(self.dict_last_size_on_bid)) and (self.previous_time != tick_time):
            self.previous_time = tick_time
            self.clear()
            print(self.display_data(closest_price, bid_price, ask_price, 'L2'))

    def time_sales_api_call(self, tick_time: str, bid_price, bid_size, ask_price, ask_size, last_price, last_size):
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
        :return: :return: None, Show table in terminal
        """
        if self.previous_time is None:
            self.previous_time = tick_time

        # Find the closest price w.r.t to last price on bid or ask
        closest_price = self.find_closest(bid_price, ask_price, last_price)

        # Write data to file
        if self.data_writer:
            with open(f'test_data/{self.DATE}_{self.ticker_name}.csv', 'a') as file_writer:
                file_writer.write(f'{tick_time},{bid_price},{bid_size},{ask_price},{ask_size},{last_price},{last_size},t&s\n')

        self.data_dictionary_generator(tick_time, bid_price, bid_size, ask_price, ask_size, closest_price, last_size)

        if self.previous_time != tick_time:
            self.previous_time = tick_time
            self.clear()
            print(self.display_data(closest_price, bid_price, ask_price, 'T&S'))

    def top_sales_histogram(self, global_price_limit):
        """
        Generate histogram for top sales
        :param global_price_limit:
        :return:
        """
        top_sales_on_ask_list = [self.top_sales_on_ask[i] if i in self.top_sales_on_ask else 0 for i in global_price_limit]
        top_sales_on_bid_list = [self.top_sales_on_bid[i] if i in self.top_sales_on_bid else 0 for i in global_price_limit]
        # Find the mean from top bid and ask sizes
        self.top_sales_block_size = int(max(self.pu.round_size((np.mean(top_sales_on_bid_list) + np.mean(top_sales_on_ask_list)) / 2), 100))
        # Top sales on ask
        top_sales_on_ask_hist = [round(i / self.top_sales_block_size) * color('↑', fore=(0, 255, 0), back=(0, 0, 0)) for i in top_sales_on_ask_list]
        # Top sales on bid
        top_sales_on_bid_hist = [round(i / self.top_sales_block_size) * color('↓', fore=(255, 0, 0), back=(0, 0, 0)) for i in top_sales_on_bid_list]
        return top_sales_on_ask_hist, top_sales_on_bid_hist

    def time_and_sales_histogram(self, global_price_limit, global_time_limit, last_ask_sizes, last_bid_sizes):
        """
        Generate histogram by aggregating sizes of sales on bid and aks withen the given time frame
        :param global_price_limit:
        :param global_time_limit:
        :param last_ask_sizes:
        :param last_bid_sizes:
        :return:
        """
        # Price histogram generation
        list_last_bid_price_size_dict = [self.dict_last_size_on_bid[i] for i in global_time_limit]  # Price on Bid, Bearish Signal
        list_last_ask_price_size_dict = [self.dict_last_size_on_ask[i] for i in global_time_limit]  # Price on Ask, Bullish Signal

        # Aggregate the size on BIDs
        bid_price_size_agg = dict()
        for price_size in list_last_bid_price_size_dict:
            for var_price in price_size.keys():
                if var_price in bid_price_size_agg:
                    bid_price_size_agg[var_price] = bid_price_size_agg[var_price] + price_size[var_price]
                else:
                    bid_price_size_agg[var_price] = price_size[var_price]

        # Aggregate the size on ASKs
        ask_price_size_agg = dict()
        for price_size in list_last_ask_price_size_dict:
            for var_price in price_size.keys():
                if var_price in ask_price_size_agg:
                    ask_price_size_agg[var_price] = ask_price_size_agg[var_price] + price_size[var_price]
                else:
                    ask_price_size_agg[var_price] = price_size[var_price]

        # Mean size transaction on bid
        max_last_bid_size = np.mean(last_bid_sizes)

        # Mean size transaction on bid
        max_last_ask_size = np.mean(last_ask_sizes)

        # Find the average of sales on mean of bid and ask, Keep the block size consistent across bid and ask to see the trend and round to 100's
        self.histogram_block_size = int(max(self.pu.round_size((max_last_bid_size + max_last_ask_size) / 2), 100))

        # Price on ask bullish
        ask_price_hist_agg = [round(ask_price_size_agg[i] / self.histogram_block_size) * color('↑', fore=(0, 255, 0), back=(0, 0, 0)) for i in
                              global_price_limit]

        # Price on bid bearish
        bid_price_hist_agg = [round(bid_price_size_agg[i] / self.histogram_block_size) * color('↓', fore=(255, 0, 0), back=(0, 0, 0)) for i in
                              global_price_limit]

        return ask_price_hist_agg, bid_price_hist_agg

    def display_data(self, closest_price: float, bid_price: float, ask_price: float, source: str):
        """
        Generate table for terminal outputs
        :param closest_price: The price closest to bid or ask w.r.t last price. Which may not be an actual last price
        :param bid_price: bid price, level II first tier only
        :param ask_price: ask price, level II first tier only
        :param source: API call source
        :return: table for terminal visualisation
        """

        # Limit the moving time, take bid as reference because the time across dictionary will be same. That how the data aggregation has been done
        global_time_limit = sorted(set(list(self.dict_last_size_on_bid.keys())
                                       + list(self.dict_last_size_on_ask.keys())
                                       + list(self.dict_ask_size_on_ask.keys())
                                       + list(self.dict_bid_size_on_bid.keys())))[-self.time_ticks_filter:]

        """
        Price and Size w.r.t BID
        """
        # All the prices on bid within the time limit and reverse high to low
        last_bid_prices = sorted(
            list((set(itertools.chain.from_iterable([list(self.dict_last_size_on_bid[i].keys()) for i in global_time_limit])))), reverse=True)

        # All the sizes on bid within the time limit and and sorted
        last_bid_sizes = sorted(set(itertools.chain.from_iterable([self.dict_last_size_on_bid[i].values() for i in global_time_limit])))

        # Colour for each order size, Bearish Signal, RED on high volume
        last_bid_colour_dictionary = self.get_colour_by_bearish(last_bid_sizes)

        # Pick the sizes which are visible in the time frame
        bid_bid_sizes = sorted(set(itertools.chain.from_iterable([self.dict_bid_size_on_bid[i].values() for i in global_time_limit])))

        # Colour for each BID size, , Higher Bids and hold, Bullish Signal, Green on high volume
        bid_bid_colour_dictionary = self.get_colour_by_bullish(bid_bid_sizes)

        # BID on BID
        # All the bid calls within the time limit and reverse high to low
        bid_bid_lst_price = sorted(
            list((set(itertools.chain.from_iterable([list(self.dict_bid_size_on_bid[i].keys()) for i in global_time_limit])))), reverse=True)

        """        
        Price and Size w.r.t ASK
        """
        # All the prices on ask within the time limit and reverse low to high
        ask_lst_price = sorted(
            list((set(itertools.chain.from_iterable([list(self.dict_last_size_on_ask[i].keys()) for i in global_time_limit])))), reverse=True)

        # All the sizes on ask within the time limit and and sorted
        last_ask_sizes = sorted(set(itertools.chain.from_iterable([self.dict_last_size_on_ask[i].values() for i in global_time_limit])))

        ask_ask_sizes = sorted(
            set(itertools.chain.from_iterable([self.dict_ask_size_on_ask[i].values() for i in global_time_limit])))

        # Colour for each order size, Bullish Signal, Green on high volume
        last_ask_colour_dictionary = self.get_colour_by_bullish(last_ask_sizes)

        # Colour for each ASK size, , Higher ASK and hold , Bearish Signal, Red on high volume
        ask_ask_colour_dictionary = self.get_colour_by_bearish(ask_ask_sizes)

        # ASK on ASK
        # All the ask calls within the time limit and reverse high to low
        ask_ask_lst_price = sorted(
            list((set(itertools.chain.from_iterable([list(self.dict_ask_size_on_ask[i].keys()) for i in global_time_limit])))), reverse=True)

        # Balance the price range
        global_price_limit = sorted(set(last_bid_prices + ask_lst_price + bid_bid_lst_price + ask_ask_lst_price), reverse=True)

        bid_index = None
        ask_index = None

        try:
            bid_index = global_price_limit.index(bid_price)
            ask_index = global_price_limit.index(ask_price)

            # Add the range of movement in the table
            if self.config.get_price_range_enabler():
                min_range = 0 if bid_index - self.config.get_timesales_price_range() < 0 else bid_index - self.config.get_timesales_price_range()
                max_range = ask_index + self.config.get_timesales_price_range()
                global_price_limit = global_price_limit[min_range:max_range]
        except ValueError:
            """
            It's perfectly fine to pass this exception. Because we may have cases like below
            1. Currently we read only the last price after the completion. Therefore we may not able to find,
                1. Ask price on current price list. which may not be executed so far
                2. Bid price on current price list. which may not be executed so far
                
            So we don't need to track if those prices are out of rance
            """
            # raise e
            pass

        # Generate top sales histogram data
        top_sales_on_ask_hist, top_sales_on_bid_hist = self.top_sales_histogram(global_price_limit)

        # Generate histogram data for sizes on bid and ask
        ask_price_hist_agg, bid_price_hist_agg = self.time_and_sales_histogram(global_price_limit, global_time_limit, last_ask_sizes, last_bid_sizes)

        # Generate table
        table_data = []
        for current_time in global_time_limit:
            value_data = []
            for current_price in global_price_limit:
                # Price both bid and ask
                if current_price in self.dict_last_size_on_bid[current_time] and current_price in self.dict_last_size_on_ask[current_time]:

                    # Select sizes for each price and time
                    last_bid_size = self.dict_last_size_on_bid[current_time][current_price]
                    last_ask_size = self.dict_last_size_on_ask[current_time][current_price]
                    try:
                        bid_bid_size = self.dict_bid_size_on_bid[current_time][current_price]
                    except KeyError:
                        bid_bid_size = 0
                    try:
                        ask_ask_size = self.dict_ask_size_on_ask[current_time][current_price]
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
                elif current_price in self.dict_last_size_on_bid[current_time] and current_price not in self.dict_last_size_on_ask[current_time]:

                    # Add the volume size
                    last_bid_size = self.dict_last_size_on_bid[current_time][current_price]
                    bid_bid_size = self.dict_bid_size_on_bid[current_time][current_price]

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
                elif current_price not in self.dict_last_size_on_bid[current_time] and current_price in self.dict_last_size_on_ask[current_time]:
                    # Add the volume size
                    last_ask_size = self.dict_last_size_on_ask[current_time][current_price]
                    ask_ask_size = self.dict_ask_size_on_ask[current_time][current_price]

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
        global_price_limit = ['{:0.2f}'.format(i) for i in global_price_limit]

        if bid_index is not None:
            try:
                if closest_price == bid_price:
                    # Increase the count if the price is on bid and reset the ask
                    self.count_concurrent_sales_on_bid = self.count_concurrent_sales_on_bid + 1
                    self.count_concurrent_sales_on_ask = 0
                    # marker to the current price if it match to bid
                    global_price_limit[bid_index] = Color('{autored}' + '→ ' + str(bid_price) + '{/autored}')
                else:
                    global_price_limit[bid_index] = Color('{autored}' + str(bid_price) + '{/autored}')
            except IndexError:
                pass

        if ask_index is not None:
            try:
                if closest_price == ask_price:
                    # Increase the count if the price is on ask and reset bid
                    self.count_concurrent_sales_on_ask = self.count_concurrent_sales_on_ask + 1
                    self.count_concurrent_sales_on_bid = 0
                    # marker to the current price if it match to ask
                    global_price_limit[ask_index] = Color('{autogreen}' + '→ ' + str(ask_price) + '{/autogreen}')
                else:
                    global_price_limit[ask_index] = Color('{autogreen}' + str(ask_price) + '{/autogreen}')
            except IndexError:
                pass

        # Show concurrent bids and ask count
        concon_asks = Color(
            '{autogreen}On Ask (' + str(self.count_concurrent_sales_on_ask) + '){/autogreen}') + f'\n   {numerize(self.histogram_block_size)}'
        concon_bids = Color(
            '{autored}On Bid (' + str(self.count_concurrent_sales_on_bid) + '){/autored}') + f'\n{numerize(self.histogram_block_size)}    '

        # Add price and time accordingly as header and index
        table_data.append(global_price_limit)
        table_data.append(top_sales_on_bid_hist)
        table_data.append(top_sales_on_ask_hist)
        table_data.append(bid_price_hist_agg)
        table_data.append(ask_price_hist_agg)
        table_data = list(map(list, zip(*table_data)))
        table_data.insert(0, global_time_limit + ['Price',
                                                  color(f'Top on Bid\n    {numerize(self.top_sales_block_size)}    ', fore=(255, 99, 92),
                                                        back=(0, 0, 0)),
                                                  color(f'Top on Ask\n    {numerize(self.top_sales_block_size)}    ', fore=(0, 255, 0),
                                                        back=(0, 0, 0)),
                                                  concon_bids,
                                                  concon_asks])

        # Prince Description
        print('\n\n')
        print(f'{source}      {self.ticker_name}       Spread: {round(ask_price - bid_price, 2)}')

        # Create table instance
        table_instance = AsciiTable(table_data)
        table_instance.inner_heading_row_border = False
        table_instance.inner_row_border = True
        table_instance.inner_column_border = False

        # Align text for price column
        time_length = len(global_time_limit)
        # Default alignment is on left
        table_instance.justify_columns = {time_length: 'right', time_length + 1: 'right', time_length + 2: 'left', time_length + 3: 'right'}
        return table_instance.table
