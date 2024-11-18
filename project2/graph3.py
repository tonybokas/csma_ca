#!/usr/bin/env python

from pandas import DataFrame, read_csv, to_numeric
from matplotlib import pyplot


# GRAPH 3

df = read_csv('routeviews-rv2-20241106-1400.pfx2as.txt',
              names=['prefix_len', 'as_num'],  # column names
              sep='\t',                                     # column separator
              usecols=[1, 2])                               # columns to keep

# The data is not totally clean. AS number has some non-numeric characters.
# Convert any non-numeric values in as_num column to NaN (Not a Number),
# then drop NaN and cast as_num to int:
df.as_num = df.as_num.apply(lambda x: to_numeric(x, errors='coerce'))
df = df.dropna()
df.as_num = df.as_num.astype(int)

# Similar approach to binning as in graph 2, but this time, I am calculating
# the mean prefix length for each AS bin:
df = df.drop_duplicates().groupby('as_num').mean().reset_index()
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

prefix_len_dist = [df[df.as_num.between(0, 100)].prefix_len.mean(),
                   df[df.as_num.between(101, 200)].prefix_len.mean(),
                   df[df.as_num.between(201, 300)].prefix_len.mean(),
                   df[df.as_num.between(301, 400)].prefix_len.mean(),
                   df[df.as_num.between(401, 500)].prefix_len.mean(),
                   df[df.as_num.between(501, 600)].prefix_len.mean(),
                   df[df.as_num.between(601, 700)].prefix_len.mean(),
                   df[df.as_num.between(701, 800)].prefix_len.mean(),
                   df[df.as_num.between(801, 900)].prefix_len.mean(),
                   df[df.as_num.between(901, 1000)].prefix_len.mean(),
                   df[df.as_num > 1000].prefix_len.mean()]

df = DataFrame({'as_num': bins, 'prefix_len': prefix_len_dist})

plot = df.plot.bar(title='AS and Prefix Length',
                   x='as_num',
                   xlabel='AS number',
                   y='prefix_len',
                   ylabel='average prefix length',
                   color='black',
                   rot=45,
                   legend=False)

plot.get_figure().tight_layout()
plot.get_figure().savefig('3_AS_space_dist.png', dpi=200)

print('Success.')
