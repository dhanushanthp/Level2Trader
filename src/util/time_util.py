class TimeUtil:
    def __init__(self):
        pass

    @staticmethod
    def round_time(value, base=5):
        return str(base * round(value / base)).zfill(2)
