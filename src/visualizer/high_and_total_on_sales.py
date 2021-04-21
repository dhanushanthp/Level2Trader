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
fig, ax = plt.subplots(ncols=2, figsize=(chart_width, chart_height))
ax[0].invert_xaxis()
fig.text(0.5, 0.01, 'Number of shares', ha='center')


def animate(i):
    total_on_sales = pd.read_csv('data/real_time_data_output/all_time_sales.csv')
    total_on_sales.sort_values(['price'], inplace=True)

    hig_on_sales = pd.read_csv('data/real_time_data_output/all_time_high.csv')
    hig_on_sales.sort_values(['price'], inplace=True)

    records_idx = np.arange(len(hig_on_sales['price']))  # the label locations
    # Ratio, If we use 0.5 then it will be bar without gaps since we have 2 bar side by size. The max value is 1 same as 100% space for bar
    bar_width = 0.45

    y = hig_on_sales['price'].astype(str)
    x1_high = hig_on_sales['bid']
    x2_high = hig_on_sales['ask']

    x1_total = total_on_sales['bid']
    x2_total = total_on_sales['ask']

    ax[0].clear()  # High Sales
    ax[1].clear()  # Total Sales
    ax[0].invert_xaxis()

    # y coordinated of the bar
    bar_bids_high = ax[0].barh(y=records_idx + bar_width, width=x1_high, height=bar_width, label='On BID', color='tab:red')
    bar_ask_high = ax[0].barh(y=records_idx + bar_width + bar_width, width=x2_high, height=bar_width, label='On ASK', color='darkgreen')

    bar_bids_total = ax[1].barh(y=records_idx + bar_width, width=x1_total, height=bar_width, label='On BID', color='tab:red')
    bar_ask_total = ax[1].barh(y=records_idx + bar_width + bar_width, width=x2_total, height=bar_width, label='On ASK', color='darkgreen')

    # ticks: coordinates of the bar
    ax[0].set_yticks(ticks=records_idx + bar_width + bar_width / 2)
    ax[0].set_yticklabels(labels=[])

    ax[1].set_yticks(ticks=records_idx + bar_width + bar_width / 2)
    ax[1].set_yticklabels(labels=y, fontsize=12)

    # Annotate the bar with values
    ax[0].bar_label(container=bar_bids_high, labels=[numerize(i) for i in x1_high], padding=-20)
    ax[0].bar_label(container=bar_ask_high, labels=[numerize(i) for i in x2_high], padding=-20)

    ax[1].bar_label(container=bar_bids_total, labels=[numerize(i) for i in x1_total], padding=3)
    ax[1].bar_label(container=bar_ask_total, labels=[numerize(i) for i in x2_total], padding=3)

    # plt.legend(loc='upper right')
    ax[0].set_ylabel('Price')
    # plt.tight_layout()
    ax[0].set_title('High On Sales')

    ax[1].set_title('Total On Sales')


ani = FuncAnimation(fig, animate, interval=1000)
plt.tight_layout(pad=0.5)
plt.subplots_adjust(left=0.035, right=0.96, top=0.95, bottom=0.08)
plt.show()
