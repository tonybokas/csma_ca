#!/usr/bin/env python

from pandas import DataFrame, Series, concat, read_csv
from matplotlib import pyplot

''' NOTES

Customers: if value is -1 then link is p2c: count provider_as
Peers: if value is 0 then link is p2p: count customer_as and provider_as
Providers: if value is -1 then link is p2c: count customer_as
Global: count customer_as and provider_as
'''


def frequencies(series: Series) -> list:
    '''I tried to use hist plot but cannot get custom bins to work. Instead, I
    create a total for each bin and make a new DataFrame to plot. For
    temp[temp == X], the inner temp == X returns the rows that equal X, these
    are then filtered in by the outer temp. len then gives you the total in the
    pandas Series.'''

    return [len(series[series == 0]),
            len(series[series == 1]),
            len(series[series.between(2, 5)]),
            len(series[series.between(6, 100)]),
            len(series[series.between(101, 500)]),
            len(series[series.between(501, 1000)]),
            len(series[series > 1000])]


# Load Data:
df = read_csv('20241101.as-rel2.txt',
              names=['provider_as', 'customer_as', 'value'],  # column names
              sep='|',            # column separator
              usecols=[0, 1, 2])  # columns to keep

# FIGURE

# Nominal bins:
bins = ['0', '1', '2-5', '6-100', '101-500', '501-1000', '1000<']

# Create a 2x2 figure with subplots:
figure, plots = pyplot.subplots(nrows=2, ncols=2, figsize=(12, 6))

# PLOT 1

temp = concat([df.provider_as, df.customer_as])
temp = DataFrame({'value': bins, 'freq': frequencies(temp)})

temp.plot.bar(ax=plots[0][0],
              x='value',
              xlabel='AS ID',
              y='freq',
              ylabel='number of distinct links',
              logy=True,
              color='black',
              rot=0,
              legend=False)

# PLOT 2

temp = df.query('value == -1').provider_as
temp = DataFrame({'value': bins, 'freq': frequencies(temp)})

temp.plot.bar(ax=plots[0][1],
              x='value',
              xlabel='AS ID',
              y='freq',
              ylabel='number of direct customers',
              logy=True,
              color='black',
              rot=0,
              legend=False)

# PLOT 3

temp = df.query('value == 0')
temp = concat([temp.provider_as, temp.customer_as])
temp = DataFrame({'value': bins, 'freq': frequencies(temp)})

temp.plot.bar(ax=plots[1][0],
              x='value',
              xlabel='AS ID',
              y='freq',
              ylabel='number of peers',
              logy=True,
              color='dimgrey',
              rot=0,
              legend=False)

# PLOT 4

temp = df.query('value == -1').customer_as
temp = DataFrame({'value': bins, 'freq': frequencies(temp)})

temp.plot.bar(ax=plots[1][1],
              x='value',
              xlabel='AS ID',
              y='freq',
              ylabel='number of providers',
              logy=True,
              color='silver',
              rot=0,
              legend=False)

# FIGURE SETTINGS

figure.tight_layout()                               # improve spacing
figure.suptitle('Degree Distribution of AS Links')  # figure title
figure.subplots_adjust(top=0.92)                    # space below title
figure.savefig('2_AS_degree_dist.png', dpi=200)     # custom dots per inch

print('Success.')
