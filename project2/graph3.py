#!/usr/bin/env python

from pandas import DataFrame, read_csv, to_numeric

# GRAPH 3

df = read_csv('routeviews-rv2-20241106-1400.pfx2as.txt',
              names=['prefix', 'as_id'],  # column names
              sep='\t',                   # column separator
              usecols=[1, 2])             # columns to keep

# Remove rows with non-numeric characters in AS column:
df.as_id = df.as_id.apply(lambda x: to_numeric(x, errors='coerce'))
df = df.dropna()

# Calculate IP space per discussion post instructions:
df['ip_space'] = df.prefix.apply(lambda x: 2**(32 - x))

# Dervice the total IP space for each AS:
bins = ['<500', '501-1000', '1001-2000', '2001-4000', '4001-8000', '8000<']

freq = [df[df.as_id < 500].ip_space.sum(),
        df[df.as_id.between(501, 1000)].ip_space.sum(),
        df[df.as_id.between(1001, 2000)].ip_space.sum(),
        df[df.as_id.between(2001, 4000)].ip_space.sum(),
        df[df.as_id.between(4001, 8000)].ip_space.sum(),
        df[df.as_id > 8000].ip_space.sum()]

temp = DataFrame({'value': bins, 'freq': freq})
temp.freq = temp.freq / (1 * 10**9)  # adjust values to correspond to yticks

plot = temp.plot.bar(
    title='IP Space Distribution Across ASes',
    x='value',
    xlabel='AS ID',
    y='freq',
    yticks=[i * 0.1 for i in range(0, 23, 2)],
    ylabel='IP space (billions)',
    color='dimgrey',
    rot=0,
    legend=False
    )

plot.get_figure().tight_layout()
plot.get_figure().savefig('3_AS_space_dist.png', dpi=200)

print('Success.')
