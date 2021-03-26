from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.client import TickAttribLast, TickerId, TickAttribBidAsk
import sys
import datetime
from tape_reading.tape_reader import TapeReader


class IBapi(EWrapper, EClient):
    def __init__(self, ticker):
        EClient.__init__(self, self)
        self.time_and_sales = TapeReader(ticker=ticker)
        self.data = []  # Initialize variable to store candle
        self.bid = None
        self.ask = None
        self.bid_size = None
        self.ask_size = None

    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        print(f"{reqId}, {errorCode}, {errorString}")

    def tickByTickAllLast(self, reqId: int, tickType: int, ticktime: int, price: float, size: int, tickAtrribLast: TickAttribLast, exchange: str,
                          specialConditions: str):
        """
        Load the ticker All last Data
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

        if tickType == 1:
            # Once the level II is available
            if self.bid:
                self.time_and_sales.data_generator(datetime.datetime.fromtimestamp(ticktime).strftime("%H:%M:%S"), self.bid, self.bid_size, self.ask,
                                                   self.ask_size, price, size)

    def tickByTickBidAsk(self, reqId: int, time: int, bidPrice: float, askPrice: float, bidSize: int, askSize: int,
                         tickAttribBidAsk: TickAttribBidAsk):
        """
        Update the bid and ask price when ever the function triggered
        :param reqId:
        :param time:
        :param bidPrice:
        :param askPrice:
        :param bidSize:
        :param askSize:
        :param tickAttribBidAsk:
        :return:
        """

        super().tickByTickBidAsk(reqId, time, bidPrice, askPrice, bidSize, askSize, tickAttribBidAsk)
        """
        Update bid and ask, Since the bid and ask is not a frequent call. we need to keep the bid and ask in class
        level and update when ever the bid and ask api triggered.
        """
        self.bid = bidPrice
        self.ask = askPrice
        self.bid_size = bidSize
        self.ask_size = askSize


def main():
    ticker = str(sys.argv[1]).upper()
    app = IBapi(ticker)
    app.connect(host='127.0.0.1', port=7497, clientId=19879)

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
