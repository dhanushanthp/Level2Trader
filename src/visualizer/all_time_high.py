import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from numerize.numerize import numerize

plt.style.use('ggplot')
chart_width = 10
chart_height = 6
plt.figure(figsize=(chart_width, chart_height))
plt.rcParams['toolbar'] = 'None'


def animate(i):
    data = pd.read_csv('data/real_time_data_output/all_time_high.csv')
    data.sort_values(['price'], inplace=True)
    records_idx = np.arange(len(data['price']))  # the label locations
    # Ratio, If we use 0.5 then it will be bar without gaps since we have 2 bar side by size. The max value is 1 same as 100% space for bar
    bar_width = 0.45

    y = data['price'].astype(str)
    x1 = data['bid']
    x2 = data['ask']
    plt.cla()
    # x coordinated of the bar
    bar_bids = plt.barh(y=records_idx + bar_width, width=x1, height=bar_width, label='On BID', color='tab:red')
    bar_ask = plt.barh(y=records_idx + bar_width + bar_width, width=x2, height=bar_width, label='On ASK', color='darkgreen')
    # ticks: coordinates of the bar
    plt.yticks(ticks=records_idx + bar_width + bar_width / 2, labels=y, fontsize=14)

    # Annotate the bar with values
    plt.bar_label(container=bar_bids, labels=[numerize(i) for i in x1], padding=3)
    plt.bar_label(container=bar_ask, labels=[numerize(i) for i in x2], padding=3)

    # plt.legend(loc='upper right')
    plt.ylabel('Price')
    plt.xlabel('Number of shares')
    plt.title('High On Sales')
    plt.tight_layout()


ani = FuncAnimation(plt.gcf(), animate, interval=1000)
plt.tight_layout()
plt.show()
