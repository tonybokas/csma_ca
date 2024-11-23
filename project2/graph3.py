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
bins = ['<4',
        '4-8',
        '8-12',
        '12-16',
        '16-20',
        '20-24',
        '24-28',
        '28-32',
        '32-36',
        '36<']

freq = [df[df.as_id < 4000].ip_space.sum(),
        df[df.as_id.between(4001, 8000)].ip_space.sum(),
        df[df.as_id.between(8001, 12000)].ip_space.sum(),
        df[df.as_id.between(12001, 16000)].ip_space.sum(),
        df[df.as_id.between(16001, 20000)].ip_space.sum(),
        df[df.as_id.between(20001, 24000)].ip_space.sum(),
        df[df.as_id.between(24001, 28000)].ip_space.sum(),
        df[df.as_id.between(28001, 32000)].ip_space.sum(),
        df[df.as_id.between(32001, 36000)].ip_space.sum(),
        df[df.as_id > 36000].ip_space.sum()]

temp = DataFrame({'value': bins, 'freq': freq})
temp.freq = temp.freq / (1 * 10**9)  # adjust values to correspond to yticks

plot = temp.plot.bar(
    title='IP Space Distribution Across ASes',
    x='value',
    xlabel='AS ID number (thousands)',
    y='freq',
    yticks=[i * 0.1 for i in range(0, 14, 2)],
    ylabel='IP space (billions)',
    color='dimgrey',
    rot=0,
    legend=False
    )

plot.get_figure().tight_layout()
plot.get_figure().savefig('3_AS_space_dist.png', dpi=200)

print('Success.')
