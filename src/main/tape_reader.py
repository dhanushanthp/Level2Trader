import itertools
from terminaltables import AsciiTable
import numpy as np
from colr import color
from config import Config
import os
from numerize.numerize import numerize
from src.util import time_util
from src.util import size_util
from datetime import datetime
from src.feature_extraction.top_sales_extractor import TopSalesExtractor
from src.feature_extraction.time_and_sales_extractor import TimeSalesExtractor
import operator
import pandas as pd


class TapeReader:
    def __init__(self, ticker, data_writer: bool, time_frequency):
        """
        We don't track the actual price of last price here. rather we find the most close bid and ask price for the last price.
        The goal is to find the price on bid and price on ask for bullish and bearish signals.

        :param ticker:
        :param data_writer:
        """

        # Clear Terminal
        self.clear = lambda: os.system('clear')
        self.clear_counter = 0

        # Ticker by each second, So the size aggregation will be done by seconds
        self.ticker_name = ticker
        self.config = Config()
        self.time_ticks_filter = self.config.get_timesales_timeticks()
        self.time_frequency = time_frequency
        self.DATE = datetime.today().strftime('%Y%m%d%H')

        self.data_writer = data_writer

        # Track previous bid and ask prices.
        self.previous_bid_price = 0
        self.previous_ask_price = 0

        # Track the previous time to print every second
        self.previous_time = None

        self.su = size_util.SizeUtil()
        self.tu = time_util.TimeUtil()
        self.top_se = TopSalesExtractor()
        self.time_se = TimeSalesExtractor()

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

        # Top Sales Extraction
        self.top_se.extract_top_sales(tick_time, ask_price, ask_size, bid_price, bid_size, closest_price, last_size)

        # Time and Sales Extraction
        self.time_se.extract_time_and_sales(ask_price, bid_price, closest_price, last_size, tick_time)

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

        source = self.config.get_bid_ask_source_name()

        # Write data to file
        if self.data_writer:
            with open(f'data/test_data/{self.DATE}_{self.ticker_name}.csv', 'a') as file_writer:
                file_writer.write(f'{tick_time},{bid_price},{bid_size},{ask_price},{ask_size},{last_price},{last_size},{source}\n')

        tick_time_split = tick_time.split(":")
        tick_time = ':'.join(tick_time_split[:-1]) + ':' + self.tu.round_time(int(tick_time_split[-1]), base=self.time_frequency)

        if self.previous_time is None:
            # Set current time as previous time if it's none
            self.previous_time = tick_time

        # Find the closest price w.r.t to last price on bid or ask
        closest_price = self.su.find_closest(bid_price, ask_price, last_price)

        # Don't initiate the print until we get the api call in last to update the dictionary
        if (bool(self.top_se.top_sales_on_ask)) and (bool(self.top_se.top_sales_on_bid)) and (
                self.previous_time != tick_time):
            self.clear()
            print(self.display_data(closest_price, bid_price, ask_price, 'B&A'))
            self.previous_time = tick_time

        # Update the level II bid and ask with sizes
        self.data_dictionary_generator(tick_time, bid_price, bid_size, ask_price, ask_size, closest_price, last_size)

    def time_sales_api_call(self, tick_time: str, bid_price, bid_size, ask_price, ask_size, last_price, last_size, exchange):
        """
        Update table when time and sales api trigger every tick
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
        source = self.config.get_time_sales_source_name()

        # Write data to file
        if self.data_writer:
            with open(f'data/test_data/{self.DATE}_{self.ticker_name}.csv', 'a') as file_writer:
                file_writer.write(f'{tick_time},{bid_price},{bid_size},{ask_price},{ask_size},{last_price},{last_size},{source}\n')

        tick_time_split = tick_time.split(":")
        tick_time = ':'.join(tick_time_split[:-1]) + ':' + self.tu.round_time(int(tick_time_split[-1]), base=self.time_frequency)

        if self.previous_time is None:
            self.previous_time = tick_time

        # Find the closest price w.r.t to last price on bid or ask
        closest_price = self.su.find_closest(bid_price, ask_price, last_price)

        if self.previous_time != tick_time:
            self.clear()
            # This function needs to be triggered before calling data dictionary generator to avoid the next time tick partial call
            print(self.display_data(closest_price, bid_price, ask_price, 'T&S'))
            self.previous_time = tick_time

        self.data_dictionary_generator(tick_time, bid_price, bid_size, ask_price, ask_size, closest_price, last_size)

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

    def generate_all_time_highs(self, global_price_limit):

        # bid = {i: self.top_se.all_time_high_on_bid[i] for i in global_price_limit if i in self.top_se.all_time_high_on_bid}
        # ask = {i: self.top_se.all_time_high_on_ask[i] for i in global_price_limit if i in self.top_se.all_time_high_on_ask}
        bid = self.top_se.all_time_high_on_bid
        ask = self.top_se.all_time_high_on_ask

        bid = pd.DataFrame(bid.items(), columns=['price', 'bid'])
        ask = pd.DataFrame(ask.items(), columns=['price', 'ask'])

        combined = bid.merge(ask, on=['price'], how='outer')
        combined.fillna(0, inplace=True)

        now = datetime.now()
        minu, sec = [int(i) for i in now.strftime('%M:%S').split(':')]
        # Reset chart data for every 1 min
        if (minu % 1 == 0 and sec in [58, 59]) or (len(self.top_se.all_time_high_on_bid) > 12):
            self.top_se.all_time_high_on_bid = dict()
            self.top_se.all_time_high_on_ask = dict()

        combined.to_csv('data/real_time_data_output/all_time_high.csv', index=False)

    def generate_all_time_total(self, global_price_limit):

        # bid = {i: self.time_se.all_time_sales_bid[i] for i in global_price_limit if i in self.time_se.all_time_sales_bid}
        # ask = {i: self.time_se.all_time_sales_ask[i] for i in global_price_limit if i in self.time_se.all_time_sales_ask}

        bid = self.time_se.all_time_sales_bid
        ask = self.time_se.all_time_sales_ask

        bid = pd.DataFrame(bid.items(), columns=['price', 'bid'])
        ask = pd.DataFrame(ask.items(), columns=['price', 'ask'])

        combined = bid.merge(ask, on=['price'], how='outer')
        combined.fillna(0, inplace=True)

        combined['bid_rank'] = combined['bid'].rank(ascending=False).astype(int)
        combined['ask_rank'] = combined['ask'].rank(ascending=False).astype(int)

        now = datetime.now()
        minu, sec = [int(i) for i in now.strftime('%M:%S').split(':')]
        # Reset chart data for every 1 min
        if (minu % 1 == 0 and sec in [58, 59]) or (len(self.time_se.all_time_sales_bid) > 12):
            self.time_se.all_time_sales_bid = dict()
            self.time_se.all_time_sales_ask = dict()

        combined.to_csv('data/real_time_data_output/all_time_sales.csv', index=False)

    def top_on_sales_pre_display_data(self):
        """
        Prepare data for pre display for top sales
        :return:
        """
        # Limit the moving time to bid and ask ranges
        global_time_limit = sorted(
            set(list(self.top_se.top_sales_on_bid.keys()) + list(self.top_se.top_sales_on_ask.keys())))[
                            -self.time_ticks_filter:]

        # All the prices on bid within the time limit and reverse high to low
        top_on_bid_price_list = sorted(
            list((set(itertools.chain.from_iterable([list(self.top_se.top_sales_on_bid[i].keys()) for i in global_time_limit])))),
            reverse=True)

        # All the prices on ask within the time limit and reverse low to high
        top_on_ask_price_list = sorted(
            list((set(itertools.chain.from_iterable([list(self.top_se.top_sales_on_ask[i].keys()) for i in global_time_limit])))),
            reverse=True)

        # All the sizes on ask within the time limit and and sorted
        top_on_ask_size_list = sorted(
            set(itertools.chain.from_iterable([self.top_se.top_sales_on_ask[i].values() for i in global_time_limit])))

        # All the sizes on ask within the time limit and and sorted
        top_on_bid_size_list = sorted(
            set(itertools.chain.from_iterable([self.top_se.top_sales_on_bid[i].values() for i in global_time_limit])))

        # List of dictionaries
        top_on_bid_price_size_list_of_dictionaries = [self.top_se.top_sales_on_bid[i] for i in global_time_limit]
        top_on_ask_price_size_list_of_dictionaries = [self.top_se.top_sales_on_ask[i] for i in global_time_limit]

        # Balance the price range
        global_price_limit = sorted(set(top_on_bid_price_list + top_on_ask_price_list), reverse=True)
        total_sizes = np.sum(top_on_ask_size_list + top_on_bid_size_list)
        top_on_bid_rank = self.calculate_ranks(top_on_bid_price_size_list_of_dictionaries, global_price_limit)
        top_on_ask_rank = self.calculate_ranks(top_on_ask_price_size_list_of_dictionaries, global_price_limit)

        # Highlight by colour
        top_on_bid_rank = [color(i, fore=(255, 0, 0), back=(0, 0, 0)) if i != '' else '' for i in top_on_bid_rank]
        top_on_ask_rank = [color(i, fore=(0, 255, 0), back=(0, 0, 0)) if i != '' else '' for i in top_on_ask_rank]

        # Combine the ranks
        ranks_output = ['\n'.join(x) for x in zip(top_on_ask_rank, top_on_bid_rank)]

        # Generate all time highs as files
        self.generate_all_time_highs(global_price_limit)

        return global_price_limit, global_time_limit, ranks_output, total_sizes

    def time_and_sales_pre_display_data(self, global_time_limit, global_price_limit):

        # Generate list of dictionaries
        sales_on_bid = {i: self.time_se.dict_last_size_on_bid[i] for i in global_time_limit}
        sales_on_ask = {i: self.time_se.dict_last_size_on_ask[i] for i in global_time_limit}

        # Generate list of tuples
        sales_on_bid = list(itertools.chain.from_iterable([zip(list(i.keys()), list(i.values())) for i in sales_on_bid.values()]))
        sales_on_ask = list(itertools.chain.from_iterable([zip(list(i.keys()), list(i.values())) for i in sales_on_ask.values()]))

        # Data frame creation
        sales_on_bid = pd.DataFrame(sales_on_bid, columns=['price', 'bid']).groupby(['price'])['bid'].sum().reset_index()
        sales_on_ask = pd.DataFrame(sales_on_ask, columns=['price', 'ask']).groupby(['price'])['ask'].sum().reset_index()

        # Combine data
        time_and_sales_df = sales_on_bid.merge(sales_on_ask, on=['price'], how='outer')
        time_and_sales_df['total'] = time_and_sales_df['bid'] + time_and_sales_df['ask']

        # Generate rank by sum of sales
        time_and_sales_df['total_rank'] = time_and_sales_df['total'].rank(ascending=False).astype(int)
        time_and_sales_df['bid'] = round((time_and_sales_df['bid'] / time_and_sales_df['total']) * 100)
        time_and_sales_df['ask'] = round((time_and_sales_df['ask'] / time_and_sales_df['total']) * 100)

        # Fill missing values with 0
        time_and_sales_df = time_and_sales_df.fillna(0)
        time_and_sales_df['total'] = time_and_sales_df['total'].apply(lambda x: numerize(x))

        # Generated decorated percentage output
        def percentage_output_deco(x):
            output = color(f"{round(x['ask'])}%" if x['ask'] != 0 else '', fore=(0, 255, 0), back=(0, 0, 0)) if x['ask'] > x[
                'bid'] else '\n' + color(f"{round(x['bid'])}%",
                                         fore=(255, 0, 0),
                                         back=(0, 0, 0)) if x['bid'] != 0 else ''

            return output

        time_and_sales_df['percentage_output'] = time_and_sales_df.apply(lambda x: percentage_output_deco(x), axis=1)

        # Highlight the total output w.r.t the Total percentage on bid/ask
        # TODO Set the position up for ask down for bid based on the percentage distribution. Currently it's just compare total size
        def total_sales_deco(x):
            output = (color(x['total'], fore=(0, 255, 0), back=(0, 0, 0)) if x['ask'] > x['bid'] else '\n' + color(x['total'], fore=(255, 0, 0),
                                                                                                                   back=(0, 0, 0))
                      ) if (x['total_rank'] == 1) else x['total']

            return output

        # Total sales within price range
        time_and_sales_df['total'] = time_and_sales_df.apply(lambda x: total_sales_deco(x), axis=1)
        total_sales_output = dict(zip(time_and_sales_df['price'], time_and_sales_df['total']))
        total_sales_output = [total_sales_output[i] if i in total_sales_output else '' for i in global_price_limit]

        # Percentage Output
        percentage_output = dict(zip(time_and_sales_df['price'], time_and_sales_df['percentage_output']))
        percentage_output = [percentage_output[i] if i in percentage_output else '' for i in global_price_limit]

        # Rank by total sales
        rank_total = time_and_sales_df[time_and_sales_df['total_rank'] < 4]
        rank_by_total_sales = dict(zip(rank_total['price'], rank_total['total_rank']))
        rank_by_total_sales = [rank_by_total_sales[i] if i in rank_by_total_sales else '' for i in global_price_limit]

        # Generate all time highs on total sales
        self.generate_all_time_total(global_price_limit)

        return rank_by_total_sales, percentage_output, total_sales_output

    def display_data(self, closest_price: float, bid_price: float, ask_price: float, source: str):
        """
        Generate table for terminal outputs

        :param closest_price: The price closest to bid or ask w.r.t last price. Which may not be an actual last price
        :param bid_price: bid price, level II first tier only
        :param ask_price: ask price, level II first tier only
        :param source: API call source
        :return: table for terminal visualisation
        """

        # Top sales pre data prep
        global_price_limit, global_time_limit, ranks_output, total_sizes = self.top_on_sales_pre_display_data()

        # Time and sales pre data prep
        ranks_by_total_sales, dist_of_total_sales_on_bid_vs_ask, sum_total_sales = self.time_and_sales_pre_display_data(global_time_limit,
                                                                                                                        global_price_limit)

        """
        Generate data for the table with high sales on bid and ask within given time frame. 
        """
        table_data = []
        for current_time in global_time_limit:
            value_data = []
            for current_price in global_price_limit:
                # Price both bid and ask
                if current_price in self.top_se.top_sales_on_bid[current_time] and current_price in \
                        self.top_se.top_sales_on_ask[current_time]:

                    # Select sizes for each price and time
                    last_bid_size = self.top_se.top_sales_on_bid[current_time][current_price]
                    last_bid_size = numerize(last_bid_size) + ' ' + round((last_bid_size / total_sizes) * 10) * \
                                    color('↓', fore=(255, 0, 0), back=(0, 0, 0)) if last_bid_size != 0 else ' '

                    last_ask_size = self.top_se.top_sales_on_ask[current_time][current_price]
                    last_ask_size = numerize(last_ask_size) + ' ' + round((last_ask_size / total_sizes) * 10) * \
                                    color('↑', fore=(0, 255, 0), back=(0, 0, 0)) if last_ask_size != 0 else ' '

                    normal_transaction = color(last_ask_size, fore=(0, 255, 0), back=(0, 0, 0)) + '\n' + color(last_bid_size, fore=(255, 0, 0),
                                                                                                               back=(0, 0, 0))
                    value_data.append(normal_transaction)

                # Price exist in BID but Not in ASK
                elif current_price in self.top_se.top_sales_on_bid[current_time] and current_price not in \
                        self.top_se.top_sales_on_ask[current_time]:

                    # Add the volume size
                    last_bid_size = self.top_se.top_sales_on_bid[current_time][current_price]
                    value_data.append(
                        '\n' + color(numerize(last_bid_size),
                                     fore=(255, 0, 0),
                                     back=(0, 0, 0)) + ' ' + round((last_bid_size / total_sizes) * 10) * color('↓',
                                                                                                               fore=(255, 0, 0),
                                                                                                               back=(0, 0, 0)))

                # Price exist in ASK but Not in BID
                elif current_price not in self.top_se.top_sales_on_bid[current_time] and current_price in \
                        self.top_se.top_sales_on_ask[current_time]:
                    # Add the volume size
                    last_ask_size = self.top_se.top_sales_on_ask[current_time][current_price]
                    value_data.append(
                        color(numerize(last_ask_size), fore=(0, 255, 0),
                              back=(0, 0, 0)) + ' ' + round((last_ask_size / total_sizes) * 10) * color('↑', fore=(0, 255, 0),
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
        latest_size_on_price_ask = self.top_se.top_sales_on_ask[latest_time_stamp]
        latest_size_on_price_bid = self.top_se.top_sales_on_bid[latest_time_stamp]
        indicator_top_ask_size_price = str(max(latest_size_on_price_ask.items(), key=operator.itemgetter(1))[0])
        indicator_top_bid_size_price = str(max(latest_size_on_price_bid.items(), key=operator.itemgetter(1))[0])

        if indicator_top_bid_size_price == indicator_top_ask_size_price:
            # When both price at their top
            global_price_limit = [color(i, fore=(0, 0, 0), back=(0, 255, 0)) + '\n' + color(i, fore=(255, 255, 255), back=(
                255, 0, 0)) if i == indicator_top_ask_size_price else i for i in
                                  global_price_limit]
        else:
            global_price_limit = [color(i, fore=(0, 0, 0), back=(0, 255, 0)) + '\n' if i == indicator_top_ask_size_price else i for i in
                                  global_price_limit]
            global_price_limit = ['\n' + color(i, fore=(255, 255, 255), back=(255, 0, 0)) if i == indicator_top_bid_size_price else i for i in
                                  global_price_limit]

        """
        Rank price by the sizes within the time range
        """
        # Add price and time accordingly as header and index
        table_data.append(global_price_limit)
        table_data.append(ranks_output)
        table_data.append(ranks_by_total_sales)
        table_data.append(sum_total_sales)
        table_data.append(dist_of_total_sales_on_bid_vs_ask)
        table_data = list(map(list, zip(*table_data)))
        table_data.insert(0, global_time_limit + ['Price', 'Top S. R.', 'Total S. R.', 'Total S.', 'T. %'])

        # Prince Description
        print(
            f'{source}      {self.ticker_name}       Spread: {round(ask_price - bid_price, 2)}        Timeframe:{self.time_frequency}sec')

        # Create table instance
        table_instance = AsciiTable(table_data)
        table_instance.inner_heading_row_border = False
        table_instance.inner_row_border = True
        table_instance.inner_column_border = False

        # Align text for price column
        time_length = len(global_time_limit)
        # Default alignment is on left
        table_instance.justify_columns = {time_length: 'center', time_length + 1: 'center', time_length + 2: 'center', time_length + 3: 'center',
                                          time_length + 4: 'center'}
        return table_instance.table
