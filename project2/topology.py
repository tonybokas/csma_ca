#!/usr/bin/env python

import pandas as pd
from matplotlib import pyplot


# GRAPH 1 AS CLASSIFICATION PIE CHART

files = ['20150801.as2types.txt', '20210401.as2types.txt']

figure, plots = pyplot.subplots(1, 2, figsize=(12, 6))

for i, f in enumerate(files):
    df = pd.read_csv(f, sep='|')

    df.groupby('type').count().plot.pie(
        ax=plots[i],
        title='AS Classes ' + f[:4],
        y='as',
        ylabel='percent',
        autopct='%.1f',
        colors=['dimgrey', 'darkgrey', 'gainsboro'],
        legend=False
        )

figure.savefig(f'1_AS_classes.png', dpi=200)


# GRAPH 2
