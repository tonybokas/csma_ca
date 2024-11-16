#!/usr/bin/env python

import pandas as pd
from matplotlib import pyplot


# GRAPH 2

df = pd.read_csv('20241101.as-rel2.txt', sep='|', usecols=[0, 1, 2])

figure, plots = pyplot.subplots(nrows=2, ncols=2, figsize=(12, 6))

temp = pd.DataFrame({'type': ['distinct', 'providers', 'customers', 'peers'],
                     'freq': [len(df.drop_duplicates()),  # distinct links
                              len(set(df.query('value == -1').customer_as)),
                              len(set(df.query('value == 0').customer_as)),
                              len(set(df.query('value == -1').provider_as))]})

temp.plot.bar(ax=plots[0][0],
              x='type',
              y='freq',
              ylabel='distinct links',
              rot=0,
              legend=False)

bins = ['0', '1', '2-5', '6-100', '101-500', '501-1000', '>1000']

temp = df.query('value == -1').groupby('provider_as').count().customer_as

temp = pd.DataFrame({'as_value': bins,
                     'freq': [len(temp[temp == 0]),
                              len(temp[temp == 1]),
                              len(temp[temp.between(2, 5)]),
                              len(temp[temp.between(6, 100)]),
                              len(temp[temp.between(101, 500)]),
                              len(temp[temp.between(501, 1000)]),
                              len(temp[temp >= 1001])]})

temp.plot.bar(ax=plots[1][0],
              x='as_value',
              y='freq',
              ylabel='number of direct customers',
              rot=0,
              legend=False)

temp = df.query('value == 0').groupby('customer_as').count().provider_as

temp = pd.DataFrame({'as_value': bins,
                     'freq': [len(temp[temp == 0]),
                              len(temp[temp == 1]),
                              len(temp[temp.between(2, 5)]),
                              len(temp[temp.between(6, 100)]),
                              len(temp[temp.between(101, 500)]),
                              len(temp[temp.between(501, 1000)]),
                              len(temp[temp >= 1001])]})

temp.plot.bar(ax=plots[0][1],
              x='as_value',
              y='freq',
              ylabel='number of peers',
              rot=0,
              legend=False)

temp = df.query('value == -1').groupby('customer_as').count().provider_as

temp = pd.DataFrame({'as_value': bins,
                     'freq': [len(temp[temp == 0]),
                              len(temp[temp == 1]),
                              len(temp[temp.between(2, 5)]),
                              len(temp[temp.between(6, 100)]),
                              len(temp[temp.between(101, 500)]),
                              len(temp[temp.between(501, 1000)]),
                              len(temp[temp >= 1001])]})

temp.plot.bar(ax=plots[1][1],
              x='as_value',
              y='freq',
              ylabel='number of providers',
              rot=0,
              legend=False)

figure.tight_layout()
figure.suptitle('Degree Distributions')
figure.subplots_adjust(top=0.9)
figure.savefig(f'2_AS_degree_dist.png', dpi=200)
