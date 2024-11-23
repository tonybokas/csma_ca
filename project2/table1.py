#!/usr/bin/env python

from pandas import DataFrame, concat, read_csv

''' NOTES

Customers: if value is -1 then link is p2c: count provider_as
Peers: if value is 0 then link is p2p: count customer_as and provider_as
Providers: if value is -1 then link is p2c: count customer_as
Global: count customer_as and provider_as
'''

# Load Data:
df = read_csv('20241101.as-rel2.txt',
              names=['provider_as', 'customer_as', 'value'],  # column names
              sep='|',            # column separator
              usecols=[0, 1, 2])  # columns to keep


g_rank = DataFrame({'as_id': concat([df.provider_as, df.customer_as]),
                    'members': 1})

g_rank = (g_rank.groupby('as_id').count()           # count connections
          .sort_values('members', ascending=False)  # rank by count
          .reset_index()[:50])                      # only need top 50

# Filter and save all each distinct as_id value that corresponds to each
# as_id in the top-50 list:
g_rank['conn'] = g_rank.as_id.apply(
    lambda x: set(df[df.provider_as == x].customer_as.to_list() +
                  df[df.customer_as == x].provider_as.to_list()),
    )

as_id_1 = g_rank.iloc[0]   # the #1 as_id

# Check if each as_id in the top 50 is the #1 as_id's connections:
g_rank['clique_1'] = g_rank.apply(lambda x: x.as_id in as_id_1.conn, axis=1)
g_rank.loc[0, 'clique_1'] = True  # set to True since its the root

# Save to CSV:
g_rank[['as_id', 'members', 'clique_1']].to_csv('5_AS_clique.csv')

print('Success.')
