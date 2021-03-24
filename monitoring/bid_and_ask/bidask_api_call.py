from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.client import TickerId, TickAttribBidAsk
import sys
from bidask import BidAsk
import datetime


class IBapi(EWrapper, EClient):
    def __init__(self, ticker):
        EClient.__init__(self, self)
        self.data = []  # Initialize variable to store candle
        self.time_and_sales = BidAsk(ticker=ticker, last_x_min=1)

    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        print(f"{reqId}, {errorCode}, {errorString}")

    def tickByTickBidAsk(self, reqId: int, time: int, bidPrice: float, askPrice: float,
                         bidSize: int, askSize: int, tickAttribBidAsk: TickAttribBidAsk):
        """

        :param reqId:
        :param time:
        :param bidPrice:
        :param askPrice:
        :param bidSize:
        :param askSize:
        :param tickAttribBidAsk:
        :return:
        """

        super().tickByTickBidAsk(reqId, time, bidPrice, askPrice, bidSize,

                                 askSize, tickAttribBidAsk)

        self.time_and_sales.data_generator(datetime.datetime.fromtimestamp(time).strftime("%H:%M:%S"), bidPrice, bidSize, askPrice, askSize)



def main():
    ticker = str(sys.argv[1])
    app = IBapi(ticker)
    app.connect(host='127.0.0.1', port=7497, clientId=0)
    # Create contract object
    contract = Contract()
    contract.symbol = ticker
    contract.secType = 'STK'
    contract.exchange = 'SMART'
    contract.currency = 'USD'
    contract.primaryExchange = 'NASDAQ'

    # Request historical candles
    app.reqTickByTickData(reqId=19002, contract=contract, tickType="BidAsk", numberOfTicks=0, ignoreSize=True)

    app.run()
    # app.cancelTickByTickData(1)
    # app.disconnect()


main()
