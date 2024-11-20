#!/usr/bin/env python

from pandas import DataFrame, read_csv, to_numeric
from matplotlib import pyplot


''' NOTES

PLOT 1

Customers: if value is -1 then link is provider-to-customer: count customer_as
Peers: if value is 0 then link is peer-to-peer: count customer_as
Providers: if value is -1 then link is provider-to-customer: count provider_as

PLOT 2, 3, 4

Same as above, but group by counted column, then allocate into bins
'''

# PLOT 1

df = read_csv('20241101.as-rel2.txt',
              names=['provider_as', 'customer_as', 'value'],  # column names
              sep='|',            # column separator
              usecols=[0, 1, 2])  # columns to keep

# Create a 2x2 figure with subplots:
figure, plots = pyplot.subplots(nrows=2, ncols=2, figsize=(12, 6))

freq = [len(set(df.query('value == 0').customer_as)),
        len(set(df.query('value == -1').provider_as)),
        len(set(df.query('value == -1').customer_as))]

# Total the number of links for each type; casting as set removes duplicates:
temp = DataFrame({'type': ['customers', 'peers', 'providers'], 'freq': freq})

temp.plot.bar(ax=plots[0][0],  # assign to top-left square of figure
              x='type',
              y='freq',
              ylabel='distinct links',
              color=['black', 'dimgrey', 'silver'],
              rot=0,  # don't rotate x-axis labels
              legend=False)

# PLOT 2

# Nominal bins:
bins = ['0', '1', '2-5', '6-100', '101-500', '501-1000', '1000<']

temp = df.query('value == -1').groupby('provider_as').count().customer_as

freq = [len(temp[temp == 0]),
        len(temp[temp == 1]),
        len(temp[temp.between(2, 5)]),
        len(temp[temp.between(6, 100)]),
        len(temp[temp.between(101, 500)]),
        len(temp[temp.between(501, 1000)]),
        len(temp[temp > 1000])]

# I tried to use hist plot but cannot get custom bins to work. Instead, I
# create a total for each bin and make a new DataFrame to plot. For
# temp[temp == X], the inner temp == X returns the rows that equal X, these
# are then filtered in by the outer temp. len then gives you the total in the
# pandas Series:
temp = DataFrame({'value': bins, 'freq': freq})

temp.plot.bar(ax=plots[0][1],
              x='value',
              xlabel='AS ID',
              y='freq',
              ylabel='number of direct customers',
              color='black',
              rot=0,
              legend=False)

# PLOT 3

temp = df.query('value == 0').groupby('customer_as').count().provider_as

freq = [len(temp[temp == 0]),
        len(temp[temp == 1]),
        len(temp[temp.between(2, 5)]),
        len(temp[temp.between(6, 100)]),
        len(temp[temp.between(101, 500)]),
        len(temp[temp.between(501, 1000)]),
        len(temp[temp > 1000])]

temp = DataFrame({'value': bins, 'freq': freq})

temp.plot.bar(ax=plots[1][0],
              x='value',
              xlabel='AS ID',
              y='freq',
              ylabel='number of peers',
              color='dimgrey',
              rot=0,
              legend=False)

# PLOT 4

# Read in routeviews file:
rv = read_csv('routeviews-rv2-20241106-1400.pfx2as.txt',
              names=['ip_address', 'prefix', 'as_id'],  # column names
              sep='\t')                                 # tab delimited

# Remove non-numeric AS values by setting them to null then dropping:
rv.as_id = rv.as_id.apply(lambda x: to_numeric(x, errors='coerce'))
rv = rv.dropna()

rv['ip_space'] = rv.prefix.apply(lambda x: 2**(32 - x))

# Dervice the total IP space for each AS:
rv = rv[['as_id', 'ip_space']].groupby('as_id').sum().reset_index()

temp = DataFrame({'value': bins,
                  'freq': [rv[rv.as_id == 0].ip_space.sum(),
                           rv[rv.as_id == 1].ip_space.sum(),
                           rv[rv.as_id.between(2, 5)].ip_space.sum(),
                           rv[rv.as_id.between(6, 100)].ip_space.sum(),
                           rv[rv.as_id.between(101, 500)].ip_space.sum(),
                           rv[rv.as_id.between(501, 1000)].ip_space.sum(),
                           rv[rv.as_id > 1000].ip_space.sum()]})

temp.plot.bar(ax=plots[1][1],
              x='value',
              xlabel='AS ID',
              y='freq',
              yticks=[i for i in range(0, 5 * 10**9, 1 * 10**9)],
              ylabel='number of providers (billions)',
              color='silver',
              rot=0,
              legend=False)

# FIGURE SETTINGS

figure.tight_layout()                               # improve spacing
figure.suptitle('Degree Distribution of AS Links')  # figure title
figure.subplots_adjust(top=0.92)                    # space below title
figure.savefig('2_AS_degree_dist.png', dpi=200)     # custom dots per inch

print('Success.')
