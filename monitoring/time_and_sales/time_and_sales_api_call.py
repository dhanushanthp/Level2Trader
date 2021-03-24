from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.client import TickAttribLast, TickerId
import sys
import datetime
from time_and_sales import TimeAndSales


class IBapi(EWrapper, EClient):
    def __init__(self, ticker, time_range=6):
        EClient.__init__(self, self)
        self.data = []  # Initialize variable to store candle
        self.time_and_sales = TimeAndSales(ticker=ticker, multiple_of_10sec=time_range)

    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        print(f"{reqId}, {errorCode}, {errorString}")

    def tickByTickAllLast(self, reqId: int, tickType: int, ticktime: int, price: float, size: int,
                          tickAtrribLast: TickAttribLast, exchange: str,
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
            self.time_and_sales.data_generator(datetime.datetime.fromtimestamp(ticktime).strftime("%H:%M:%S"),
                                               price, size, exchange)


def main():
    ticker = str(sys.argv[1])
    time_range = int(sys.argv[2])
    app = IBapi(ticker, time_range)
    app.connect(host='127.0.0.1', port=7497, clientId=0)
    # Create contract object
    contract = Contract()
    contract.symbol = ticker
    contract.secType = 'STK'
    contract.exchange = 'SMART'
    contract.currency = 'USD'
    contract.primaryExchange = 'NASDAQ'

    # Request historical candles
    app.reqTickByTickData(reqId=19001, contract=contract, tickType="Last", numberOfTicks=0, ignoreSize=True)

    app.run()
    # app.cancelTickByTickData(1)
    app.disconnect()


main()
