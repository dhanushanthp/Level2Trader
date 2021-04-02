from terminaltables import AsciiTable
import itertools
import json
from numerize.numerize import numerize
from colr import color
import os


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
        data = self.read_data(path)
        # all_sizes = list(itertools.chain.from_iterable([list(i.values()) for i in itertools.chain.from_iterable(data.values())]))
        # block_size = np.mean(all_sizes)
        block_size = 5000

        ticker_times = sorted(data.keys())
        ll = [data[i] for i in ticker_times]

        asks = [i[0] for i in ll]
        bids = [i[0] for i in ll]

        bid_prices = sorted(set(itertools.chain.from_iterable(([list(i.keys()) for i in bids]))))
        ask_prices = sorted(set(itertools.chain.from_iterable(([list(i.keys()) for i in asks]))))
        all_prices = sorted(set(bid_prices + ask_prices), reverse=True)

        table_data = []
        for t in ticker_times:
            # 0 index for bids
            price_on_bids = data[t][0]
            # 1 index for bids
            price_on_asks = data[t][1]

            # Price on ask bullish
            price_size_on_asks = [self.bullish_signals(block_size, price_on_asks[p]) if p in price_on_asks else '' for p in all_prices]
            # Price on bid bearish
            price_size_on_bids = [self.bearish_signals(block_size, price_on_bids[p]) if p in price_on_bids else '' for p in all_prices]
            """
            In actual output ASK sizes will be on top and BID sizes will be in bottom. Since we do the table pivot in later part. 
            We are adding BID front and ASK at back in below logic.
            """
            output = ['\n'.join(x) for x in zip(price_size_on_bids, price_size_on_asks)]
            table_data.append(output)

        table_data.append(all_prices)
        # BID and ASK sizes will be pivot
        table_data = list(map(list, zip(*table_data)))
        table_data.insert(0, ticker_times)

        # Create table instance
        table_instance = AsciiTable(table_data)
        table_instance.inner_heading_row_border = False
        table_instance.inner_row_border = True
        table_instance.inner_column_border = False

        # table_instance.justify_columns = {0: 'center', 1: 'center', 2: 'center', 3: 'center', 4: 'center', 5: 'center', 6: 'center'}
        self.clear()
        print(table_instance.table)
