def level_one_current_bids_asks(self, ask_price, ask_size, bid_price, bid_size, tick_time):
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
            # If match, update the size
            self.dict_bid_size_on_bid[tick_time][bid_price] = bid_size
        else:
            if self.previous_bid_price != 0:
                # If the previous price is not holding the bid
                self.dict_bid_size_on_bid[tick_time][self.previous_bid_price] = 0
    else:
        # Current new bid price and size
        self.dict_bid_size_on_bid[tick_time] = {bid_price: bid_size}

    # Set current bid price for the next iteration as previous bid price
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

    # Set current ask price for the next iteration as previous ask price
    self.previous_ask_price = ask_price