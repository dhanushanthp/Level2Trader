import pandas as pd


class Speed:
    def __init__(self):
        pass

    total_on_sales = pd.read_csv('data/real_time_data_output/all_time_sales.csv')
    total_on_sales.sort_values(['price'], inplace=True)

    def speed_calculator(self, tick_time: str, size: int):
        """
        Calculate the speed of a tape that help to identify breakouts or breakdowns.
        Count number of sales in a second
        :return:
        """
        self.speed = self.speed + 1

        if self.previous_time is None:
            self.previous_time = tick_time
            # Reset speed for next second
            self.speed = 0

        if self.previous_time != tick_time:
            # self.clear()
            print(tick_time, self.speed)
