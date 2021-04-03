from terminaltables import AsciiTable
import itertools
import json
from numerize.numerize import numerize
from colr import color
import numpy as np
import os
import operator


class TopSalesTracker:

    def __init__(self):
        # Clear Terminal
        self.clear = lambda: os.system('clear')
        self.clear_counter = 0

    @staticmethod
    def read_data(path):
        """
        Read JSON file
        :return:
        """
        with open(path) as f:
            data = json.load(f)

        return data

    @staticmethod
    def latest_top_sales(data, time_range):
        # Pick the latest timestamp and the bid and ask dictionary
        last_time_stamp = time_range[-1]
        top_ask_on_latest = max(data[last_time_stamp][0].items(), key=operator.itemgetter(1))[0]
        top_bid_on_latest = max(data[last_time_stamp][1].items(), key=operator.itemgetter(1))[0]
        return top_ask_on_latest, top_bid_on_latest

    @staticmethod
    def calculate_ranks(dict_prices, all_prices):
        """
        Calculate and rank the top size levels w.r.t last n minutes. Currently its set as 10 minutes and rank top 3
        :param dict_prices: Dictionary of prices with size
        :param all_prices: All the prices in valid range
        :return:
        """
        # Tuple of price list generated from list of price and size dictionary, Converted the dictionary to tuple
        tuple_lst_price_size = list(itertools.chain.from_iterable([list(zip(list(i.keys()), list(i.values()))) for i in dict_prices]))
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

    @staticmethod
    def bearish_signals(block_size, actual_size):
        num_of_clicks = round(actual_size / block_size)
        num_of_clicks = color(numerize(actual_size), fore=(0, 255, 0), back=(0, 0, 0)) + ' ' + num_of_clicks * color('↑', fore=(0, 255, 0),
                                                                                                                     back=(0, 0, 0))
        return num_of_clicks

    @staticmethod
    def bullish_signals(block_size, actual_size):
        num_of_clicks = round(actual_size / block_size)
        num_of_clicks = color(numerize(actual_size), fore=(255, 0, 0), back=(0, 0, 0)) + ' ' + num_of_clicks * color('↓', fore=(255, 0, 0),
                                                                                                                     back=(0, 0, 0))
        return num_of_clicks

    def generate_terminal_data(self, path):
        top_sales_data = self.read_data(path)
        # all_sizes = list(itertools.chain.from_iterable([list(i.values()) for i in itertools.chain.from_iterable(data.values())]))
        # block_size = np.mean(all_sizes)
        block_size = 5000

        ticker_times = sorted(top_sales_data.keys())
        price_and_sizes = [top_sales_data[i] for i in ticker_times]

        # Ask prices dictionary
        dict_ask_price = [i[0] for i in price_and_sizes]
        # Bid prices dictionary
        dict_bid_price = [i[1] for i in price_and_sizes]

        ask_prices = sorted(set(itertools.chain.from_iterable(([list(i.keys()) for i in dict_ask_price]))))
        bid_prices = sorted(set(itertools.chain.from_iterable(([list(i.keys()) for i in dict_bid_price]))))
        all_prices = sorted(set(bid_prices + ask_prices), reverse=True)

        """
        Rank size based on High to low.
        """
        # Identify the ranks of top sales
        bid_rank = self.calculate_ranks(dict_bid_price, all_prices)
        ask_rank = self.calculate_ranks(dict_ask_price, all_prices)

        # Highlight by colour
        bid_rank = [color(i, fore=(255, 0, 0), back=(0, 0, 0)) if i != '' else '' for i in bid_rank]
        ask_rank = [color(i, fore=(0, 255, 0), back=(0, 0, 0)) if i != '' else '' for i in ask_rank]

        # Combine the ranks
        ranks = ['\n'.join(x) for x in zip(ask_rank, bid_rank)]

        # Top ask and bid prices w.r.t size from last timeframe
        latest_top_ask, latest_top_bid = self.latest_top_sales(top_sales_data, ticker_times)

        """
        Identify the latest top size on sale w.r.t bid and ask
        """
        table_data = []
        for t in ticker_times:
            # 0 index for bids
            price_on_bids = top_sales_data[t][0]
            # 1 index for bids
            price_on_asks = top_sales_data[t][1]
            # Price on ask bullish
            price_size_on_asks = [self.bullish_signals(block_size, price_on_asks[p]) if p in price_on_asks else '' for p in all_prices]
            # Price on bid bearish
            price_size_on_bids = [self.bearish_signals(block_size, price_on_bids[p]) if p in price_on_bids else '' for p in all_prices]
            """
            In actual output, ASK sizes will be on top and BID sizes will be in bottom. Since we do the table pivot in later part. 
            We are adding BID front and ASK at back in below logic.
            """
            terminal_output = ['\n'.join(x) for x in zip(price_size_on_bids, price_size_on_asks)]
            table_data.append(terminal_output)

        # If sale on bid and ask is high on last time frame
        common_price = np.intersect1d(latest_top_ask, latest_top_bid)

        if len(common_price) > 0:
            common_price = common_price[0]
            all_prices = [color(i, fore=(0, 0, 0), back=(255,255,0)) if i == common_price else i for i in all_prices]
        else:
            all_prices = [color(i, fore=(0, 0, 0), back=(0, 255, 0)) + '\n' if i == latest_top_ask else i for i in all_prices]
            all_prices = ['\n' + color(i, fore=(255, 255, 255), back=(255, 0, 0)) if i == latest_top_bid else i for i in all_prices]

        table_data.append(all_prices)
        table_data.append(ranks)
        # BID and ASK sizes will be pivot
        table_data = list(map(list, zip(*table_data)))
        table_data.insert(0, ticker_times + ['Price', 'Ranks'])

        # Create table instance
        table_instance = AsciiTable(table_data)
        table_instance.inner_heading_row_border = False
        table_instance.inner_row_border = True
        table_instance.inner_column_border = False

        self.clear()
        print(table_instance.table)
