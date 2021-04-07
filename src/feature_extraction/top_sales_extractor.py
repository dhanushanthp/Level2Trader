from src.util import price_util


class TopSalesExtractor:
    def __init__(self):
        # Most high price on ask, Bullish within the price range
        self.top_sales_on_ask = dict()

        # Most hit price on bids, Bearish within the price range
        self.top_sales_on_bid = dict()

        self.pu = price_util.PriceUtil()

    def generate_top_sales(self, tick_time, ask_price, ask_size, bid_price, bid_size, closest_price, last_size):
        """
        Identification of top sales(sizes) in BID and ASK by time. If the time iterate by seconds then this function will find the top sizes on bid
        and ask in seconds. Also note than we receive more than 1 api calls within a second

        The API calls from level 1 bid & ask and time and sales won't impact the below process. Since we don't do any aggregation over time.

        :param tick_time: Time of ticker
        :param ask_price: ask price, level I current ask price
        :param ask_size
        :param bid_price: bid price, level I current bid price
        :param bid_size
        :param closest_price: price close to bid or ask
        :param last_size: last size, time & sales
        :return:
        """

        if bid_price == ask_price:
            """
            When the bid price is same as ask price. we need to make a decision to assign one of the sides. Bid or ask
            So the bid size and ask size will be used to decide the sides. Where If bid size is higher than ask price then the sales on bid and vice
            versa
            """
            if bid_size > ask_size:
                self.top_bid_updater(ask_price, bid_price, closest_price, last_size, tick_time)
            elif bid_size < ask_size:
                self.top_ask_updater(ask_price, bid_price, closest_price, last_size, tick_time)
            else:
                raise Exception('Bid and ask sizes are same while the prices also same')
        else:
            self.top_bid_updater(ask_price, bid_price, closest_price, last_size, tick_time)

            self.top_ask_updater(ask_price, bid_price, closest_price, last_size, tick_time)

    def top_ask_updater(self, ask_price, bid_price, closest_price, last_size, tick_time):
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

    def top_bid_updater(self, ask_price, bid_price, closest_price, last_size, tick_time):
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
