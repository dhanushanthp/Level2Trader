from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.client import TickAttribLast, TickAttribBidAsk, TickerId
import datetime
import threading


class IBapi(EWrapper, EClient):
    """
    Read time and sales for visualization
    https://www.youtube.com/watch?v=aSdi667LGp0

    https://interactivebrokers.github.io/tws-api/tick_data.html

    Parameters
    reqId	- unique identifier of the request
    tickType	- tick-by-tick real-time tick type: "Last" or "AllLast"
    time	- tick-by-tick real-time tick timestamp
    price	- tick-by-tick real-time tick last price
    size	- tick-by-tick real-time tick last size
    tickAttribLast	- tick-by-tick real-time last tick attribs (bit 0 - past limit, bit 1 - unreported)
    exchange	- tick-by-tick real-time tick exchange
    specialConditions	- tick-by-tick real-time tick special conditions


    self.reqTickByTickData(19001, ContractSamples.EuropeanStock2(), "Last", 0, True)
    self.reqTickByTickData(19002, ContractSamples.EuropeanStock2(), "AllLast", 0, False)
    self.reqTickByTickData(19003, ContractSamples.EuropeanStock2(), "BidAsk", 0, True)
    self.reqTickByTickData(19004, ContractSamples.EurGbpFx(), "MidPoint", 0, False)


    https://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EWrapper.html#a2c817ab5a7e907dbdd5d646f17512b66


    """

    def __init__(self):
        EClient.__init__(self, self)
        self.data = []  # Initialize variable to store candle

    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        print(f"WARNING: {reqId}, {errorCode}, {errorString}")

    def tickByTickAllLast(self, reqId: int,
                          tickType: int,
                          ticktime: int,
                          price: float,
                          size: int,
                          tickAtrribLast: TickAttribLast,
                          exchange: str,
                          specialConditions: str):
        super().tickByTickAllLast(reqId, tickType, ticktime, price, size, tickAtrribLast, exchange, specialConditions)

        if tickType == 1:
            print("Last.", end='')
        else:
            print("AllLast.", end='')

        print(" ReqId:", reqId, "Time:", datetime.datetime.fromtimestamp(ticktime).strftime("%Y%m%d %H:%M:%S"),
              "PriceUtil:",
              price, "Size:", size, "Exch:", exchange, "Spec Cond:", specialConditions, "PastLimit:",
              tickAtrribLast.pastLimit, "Unreported:",
              tickAtrribLast.unreported)

    def tickByTickBidAsk(self, reqId: int, time: int, bidPrice: float, askPrice: float,
                         bidSize: int, askSize: int, tickAttribBidAsk: TickAttribBidAsk):

        super().tickByTickBidAsk(reqId, time, bidPrice, askPrice, bidSize,

                                 askSize, tickAttribBidAsk)

        print("BidAsk. ReqId:", reqId, "Time:", datetime.datetime.fromtimestamp(time).strftime("%Y%m%d %H:%M:%S"),
              "BidPrice:", bidPrice, "AskPrice:", askPrice, "BidSize:", bidSize,
              "AskSize:", askSize, "BidPastLow:", tickAttribBidAsk.bidPastLow, "AskPastHigh:",
              tickAttribBidAsk.askPastHigh)


if __name__ == '__main__':
    app = IBapi()
    app.connect('127.0.0.1', 7497, 0)

    # Create contract object
    contract = Contract()
    contract.symbol = 'NEOS'
    contract.secType = 'STK'
    contract.exchange = 'SMART'
    contract.currency = 'USD'
    contract.primaryExchange = 'NASDAQ'

    # Request historical candles

    app.reqTickByTickData(1, contract, "", False, False)
    # app.reqMarketDataType(4)
    # app.reqMktData(1, contract, "", False, False, [])

    # app.disconnect()