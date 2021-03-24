from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract


class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

        def error(self, reqId, errorCode, errorString):
            print("Error: ", reqId, " ", errorCode, " ", errorString)

        def historicalData(self, reqId, bar):
            print("HistoricalData. ", reqId, " Date:", bar.date, "Open:", bar.open,
                  "High:", bar.high, "Low:", bar.low, "Close:", bar.close, "Volume:", bar.volume, "Count:",
                  bar.barCount,
                  "WAP:", bar.average)


def main():
    app = TestApp()

    app.connect("127.0.0.1", 7497, 0)
    # define contract for EUR.USD forex pair
    contract = Contract()
    contract.symbol = "EUR"
    contract.secType = "CASH"
    contract.exchange = "IDEALPRO"
    contract.currency = "USD"
    app.reqHistoricalData(1, contract, "", "1 D", "1 min", "MIDPOINT", 0, 1, False, [])

    # Working with Pandas DataFrames
    import pandas

    df = pandas.DataFrame(app.data, columns=['DateTime', 'Close'])
    df['DateTime'] = pandas.to_datetime(df['DateTime'], unit='s')
    df.to_csv('EURUSD_Hourly.csv')

    print(df)

    app.disconnect()
    app.run()
