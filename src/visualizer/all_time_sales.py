import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from numerize.numerize import numerize

plt.style.use('ggplot')
chart_width = 15
chart_height = 5
plt.figure(figsize=(chart_width, chart_height))
plt.rcParams['toolbar'] = 'None'


def animate(i):
    data = pd.read_csv('data/real_time_data_output/all_time_sales.csv')
    data.sort_values(['price'], inplace=True)
    records_idx = np.arange(len(data['price']))  # the label locations
    # Ratio, If we use 0.5 then it will be bar without gaps since we have 2 bar side by size. The max value is 1 same as 100% space for bar
    bar_width = 0.45

    x = data['price'].astype(str)
    y1 = data['bid']
    y2 = data['ask']
    plt.cla()
    # x coordinated of the bar
    bar_bids = plt.bar(x=records_idx + bar_width, height=y1, width=bar_width, label='On BID', color='tab:red')
    bar_ask = plt.bar(x=records_idx + bar_width + bar_width, height=y2, width=bar_width, label='On ASK', color='darkgreen')
    # ticks: coordinates of the bar
    plt.xticks(ticks=records_idx + bar_width + bar_width / 2, labels=x, fontsize=14)

    # Annotate the bar with values
    plt.bar_label(container=bar_bids, labels=[numerize(i) for i in y1], padding=3)
    plt.bar_label(container=bar_ask, labels=[numerize(i) for i in y2], padding=3)

    plt.legend(loc='upper right')
    plt.xlabel('Price')
    plt.ylabel('Number of shares')
    plt.title('Total On Sales')
    plt.tight_layout()


ani = FuncAnimation(plt.gcf(), animate, interval=1000)
plt.tight_layout()
plt.show()
