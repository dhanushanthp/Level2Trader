import itertools
from terminaltables import AsciiTable
import numpy as np
from colr import color
from config import Config
import os
from numerize.numerize import numerize
from src.util import price_util
from src.util import time_util
from datetime import datetime
import operator


class TapeReader:
    def __init__(self, ticker, data_writer: bool):
        """
        We don't track the actual price of last price here. rather we find the most close bid and ask price for the last price.
        The goal is to find the price on bid and price on ask for bullish and bearish signals.

        :param ticker:
        :param data_writer:
        """
        self.pu = price_util.PriceUtil()

        # Price and size w.r.t BID and last, Bearish signal
        self.dict_last_size_on_bid = dict()

        # Price and size w.r.t ASK and last, Bullish signal
        self.dict_last_size_on_ask = dict()

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

        self.pu = price_util.PriceUtil()
        self.tu = time_util.TimeUtil()
        self.config = Config()
        self.time_ticks_filter = self.config.get_timesales_timeticks()

        self.DATE = datetime.today().strftime('%Y%m%d%H')

        self.data_writer = data_writer

        # Track previous bid and ask prices.
        self.previous_bid_price = 0
        self.previous_ask_price = 0

        # Track the previous time to print every second
        self.previous_time = None

        # Reset top sales on every one minute
        self.top_sales_previous_time = None

        # Top sales tracker each minute
        self.top_sales_tracker = dict()

        self.time_frequency = self.config.get_time_frequency()

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

    def generate_top_sales(self, tick_time, ask_price, bid_price, closest_price, last_size):
        """
        Identification of top sales(sizes) in BID and ASK by time. If the time iterate by seconds then this function will find the top sizes on bid
        and ask in seconds. Also note than we receive more than 1 api calls within a second

        The API calls from level 1 bid & ask and time and sales won't impact the below process. Since we don't do any aggregation over time.

        :param tick_time: Time of ticker
        :param ask_price: ask price, level I current ask price
        :param bid_price: bid price, level I current bid price
        :param closest_price: price close to bid or ask
        :param last_size: last size, time & sales
        :return:
        """

        """
        Keep track of price on BID w.r.t highest/top size by time
        """
        if tick_time in self.top_sales_on_bid:
            """
            Last size w.r.t BID price
            Find the closest price for last price. If the closest price match to bid price. Then the transaction considered as "Trade on BID", 
            Bearish Signal

            If the API call is from level i bid and ask, then the "last size will be 0", Therefore it will not impact the aggregation
            """
            if closest_price == bid_price:
                # If the close price is not already created from time and sales API call, If already exist, Not need to worry
                if closest_price in self.top_sales_on_bid[tick_time]:
                    # Sales on bid, If the call is from Level II then the last size will be 0
                    if last_size > self.top_sales_on_bid[tick_time][bid_price]:
                        # Update with big size in the same time frame
                        self.top_sales_on_bid[tick_time][bid_price] = self.pu.round_size(last_size)
                    else:
                        # Don't update any
                        pass
                else:
                    self.top_sales_on_bid[tick_time][bid_price] = last_size
            else:
                if bid_price not in self.top_sales_on_bid[tick_time]:
                    # Dummy bid price entry based on level II
                    self.top_sales_on_bid[tick_time][bid_price] = 0

            if ask_price not in self.top_sales_on_bid[tick_time]:
                # Dummy ask price in "dict_last_size_on_bid" dictionary, Because the the price is on bid
                self.top_sales_on_bid[tick_time][ask_price] = 0
        else:
            # If tick time not exist, Create entry for bid and dummy for price on ask
            if closest_price == bid_price:
                self.top_sales_on_bid[tick_time] = {bid_price: last_size, ask_price: 0}
            else:
                self.top_sales_on_bid[tick_time] = {bid_price: 0, ask_price: 0}

        """
        Keep track of price on ASK w.r.t highest/top size by time
        """
        if tick_time in self.top_sales_on_ask:
            """
            Last size w.r.t ASK price
            Find the closest price for last price. If the closes price match to ask price. Then the transaction considered as "Trade on ASK",
            Bullish Signal

            If the API call is from level II, then the "last size will be 0"
            """
            if closest_price == ask_price:
                # If the close price is not already created from time and sales API call, If already exist, Not need to worry
                if closest_price in self.top_sales_on_ask[tick_time]:
                    # Sales on ask
                    if last_size > self.top_sales_on_ask[tick_time][ask_price]:
                        self.top_sales_on_ask[tick_time][ask_price] = self.pu.round_size(last_size)
                    else:
                        # Don't update any
                        pass
                else:
                    self.top_sales_on_ask[tick_time][ask_price] = last_size
            else:
                # Which is bid price, Where we should have entry on "dict_last_size_on_bid" dictionary
                if ask_price not in self.top_sales_on_ask[tick_time]:
                    self.top_sales_on_ask[tick_time][ask_price] = 0

            if bid_price not in self.top_sales_on_ask[tick_time]:
                # Dummy bid price in "dict_last_size_on_ask" dictionary, Because the the price is on ask
                self.top_sales_on_ask[tick_time][bid_price] = 0

        else:
            # If tick time not exist
            if closest_price == ask_price:
                self.top_sales_on_ask[tick_time] = {ask_price: last_size, bid_price: 0}
            else:
                self.top_sales_on_ask[tick_time] = {ask_price: 0, bid_price: 0}

        # self.generate_top_sales_overtime(tick_time)

    def generate_time_and_sales(self, ask_price, bid_price, closest_price, last_size, tick_time):
        """
        Time based accumulator dictionary is a dictionary of, dictionary data structure.
            Dictionary: {Key: Time, value: Dictionary(key: price, value: size)}
        The size will be updated and aggregated through the iteration process by finding time and price accordingly
        :param ask_price:
        :param bid_price:
        :param closest_price:
        :param last_size:
        :param tick_time:
        :return:
        """

        if tick_time in self.dict_last_size_on_bid:
            """
            Last size w.r.t BID price
            Find the closest price for last price. If the closest price match to bid price. Then the transaction considered as "Trade on BID", 
            Bearish Signal

            If the API call is from level i bid and ask, then the "last size will be 0", Therefore it will not impact the aggregation
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
                # Which is bid price, Where we should have entry on "dict_last_size_on_bid" dictionary
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

    def data_dictionary_generator(self, tick_time: str, bid_price: float, bid_size: int, ask_price: float, ask_size: int, closest_price: float,
                                  last_size: int):
        """
        This function will update the values in dictionary regardless of 1sec table print on terminal.

        :param tick_time: Time of ticker
        :param bid_price: bid price, level II first tier only
        :param bid_size: bid size, level II first tier only
        :param ask_price: ask price, level II first tier only
        :param ask_size: ask size, level II first tier only
        :param closest_price: price close to bid or ask
        :param last_size: last size, time & sales
        :return:
        """

        self.generate_top_sales(tick_time, ask_price, bid_price, closest_price, last_size)

        self.generate_time_and_sales(ask_price, bid_price, closest_price, last_size, tick_time)

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
        # Write data to file
        if self.data_writer:
            with open(f'data/test_data/{self.DATE}_{self.ticker_name}.csv', 'a') as file_writer:
                file_writer.write(f'{tick_time},{bid_price},{bid_size},{ask_price},{ask_size},{last_price},{last_size},l2\n')

        tick_time_split = tick_time.split(":")
        tick_time = ':'.join(tick_time_split[:-1]) + ':' + self.tu.round_time(int(tick_time_split[-1]), base=self.time_frequency)

        if self.previous_time is None:
            # Set current time as previous time if it's none
            self.previous_time = tick_time

        # Find the closest price w.r.t to last price on bid or ask
        closest_price = self.find_closest(bid_price, ask_price, last_price)

        # Don't initiate the print until we get the api call in last to update the dictionary
        if (bool(self.top_sales_on_ask)) and (bool(self.top_sales_on_bid)) and (self.previous_time != tick_time):
            self.clear()
            print(self.display_data(closest_price, bid_price, ask_price, 'L1B_A'))
            self.previous_time = tick_time

        # Update the level II bid and ask with sizes
        self.data_dictionary_generator(tick_time, bid_price, bid_size, ask_price, ask_size, closest_price, last_size)

    def time_sales_api_call(self, tick_time: str, bid_price, bid_size, ask_price, ask_size, last_price, last_size, exchange):
        """
        Update table when time and sales api triggered
        :param tick_time: Time of ticker
        :param bid_price: bid price, level II first tier only
        :param bid_size: bid size, level II first tier only
        :param ask_price: ask price, level II first tier only
        :param ask_size: ask size, level II first tier only
        :param last_price: last price, time & sales
        :param last_size: last size, time & sales
        :param exchange:
        :return: None, Show table in terminal
        """

        # Write data to file
        if self.data_writer:
            with open(f'data/test_data/{self.DATE}_{self.ticker_name}.csv', 'a') as file_writer:
                file_writer.write(f'{tick_time},{bid_price},{bid_size},{ask_price},{ask_size},{last_price},{last_size},t&s\n')

        tick_time_split = tick_time.split(":")
        tick_time = ':'.join(tick_time_split[:-1]) + ':' + self.tu.round_time(int(tick_time_split[-1]), base=self.time_frequency)

        if self.previous_time is None:
            self.previous_time = tick_time

        # Find the closest price w.r.t to last price on bid or ask
        closest_price = self.find_closest(bid_price, ask_price, last_price)

        if self.previous_time != tick_time:
            self.clear()
            # This function needs to be triggered before calling data dictionary generator to avoid the next time tick partial call
            print(self.display_data(closest_price, bid_price, ask_price, 'T&S'))
            self.previous_time = tick_time

        self.data_dictionary_generator(tick_time, bid_price, bid_size, ask_price, ask_size, closest_price, last_size)

    def top_sales_histogram(self, global_price_limit):
        """
        Generate histogram for top sales

        :param global_price_limit: Max time range
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
        Generate histogram by aggregating sizes of sales on bid and aks within the **given time frame**

        :param global_price_limit: Max price range
        :param global_time_limit: Max time range
        :param last_ask_sizes: size on ask price
        :param last_bid_sizes: size on bid price
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

        ask_price_hist_agg = []
        bid_price_hist_agg = []

        # Find the percentage of size distribution for the same price on bid and ask
        for price in global_price_limit:
            # Price on ask by specific time
            ask_sizes = ask_price_size_agg[price]
            # Price on bid by specific time
            bid_sizes = bid_price_size_agg[price]

            total_bids = int(np.sum(bid_sizes))
            total_asks = int(np.sum(ask_sizes))
            totals = np.sum(total_asks + total_bids)

            # Find bid to ask size ratio on sales
            ask_ratio = round(total_asks / totals, 2)
            bid_ratio = round(total_bids / totals, 2)

            # Clean 0 values
            ask_ratio = ask_ratio if (ask_ratio != 0.0) or np.isnan(ask_ratio) else ''
            bid_ratio = bid_ratio if (bid_ratio != 0.0) or np.isnan(bid_ratio) else ''
            total_asks = numerize(total_asks) if total_asks != 0.0 else ''
            total_bids = numerize(total_bids) if total_bids != 0.0 else ''

            ask_price_hist_agg.append(f'{ask_ratio} {total_asks}')
            bid_price_hist_agg.append(f'{total_bids} {bid_ratio}')

        return ask_price_hist_agg, bid_price_hist_agg

    @staticmethod
    def calculate_ranks(dict_prices, all_prices):
        """
        Calculate and rank the top size levels w.r.t last n minutes. Currently its set as 10 minutes and rank top 3
        :param dict_prices: Dictionary of prices with size
        :param all_prices: All the prices in valid range
        :return:
        """
        # Tuple of price list generated from list of price and size dictionary, Converted the dictionary to tuple
        tuple_lst_price_size = list(itertools.chain.from_iterable([zip(list(i.keys()), list(i.values())) for i in dict_prices]))

        # Sort by size
        tuple_lst_price_size = sorted(tuple_lst_price_size, key=lambda tup: tup[1], reverse=True)[:3]

        price_dict = {}
        for idx, i in enumerate(tuple_lst_price_size):
            price = i[0]
            if price in price_dict:
                price_dict[price].append(str(idx + 1))
            else:
                price_dict[price] = [str(idx + 1)]

        # If the price holding top sales in multiple timeframe then we may get multiple rank for the same price
        price_ranks = [', '.join(price_dict[i]) if i in price_dict else '' for i in all_prices]

        return price_ranks

    def display_data(self, closest_price: float, bid_price: float, ask_price: float, source: str):
        """
        Generate table for terminal outputs

        :param closest_price: The price closest to bid or ask w.r.t last price. Which may not be an actual last price
        :param bid_price: bid price, level II first tier only
        :param ask_price: ask price, level II first tier only
        :param source: API call source
        :return: table for terminal visualisation
        """

        # Limit the moving time to bid and ask ranges
        global_time_limit = sorted(set(list(self.top_sales_on_bid.keys()) + list(self.top_sales_on_ask.keys())))[-self.time_ticks_filter:]

        # All the prices on bid within the time limit and reverse high to low
        last_bid_prices = sorted(
            list((set(itertools.chain.from_iterable([list(self.top_sales_on_bid[i].keys()) for i in global_time_limit])))), reverse=True)

        bid_prices_sizes = [self.top_sales_on_bid[i] for i in global_time_limit]

        # All the prices on ask within the time limit and reverse low to high
        ask_lst_price = sorted(
            list((set(itertools.chain.from_iterable([list(self.top_sales_on_ask[i].keys()) for i in global_time_limit])))), reverse=True)

        # All the sizes on ask within the time limit and and sorted
        last_ask_sizes = sorted(set(itertools.chain.from_iterable([self.top_sales_on_ask[i].values() for i in global_time_limit])))

        ask_prices_sizes = [self.top_sales_on_ask[i] for i in global_time_limit]

        # Balance the price range
        global_price_limit = sorted(set(last_bid_prices + ask_lst_price), reverse=True)

        total_sizes = np.sum(last_ask_sizes + last_ask_sizes)

        bid_rank = self.calculate_ranks(bid_prices_sizes, global_price_limit)
        ask_rank = self.calculate_ranks(ask_prices_sizes, global_price_limit)

        # Highlight by colour
        bid_rank = [color(i, fore=(255, 0, 0), back=(0, 0, 0)) if i != '' else '' for i in bid_rank]
        ask_rank = [color(i, fore=(0, 255, 0), back=(0, 0, 0)) if i != '' else '' for i in ask_rank]

        # Combine the ranks
        ranks = ['\n'.join(x) for x in zip(ask_rank, bid_rank)]

        """
        Generate data for the table with high sales on bid and ask within given time frame. 
        """
        table_data = []
        block_size = 5000
        for current_time in global_time_limit:
            value_data = []
            for current_price in global_price_limit:
                # Price both bid and ask
                if current_price in self.top_sales_on_bid[current_time] and current_price in self.top_sales_on_ask[current_time]:

                    # Select sizes for each price and time
                    last_bid_size = self.top_sales_on_bid[current_time][current_price]
                    last_bid_size = '(' + str(round((last_bid_size / total_sizes) * 100)).zfill(2) + '%) ' + numerize(
                        last_bid_size) + round(last_bid_size / block_size) * color('↓', fore=(255, 0, 0),
                                                                                   back=(0, 0, 0)) if last_bid_size != 0 else ' '
                    last_ask_size = self.top_sales_on_ask[current_time][current_price]
                    last_ask_size = '(' + str(round((last_ask_size / total_sizes) * 100)).zfill(2) + '%) ' + numerize(
                        last_ask_size) + round(last_ask_size / block_size) * color('↑', fore=(0, 255, 0),
                                                                                   back=(0, 0, 0)) if last_ask_size != 0 else ' '

                    normal_transaction = color(last_ask_size, fore=(0, 255, 0), back=(0, 0, 0)) + '\n' + color(last_bid_size, fore=(255, 0, 0),
                                                                                                               back=(0, 0, 0))
                    value_data.append(normal_transaction)

                # Price exist in BID but Not in ASK
                elif current_price in self.top_sales_on_bid[current_time] and current_price not in self.top_sales_on_ask[current_time]:

                    # Add the volume size
                    last_bid_size = self.top_sales_on_bid[current_time][current_price]
                    value_data.append(
                        '\n' + color('(' + str(round((last_bid_size / total_sizes) * 100)).zfill(2) + '%) ' + numerize(last_bid_size),
                                     fore=(255, 0, 0),
                                     back=(0, 0, 0)) + round(last_bid_size / block_size) * color('↓', fore=(255, 0, 0),
                                                                                                 back=(0, 0, 0)))

                # Price exist in ASK but Not in BID
                elif current_price not in self.top_sales_on_bid[current_time] and current_price in self.top_sales_on_ask[current_time]:
                    # Add the volume size
                    last_ask_size = self.top_sales_on_ask[current_time][current_price]
                    value_data.append(
                        color('(' + str(round((last_ask_size / total_sizes) * 100)).zfill(2) + '%) ' + numerize(last_ask_size), fore=(0, 255, 0),
                              back=(0, 0, 0)) + round(last_ask_size / block_size) * color('↑', fore=(0, 255, 0),
                                                                                          back=(0, 0, 0)))
                else:
                    value_data.append('')

            table_data.append(value_data)

        # Add current price pointer
        global_price_limit = ['{:0.2f}'.format(i) for i in global_price_limit]

        """
        Mark prices for the  latest time top sizes. Generate the color for top sales on ask and bid on latest timestamp
        """
        latest_time_stamp = global_time_limit[-1]
        latest_size_on_price_ask = self.top_sales_on_ask[latest_time_stamp]
        latest_size_on_price_bid = self.top_sales_on_bid[latest_time_stamp]
        indicator_top_ask_size_price = str(max(latest_size_on_price_ask.items(), key=operator.itemgetter(1))[0])
        indicator_top_bid_size_price = str(max(latest_size_on_price_bid.items(), key=operator.itemgetter(1))[0])

        global_price_limit = [color(i, fore=(0, 0, 0), back=(0, 255, 0)) + '\n' if i == indicator_top_ask_size_price else i for i in
                              global_price_limit]
        global_price_limit = ['\n' + color(i, fore=(255, 255, 255), back=(255, 0, 0)) if i == indicator_top_bid_size_price else i for i in
                              global_price_limit]

        """
        Rank price by the sizes within the time range
        """
        # Add price and time accordingly as header and index
        table_data.append(global_price_limit)
        table_data.append(ranks)
        table_data = list(map(list, zip(*table_data)))
        table_data.insert(0, global_time_limit + ['Price'])

        # Prince Description
        print(f'\n\n{source}      {self.ticker_name}       Spread: {round(ask_price - bid_price, 2)}')

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
