import itertools
from terminaltables import AsciiTable
from colorclass import Color


class TimeAndSales:
    def __init__(self, ticker, multiple_of_10sec=6):
        self.time_accumulator = dict()
        self.last_x_min = multiple_of_10sec
        self.ticker = ticker

    @staticmethod
    def color_size(size: int):
        """

        :param size:
        :return:
        """

        if size > 20000:
            return Color('{autobggreen}{autoblack}' + str(size) + '{/autoblack}{/autobggreen}')
        elif size > 15000:
            return Color('{autogreen}' + str(size) + '{/autogreen}')
        elif size > 10000:
            return Color('{autobgblue}' + str(size) + '{/autobgblue}')
        elif size > 5000:
            return Color('{autoblue}' + str(size) + '{/autoblue}')
        elif size > 3000:
            return Color('{autoyellow}' + str(size) + '{/autoyellow}')
        else:
            return Color(str(size))

    def data_generator(self, var_time: str, var_value: float, var_size: int, var_exchange: str):
        """

        :param var_time:
        :param var_value:
        :param var_size:
        :param var_exchange:
        :return:
        """

        # Adjust for 10 sec
        var_time = var_time[:-1]

        """
        time accumulator dictionary is a dictionary of dictionary data structure. 
        Dictionary: Key: Time, value: Dictionary(key: price, value: size)
        The value will be updated through the iteration process by finding time and price accordingly
        """
        if var_time in self.time_accumulator:
            # If time already exist in dictionary
            if var_value in self.time_accumulator[var_time]:
                # Get the value dictionary by time and price and update the size
                self.time_accumulator[var_time][var_value] = self.time_accumulator[var_time][var_value] + var_size
            else:
                # Time exist but the price is not exist, create a element with price and size
                self.time_accumulator[var_time][var_value] = var_size

        else:
            # New element creation with time, price and size
            # Create value dictionary with size
            value_dict = dict()
            value_dict[var_value] = var_size
            # Create time dictionary with value
            self.time_accumulator[var_time] = value_dict

        # Call function to generate table
        print(self.data_table_generator() + '\n')

    def data_table_generator(self):
        """
        Visualize the table
        :return: table data
        """
        # Time, select the range of few minutes of data
        lst_time = sorted(self.time_accumulator.keys())[-self.last_x_min:]
        # reversed price. Low to High
        lst_price = sorted(
            list((set(itertools.chain.from_iterable([list(self.time_accumulator[i].keys()) for i in lst_time])))),
            reverse=True)

        table_data = []
        for ele_time in lst_time:
            value_data = []
            for ele_price in lst_price:
                if ele_price in self.time_accumulator[ele_time]:
                    # Add the volume size
                    value_data.append(self.color_size(self.time_accumulator[ele_time][ele_price]))
                else:
                    value_data.append('')
            table_data.append(value_data)

        # Add price and time accordingly as header and index
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
