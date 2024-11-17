#!/usr/bin/env python

from pandas import read_csv
from matplotlib import pyplot


# GRAPH 1 AS CLASSIFICATION PIE CHART

files = ['20150801.as2types.txt', '20210401.as2types.txt']

# Create a 1x2 figure with subplots:
figure, plots = pyplot.subplots(1, 2, figsize=(12, 6))

# enumerate returns an integer for each iteration, in this case, that means
# it returns a 0 for the first iteration and a 1 for the second. We then use
# those integers for the subplot positioning:
for i, f in enumerate(files):
    # File, column names, column separater, and number of rows to skip:
    df = read_csv(f, names=['as', 'source', 'type'], sep='|', skiprows=6)

    df.groupby('type').count().plot.pie(
        ax=plots[i],
        title='AS Classes ' + f[:4],  # read first 4 characters (i.e., year)
        y='as',
        ylabel='percent',
        autopct='%.1f',  # display slice percentage
        colors=['dimgrey', 'darkgrey', 'gainsboro'],
        legend=False
        )

figure.savefig('1_AS_classes.png', dpi=200)  # custom dots per inch

print('Success.')
