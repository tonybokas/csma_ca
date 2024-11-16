#!/usr/bin/env python

import pandas as pd
from matplotlib import pyplot


# GRAPH 2

file = '20241101.as-rel2.txt'

df = pd.read_csv(file, sep='|', usecols=[0, 1, 2])

print(df.head())
print()
df.info()
print()
print(round(df.describe()))
print()
print(df.nunique())
print()
print(df.apply(pd.unique))
