#!/usr/bin/env python

from pandas import DataFrame, read_csv, to_numeric
from matplotlib import pyplot


# GRAPH 3

df = read_csv('routeviews-rv2-20241106-1400.pfx2as.txt',
              names=['prefix_len', 'as_id'],  # column names
              sep='\t',                                     # column separator
              usecols=[1, 2])                               # columns to keep

# The data is not totally clean. AS ID has some non-numeric characters.
# Convert any non-numeric values in as_id column to NaN (Not a Number),
# then drop NaN and cast as_id to int:
df.as_id = df.as_id.apply(lambda x: to_numeric(x, errors='coerce'))
df = df.dropna()
df.as_id = df.as_id.astype(int)

# Similar approach to binning as in graph 2, but this time, I am calculating
# the mean prefix length for each AS bin:
df = df.drop_duplicates().groupby('as_id').mean().reset_index()
df.prefix_len = df.prefix_len.round().astype(int)

bins = ['0-100',
        '101-200',
        '201-300',
        '301-400',
        '401-500',
        '501-600',
        '601-700',
        '701-800',
        '801-900',
        '901-1000',
        '1000<']

prefix_len_dist = [df[df.as_id.between(0, 100)].prefix_len.mean(),
                   df[df.as_id.between(101, 200)].prefix_len.mean(),
                   df[df.as_id.between(201, 300)].prefix_len.mean(),
                   df[df.as_id.between(301, 400)].prefix_len.mean(),
                   df[df.as_id.between(401, 500)].prefix_len.mean(),
                   df[df.as_id.between(501, 600)].prefix_len.mean(),
                   df[df.as_id.between(601, 700)].prefix_len.mean(),
                   df[df.as_id.between(701, 800)].prefix_len.mean(),
                   df[df.as_id.between(801, 900)].prefix_len.mean(),
                   df[df.as_id.between(901, 1000)].prefix_len.mean(),
                   df[df.as_id > 1000].prefix_len.mean()]

df = DataFrame({'as_id': bins, 'prefix_len': prefix_len_dist})

plot = df.plot.bar(title='AS and Prefix Length',
                   x='as_id',
                   xlabel='AS ID',
                   y='prefix_len',
                   ylabel='average prefix length',
                   color='black',
                   rot=45,
                   legend=False)

plot.get_figure().tight_layout()
plot.get_figure().savefig('3_AS_space_dist.png', dpi=200)

print('Success.')
