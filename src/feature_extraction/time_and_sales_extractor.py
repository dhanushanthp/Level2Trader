class TimeSalesExtractor:
    def __init__(self):
        # Price and size w.r.t BID and last, Bearish signal
        self.dict_last_size_on_bid = dict()

        # Price and size w.r.t ASK and last, Bullish signal
        self.dict_last_size_on_ask = dict()

    def extract_time_and_sales(self, ask_price, bid_price, closest_price, last_size, tick_time):
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
