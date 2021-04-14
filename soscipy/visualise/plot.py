import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import seaborn as sns


def sns_cntplt_array(dat, chart_title='Chart_Title', export=False):
    assert type(dat)==list, 'Data entered must be an array or list'
    dfWIM = pd.DataFrame({'AXLES': dat})
    ncount = len(dfWIM)
    order = dfWIM[dfWIM.columns[0]].unique()
    order = order.sort()

    plt.figure(figsize=(12, 8))
    ax = sns.countplot(x="AXLES", data=dfWIM, order=order)
    plt.title(chart_title)
    plt.xlabel('Number of Axles')

    # Make twin axis
    ax2 = ax.twinx()

    # Switch so count axis is on right, frequency on left
    ax2.yaxis.tick_left()
    ax.yaxis.tick_right()

    # Also switch the labels over
    ax.yaxis.set_label_position('right')
    ax2.yaxis.set_label_position('left')

    ax2.set_ylabel('Frequency [%]')

    for p in ax.patches:
        x = p.get_bbox().get_points()[:, 0]
        y = p.get_bbox().get_points()[1, 1]
        ax.annotate('{:.1f}%'.format(100. * y / ncount), (x.mean(), y),
                    ha='center', va='bottom')  # set the alignment of the text

    # Use a LinearLocator to ensure the correct number of ticks
    ax.yaxis.set_major_locator(ticker.LinearLocator(11))

    # Fix the frequency range to 0-100
    ax2.set_ylim(0, 100)
    ax.set_ylim(0, ncount)

    # And use a MultipleLocator to ensure a tick spacing of 10
    ax2.yaxis.set_major_locator(ticker.MultipleLocator(10))

    # Need to turn the grid on ax2 off, otherwise the gridlines end up on top of the bars
    ax2.grid(None)
    if export:
        plt.savefig(chart_title + '.pdf')