#!/usr/bin/env python

from pandas import DataFrame, concat, read_csv

''' NOTES

Customers: if value is -1 then link is p2c: count provider_as
Peers: if value is 0 then link is p2p: count customer_as and provider_as
Providers: if value is -1 then link is p2c: count customer_as
Global: count customer_as and provider_as
'''

# ETL

df = read_csv('20241101.as-rel2.txt',
              names=['provider_as', 'customer_as', 'value'],  # column names
              sep='|',            # column separator
              usecols=[0, 1, 2])  # columns to keep


g_rank = DataFrame({'as_id': concat([df.provider_as, df.customer_as]),
                    'members': 1})

g_rank = (g_rank.groupby('as_id').count()           # count connections
          .sort_values('members', ascending=False)  # rank by count
          .reset_index()[:50])                      # only need top 50

# Filter and save each distinct as_id value in the original data
# that corresponds to each as_id in the top-50 list:
g_rank['conn'] = g_rank.as_id.apply(
    lambda x: set(df[df.provider_as == x].customer_as.to_list() +
                  df[df.customer_as == x].provider_as.to_list()),
    )

clique = g_rank.iloc[0].conn  # the as_id #1 clique

# Check if each as_id in the top 50 is the #1 as_id's connections:
g_rank['clique_1'] = g_rank.apply(lambda x: x.as_id in clique, axis=1)
g_rank.loc[0, 'clique_1'] = True  # set to True since # as_id the root

# CREATE API STRING FOR CAIDA.ORG

print('Top 10 clique-member AS numbers as CAIDA API string\n'
      '(https://api.data.caida.org/as2org/v1/doc):\n')

api_string = ''

for i, as_id in enumerate(g_rank.query('clique_1 == True').as_id.to_list()):
    if i == 10:
        break
    api_string += str(as_id) + '_'

print(api_string[:-1], '\n')
print('Hint: On the API page, use the "Get /as2org/v1/asns/{asns}" endpoint\n'
      'to retrieve a JSON object of the organizations and their details.\n'
      'Put the string in the "asns *required" field and select "execute".\n'
      'Scroll down to "Responses". You will see your JSON there.\n')

# SAVE RESULTS

g_rank[['as_id', 'members', 'clique_1']].to_csv('5_AS_clique.csv')

print('Success.')
