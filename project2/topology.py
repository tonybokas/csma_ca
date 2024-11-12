#!/usr/bin/env python

import pandas as pd
from matplotlib import pyplot


# AS classification Create pie charts

files = ['20150801.as2types.txt', '20210401.as2types.txt']

for f in files:
    df = pd.read_csv(f, sep='|')
    df.groupby('type').count().plot.pie(y='as', ylabel='count')
    pyplot.show()
