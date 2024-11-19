#!/usr/bin/env python

from pandas import DataFrame, read_csv


''' NOTES

It seems like the professor wants us to compare the data from 2021 with 2024.
This seems like the only way to get the types for each AS. Since he just wants
totals, not actual AS values or details, I decided to just count the AS numbers
from 2024 that appear in 2021 under certain conditions.

The alternative is to do a bunch of join logic that would combine the
DataFrames. I think this way is more straightforward.
'''

# GRAPH 4 CLASSIFICAITON PIE CHART RECREATED

df21 = read_csv('20210401.as2types.txt',
                names=['as', 'source', 'type'],
                sep='|',
                skiprows=6)

df24 = read_csv('20241101.as-rel2.txt',
                names=['provider_as', 'customer_as', 'value'],  # column names
                sep='|',            # column separator
                usecols=[0, 1, 2])  # columns to keep

# SLICE 1

# Create subset of "any ASes without customers or peers":
subset = df24.query('value == -1').provider_as.unique()

# Find ASes that don't appear in the 2024 subset (i.e., no customers or peers).
# `df21['as'].isin(subset)` returns "True" or "False" for each index.
# The tilde (~) inverts those booleans, kind of how `not True` returns `False`.
# I then use those inverted booleans, which are indexed, to get the ASes that
# are in 2021 but not 2024:
enterprise = len(df21[~df21['as'].isin(subset)])

# SLICE 2

# Create subset of "any AS with no customers and at least one peer":
subset = (df24.query('value == 0').groupby('provider_as').count().reset_index()
          .query('customer_as > 1').provider_as)

# Find ASes that are in subset:
content = len(df21[df21['as'].isin(subset)])

# SLICE 3

# Create subset of "any AS with at least one customer":
subset = (df24.query('value == -1').groupby('provider_as').count().reset_index()
          .query('customer_as > 0').provider_as)

# Find ASes that are in subset:
transit = len(df21[df21['as'].isin(subset)])

# COMBINE SLICES AND PLOT

dfpie = DataFrame({'type': ['Enterprise', 'Content', 'Transit/Access'],
                   'count': [enterprise, content, transit]})

plot = dfpie.set_index('type').plot.pie(
    title='AS Classes 2024',
    y='count',
    ylabel='percent',
    autopct='%.1f',                               # display slice percentage
    colors=['darkgrey', 'dimgrey', 'gainsboro'],  # same colors as graph 1
    legend=False
    )

plot.get_figure().savefig('4_AS_classes.png', dpi=200)  # custom dots per inch

print('Success.')
