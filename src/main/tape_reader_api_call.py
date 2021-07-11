from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.client import TickAttribLast, TickerId, TickAttribBidAsk
import sys
import datetime
from src.main.tape_reader import TapeReader
from config import Config


class IBapi(EWrapper, EClient):
    def __init__(self, ticker):
        """
        The table will be updated with time and sales last function and level II bid and ask function. Since the functions are asynchronous calls
        we need to update values in both places with the same object.

        The values will be pushed to objects using functions.
        :param ticker:
        """
        EClient.__init__(self, self)
        config = Config()
        self.ibapi_ref = TapeReader(ticker=ticker, data_writer=config.get_can_write_data(), time_frequency=config.get_time_frequency())
        self.data = []  # Initialize variable to store candle
        self.bid = 0
        self.ask = 0
        self.bid_size = 0
        self.ask_size = 0
        self.last = 0

    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        print(f"{reqId}, {errorCode}, {errorString}")

    def tickByTickAllLast(self, reqId: int, tickType: int, ticktime: int, price: float, size: int, tickAtrribLast: TickAttribLast, exchange: str,
                          specialConditions: str):
        """
        Load the ticker All last Data. The values from API will be pushed to relevant objects
        :param reqId:
        :param tickType:
        :param ticktime:
        :param price:
        :param size:
        :param tickAtrribLast:
        :param exchange:
        :param specialConditions:
        :return:
        """
        super().tickByTickAllLast(reqId, tickType, ticktime, price, size, tickAtrribLast, exchange, specialConditions)
        self.last = price

        if tickType == 1:
            """
            Cases to tackle
            1. last function get called before bid and ask
            2. At the same time the level II data is not available
            """
            # TODO add the level II time stamp in below condition, If both time stamp match then process data
            if (self.bid != 0) and (self.ask != 0):
                self.ibapi_ref.time_sales_api_call(datetime.datetime.fromtimestamp(ticktime).strftime("%H:%M:%S"), self.bid, self.bid_size,
                                                   self.ask, self.ask_size, price, size, exchange)

    def tickByTickBidAsk(self, reqId: int, ticktime: int, bidPrice: float, askPrice: float, bidSize: int, askSize: int,
                         tickAttribBidAsk: TickAttribBidAsk):
        """
        Update the bid and ask price when ever the function triggered.  The values from API will be pushed to relevant objects
        :param reqId:
        :param ticktime:
        :param bidPrice:
        :param askPrice:
        :param bidSize:
        :param askSize:
        :param tickAttribBidAsk:
        :return:
        """

        super().tickByTickBidAsk(reqId, ticktime, bidPrice, askPrice, bidSize, askSize, tickAttribBidAsk)
        """
        Update bid and ask, Since the bid and ask is not a frequent call. we need to keep the bid and ask in class
        level and update when ever the bid and ask api triggered.
        """
        self.bid = bidPrice
        self.ask = askPrice
        self.bid_size = bidSize
        self.ask_size = askSize

        """
        Cases to tackle
        1. bid and ask function get called before last
        2. At the same time the time and sales data is not available
        3. The last size will be 0. Because at level II update the time and sales won't get updated
        """
        if self.last != 0:
            self.ibapi_ref.level_ii_api_call(datetime.datetime.fromtimestamp(ticktime).strftime("%H:%M:%S"), self.bid, self.bid_size,
                                             self.ask, self.ask_size, self.last, 0)


def main():
    ticker = str(sys.argv[1]).upper()
    app = IBapi(ticker)
    config = Config()
    app.connect(host='127.0.0.1', port=config.get_port_number(), clientId=19879)

    # Create contract object
    contract = Contract()
    contract.symbol = ticker
    contract.secType = 'STK'
    contract.exchange = 'SMART'
    contract.currency = 'USD'
    contract.primaryExchange = 'NASDAQ'

    # Request historical candles
    app.reqTickByTickData(reqId=1008, contract=contract, tickType="BidAsk", numberOfTicks=0, ignoreSize=True)

    # Request historical candles
    app.reqTickByTickData(reqId=1009, contract=contract, tickType="Last", numberOfTicks=0, ignoreSize=True)
    # app.disconnect()
    # app.cancelTickByTickData(1008)
    app.run()


main()
