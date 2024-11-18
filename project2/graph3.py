#!/usr/bin/env python

from pandas import DataFrame, read_csv, to_numeric
from matplotlib import pyplot


# GRAPH 3

df = read_csv('routeviews-rv2-20241106-1400.pfx2as.txt',
              names=['prefix_len', 'as_num'],  # column names
              sep='\t',                                     # column separator
              usecols=[1, 2])                               # columns to keep

# Convert any non-numeric values in as_num column to NaN (Not a Number):
df.as_num = df.as_num.apply(lambda x: to_numeric(x, errors='coerce'))
df = df.dropna()                   # drop NaN
df.as_num = df.as_num.astype(int)  # cast as_num to int

df = df.drop_duplicates().groupby('as_num').mean().reset_index()
df.prefix_len = df.prefix_len.round().astype(int)

bins = ['0-5', '6-100', '101-500', '501-1000', '1000<']

prefix_len_dist = [df[df.as_num.between(0, 5)].prefix_len.mean(),
                   df[df.as_num.between(6, 100)].prefix_len.mean(),
                   df[df.as_num.between(101, 500)].prefix_len.mean(),
                   df[df.as_num.between(501, 1000)].prefix_len.mean(),
                   df[df.as_num >= 1001].prefix_len.mean()]

df = DataFrame({'as_num': bins, 'prefix_len': prefix_len_dist})

plot = df.plot.bar(title='AS and Prefix Length',
                   x='as_num',
                   xlabel='AS number',
                   y='prefix_len',
                   ylabel='maximum prefix length',
                   color='black',
                   rot=0,
                   legend=False)

plot.get_figure().savefig('3_AS_space_dist.png',
                          dpi=200)  # custom dots per inch

print('Success.')
