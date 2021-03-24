import itertools
from terminaltables import AsciiTable
from colorclass import Color
from terminaltables import SingleTable


class BidAsk:
    def __init__(self, ticker, multiple_of_10sec=6, length=6):
        self.bid_time_accumulator = dict()
        self.ask_time_accumulator = dict()
        self.last_x_min = multiple_of_10sec
        self.ticker = ticker
        self.length = length

    def add_space_ask(self, string: str):
        string_length = len(string)
        change = self.length - string_length
        if change > 0:
            return string.ljust(self.length)
        else:
            return string

    def add_space_bid(self, string: str):
        string_length = len(string)
        change = self.length - string_length
        if change > 0:
            return string.rjust(self.length)
        else:
            return string

    def color_size(self, bid: int, ask: int):
        # str_bid = ''
        # str_ask = ''
        # if bid > 8000:
        #     str_bid = Color('{autored}' + self.add_space_bid(str(bid)) + '{/autored}')
        # elif bid > 5000:
        #     str_bid = Color('{autocyan}' + self.add_space_bid(str(bid)) + '{/autocyan}')
        # elif bid > 3000:
        #     str_bid = Color('{autoyellow}' + self.add_space_bid(str(bid)) + '{/autoyellow}')
        # else:
        #     str_bid = Color(self.add_space_bid(str(bid)))

        if bid > 200000:
            str_bid = Color('{autobggreen}{autoblack}' + self.add_space_bid(str(bid)) + '{/autoblack}{/autobggreen}')
        elif bid > 150000:
            str_bid = Color('{autogreen}' + self.add_space_bid(str(bid)) + '{/autogreen}')
        elif bid > 100000:
            str_bid = Color('{autobgblue}' + self.add_space_bid(str(bid)) + '{/autobgblue}')
        elif bid > 50000:
            str_bid = Color('{autoblue}' + self.add_space_bid(str(bid)) + '{/autoblue}')
        elif bid > 25000:
            str_bid = Color('{autocyan}' + self.add_space_bid(str(bid)) + '{/autocyan}')
        elif bid > 10000:
            str_bid = Color('{autoyellow}' + self.add_space_bid(str(bid)) + '{/autoyellow}')
        else:
            str_bid = Color(self.add_space_bid(str(bid)))

        if ask > 200000:
            str_ask = Color('{autobggreen}{autoblack}' + self.add_space_bid(str(ask)) + '{/autoblack}{/autobggreen}')
        elif ask > 150000:
            str_ask = Color('{autogreen}' + self.add_space_bid(str(ask)) + '{/autogreen}')
        elif ask > 100000:
            str_ask = Color('{autobgblue}' + self.add_space_bid(str(ask)) + '{/autobgblue}')
        elif ask > 50000:
            str_ask = Color('{autoblue}' + self.add_space_bid(str(ask)) + '{/autoblue}')
        elif ask > 25000:
            str_ask = Color('{autocyan}' + self.add_space_bid(str(ask)) + '{/autocyan}')
        elif ask > 10000:
            str_ask = Color('{autoyellow}' + self.add_space_bid(str(ask)) + '{/autoyellow}')
        else:
            str_ask = Color(self.add_space_bid(str(ask)))

        return str_bid + ' ➜ ' + str_ask

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
                self.bid_time_accumulator[var_time][bid_price] = self.bid_time_accumulator[var_time][
                                                                     bid_price] + bid_size
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
                self.ask_time_accumulator[var_time][ask_price] = self.ask_time_accumulator[var_time][
                                                                     ask_price] + ask_size
            else:
                self.ask_time_accumulator[var_time][ask_price] = ask_size
        else:
            # Create value dictionary with size
            value_dict = dict()
            value_dict[ask_price] = ask_size
            # Create time dictionary with value
            self.ask_time_accumulator[var_time] = value_dict

        # Call function to generate table
        print(self.data_table_generator() + '\n')

    def data_table_generator(self):
        """
        Visualize the table
        :return: table data
        """
        # Time
        lst_time = sorted(self.bid_time_accumulator.keys())[-self.last_x_min:]
        # value
        bid_lst_price = sorted(
            list((set(itertools.chain.from_iterable([list(self.bid_time_accumulator[i].keys()) for i in lst_time])))))
        ask_lst_price = sorted(
            list((set(itertools.chain.from_iterable([list(self.ask_time_accumulator[i].keys()) for i in lst_time])))))
        lst_price = sorted(list(set(bid_lst_price + ask_lst_price)), reverse=True)

        table_data = []
        for ele_time in lst_time:
            value_data = []
            for ele_price in lst_price:
                # Price from both bid and ask
                if ele_price in self.bid_time_accumulator[ele_time] and \
                        ele_price in self.ask_time_accumulator[ele_time]:
                    value_data.append(
                        self.color_size(self.bid_time_accumulator[ele_time][ele_price],
                                        self.ask_time_accumulator[ele_time][ele_price]))
                # Price exist in BID but Not in ASK
                elif ele_price in self.bid_time_accumulator[ele_time] and \
                        ele_price not in self.ask_time_accumulator[ele_time]:
                    # Add the volume size
                    value_data.append(self.color_size(self.bid_time_accumulator[ele_time][ele_price], 0))
                # Price exist in ASK but Not in BID
                elif ele_price not in self.bid_time_accumulator[ele_time] and \
                        ele_price in self.ask_time_accumulator[ele_time]:
                    # Add the volume size
                    value_data.append(self.color_size(0, self.ask_time_accumulator[ele_time][ele_price]))
                else:
                    value_data.append('')
            table_data.append(value_data)

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
