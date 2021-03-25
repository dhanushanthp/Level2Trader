import configparser


class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('example.ini')

    def bidask_timerange(self):
        self.config.get('BIDASK', 'timerange')
