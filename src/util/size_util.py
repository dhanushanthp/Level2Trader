class SizeUtil:
    def __init__(self):
        pass

    @staticmethod
    def find_closest(bid: float, ask: float, last: float) -> float:
        """
        Find the closest price w.r.t to bid and ask compare to last value

        :param bid: bid price, level II first tier only
        :param ask: ask price, level II first tier only
        :param last: last price, Time & Sales
        :return: Closest possible to bid or ask
        """
        return min([bid, ask], key=lambda x: abs(x - last))
