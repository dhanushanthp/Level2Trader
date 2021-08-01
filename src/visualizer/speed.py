import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from numerize.numerize import numerize
import warnings

warnings.filterwarnings("ignore")

plt.style.use('ggplot')
chart_width = 15
chart_height = 6

# create a figure with two subplots
fig, ax = plt.subplots(ncols=1, figsize=(chart_width, chart_height))
# ax.invert_xaxis()
fig.text(0.5, 0.01, 'Number of shares', ha='center')


def animate(i):
    data = pd.read_csv('data/test_data/2021071221_TSLA_tape.csv',
                       names=['time_tick', 'bid_price', 'bid_size', 'ask_price', 'ask_size', 'last_price', 'last_size', 'source'])

    agg_data = data.groupby(['time_tick'])['bid_price'].count().reset_index(name='speed')

    agg_data.sort_values(['time_tick'], inplace=True)

    agg_data = agg_data.tail(180)

    records_idx = np.arange(len(agg_data['time_tick']))  # the label locations
    # Ratio, If we use 0.5 then it will be bar without gaps since we have 2 bar side by size. The max value is 1 same as 100% space for bar
    bar_width = 0.45

    y = agg_data['time_tick'].astype(str)
    x1_high = agg_data['speed']
    # x2_high = agg_data['ask']

    # x1_total = total_on_sales['bid']
    # x2_total = total_on_sales['ask']

    ax.clear()  # High Sales
    # ax[1].clear()  # Total Sales
    # ax[0].invert_xaxis()

    # y coordinated of the bar
    # bar_bids_high = ax.bar(x=records_idx + bar_width, height=x1_high, width=bar_width, label='On BID', color='tab:red')
    ax.plot(agg_data['time_tick'], agg_data['speed'])
    # bar_ask_high = ax[0].barh(y=records_idx + bar_width + bar_width, width=x2_high, height=bar_width, label='On ASK', color='darkgreen')

    # bar_bids_total = ax[1].barh(y=records_idx + bar_width, width=x1_total, height=bar_width, label='On BID', color='tab:red')
    # bar_ask_total = ax[1].barh(y=records_idx + bar_width + bar_width, width=x2_total, height=bar_width, label='On ASK', color='darkgreen')

    # ticks: coordinates of the bar
    # ax.set_yticks(ticks=records_idx + bar_width + bar_width / 2)
    # ax.set_yticklabels(labels=[])

    # ax[1].set_yticks(ticks=records_idx + bar_width + bar_width / 2)
    # ax.set_yticklabels(labels=y, fontsize=12)

    # Annotate the bar with values
    # ax.bar_label(container=bar_bids_high, labels=[numerize(i) for i in x1_high], padding=-20)
    # ax[0].bar_label(container=bar_ask_high, labels=[numerize(i) for i in x2_high], padding=-20)

    # ax[1].bar_label(container=bar_bids_total, labels=[numerize(i) for i in x1_total], padding=3)
    # ax[1].bar_label(container=bar_ask_total, labels=[numerize(i) for i in x2_total], padding=3)

    # plt.legend(loc='upper right')
    ax.set_ylabel('Record/Second')
    # plt.tight_layout()
    ax.set_title('Identification of Speed')

    # ax[1].set_title('Total On Sales')


ani = FuncAnimation(fig, animate, interval=1000)
plt.tight_layout(pad=0.5)
plt.subplots_adjust(left=0.035, right=0.96, top=0.95, bottom=0.08)
plt.show()
