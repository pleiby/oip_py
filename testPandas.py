# -*- coding: utf-8 -*-
"""
Created on Sat Dec  5 13:46:21 2015

@author: pzl
"""

# testPandas.py

import numpy as np
import pandas as pd

# see: http://pandas.pydata.org/pandas-docs/stable/dsintro.html

# s = pd.Series(data, index=index, name="")
s = pd.Series(data=np.random.normal(1,2.0,size=1000), name="RVseries1")

# A key difference between Series and ndarray is that operations between
# Series automatically align the data based on label. Thus, you can write
# computations without giving consideration to whether the Series involved
# have the same labels.

# Being able to write code without doing any explicit data alignment grants
# immense freedom and flexibility in interactive data analysis and research.
# The integrated data alignment features of the pandas data structures
# set pandas apart from the majority of related tools for working with labeled data.

# keeping labels with slices, and aligning by (row) label for math operations
# is useful.  In this case it means simple shifts are ignored.
(s[1:] - s[:-1])[0:10]  # returns all zeros

### DataFrame
# DataFrame is a 2-dimensional labeled data structure with
# columns of potentially different types.
# Can hink of it like a spreadsheet or SQL table, or a dict of Series objects.
# It is generally the most commonly used pandas object. 

# Along with the data, you can optionally pass index (row labels) and columns
# (column labels) arguments. If you pass an index and / or columns,
# you are guaranteeing the index and / or columns of the resulting DataFrame.
# Thus, a dict of Series plus a specific index will discard all data not
# matching up to the passed index.

### DataFrame from Series

d = {'one' : pd.Series([1., 2., 3.], index=['a', 'b', 'c']), 
     'two' : pd.Series([1., 2., 3., 4.], index=['a', 'b', 'c', 'd'])}

df = pd.DataFrame(d)
df

# vs
pd.DataFrame(d, index=['d', 'b', 'a'])

df.index
df.columns

### DataFrame From dict of ndarrays / lists

# The ndarrays must all be the same length. If an index is passed, it must clearly also be the same length as the arrays. If no index is passed, the result will be range(n), where n is the array length.

d = {'one' : [1., 2., 3., 4.], 'two' : [4., 3., 2., 1.]}
pd.DataFrame(d)
pd.DataFrame(d, index=['a', 'b', 'c', 'd'])


### DataFrame From structured or record array

# This case is handled identically to a dict of arrays.

data = np.zeros((2,), dtype=[('A', 'i4'),('B', 'f4'),('C', 'a10')])

data[:] = [(1,2.,'Hello'), (2,3.,"World")]

pd.DataFrame(data)
# can add column (series) names
pd.DataFrame(data, index=['first', 'second'])

### DataFrame From a list of dicts

DataFrame.from_items

# DataFrame.from_items works analogously to the form of the dict constructor
#  that takes a sequence of (key, value) pairs, where the keys are column
#  (or row, in the case of orient='index') names,
#  and the value are the column values (or row values).
# This can be useful for constructing a DataFrame with the columns in a
#  particular order without having to pass an explicit list of columns:

pd.DataFrame.from_items([('A', [1, 2, 3]), ('B', [4, 5, 6])])

# Can treat a DataFrame semantically like a dict of like-indexed Series objects.
#  Getting, setting, and deleting columns works with the same syntax as the analogous dict operations:

df['one']
df['three'] = df['one'] * df['two']
df['three']
df['three']>2

### Broadcsting

# When doing an operation between DataFrame and Series,
# the default behavior is to align the Series index on the DataFrame columns,
# thus broadcasting row-wise. For example:

df - df.iloc[0]
# Note: this is very different from R

# In the special case of working with time series data, and the DataFrame
# index also contains dates, the broadcasting will be column-wise:

indexOfDates = pd.date_range('1/1/2000', periods=8)

df_t = pd.DataFrame(np.random.randn(8, 3), index=indexOfDates, columns=list('ABC'))

df_t
df_t['A']

df_t - df_t['A']
# ??? not at all clear to me why you would want this behavior


# When inserting a scalar value, it will naturally be propagated to fill the column:

df['foo'] = 'bar'
df

# Columns can be deleted or popped like with a dict:

df2 = df # note this is an alias, not a copy, of df

del df2['two']

three = df2.pop('three')

df2
df


### Assigning New Columns in Method Chains

# New in version 0.16.0.

# Inspired by dplyr’s mutate verb, DataFrame has an assign() method
# that allows you to easily create new columns that are potentially
# derived from existing columns.

iris = pd.read_csv('data/iris.data')
iris.head()

(iris.assign(sepal_ratio = iris['SepalWidth'] / iris['SepalLength']).head())

# assign **always** returns a copy of the data, leaving the original DataFrame untouched.

### Indexing / Selection

# The basics of indexing are as follows:
#
# Operation	Syntax	Result
# Select column	df[col]	Series
# Select row by label	df.loc[label]	Series
# Select row by integer location	df.iloc[loc]	Series
# Slice rows	df[5:10]	DataFrame
# Select rows by boolean vector	df[bool_vec]	DataFrame

### Data alignment and arithmetic

# Data alignment between DataFrame objects automatically align on both the
# columns and the index (row labels). Again, the resulting object will have
# the union of the column and row labels.

# Note: **this is very different from behavior of R**, 
# where user is responsible for data alignment

### Console display

# Very large DataFrames will be truncated to display them in the console.
# You can also get a summary using info().
# (Here I am reading a CSV version of the baseball dataset from the plyr R package):

baseball = pd.read_csv('data/baseball.csv')
# New since 0.10.0, wide DataFrames will now be printed across multiple rows by default:
pd.DataFrame(np.random.randn(3, 12))

### Data Manipulation: melt, pivot, groupby
#The groupby() method is similar to base R aggregate function.

df = pd.DataFrame({
  'v1': [1,3,5,7,8,3,5,np.nan,4,5,7,9],
  'v2': [11,33,55,77,88,33,55,np.nan,44,55,77,99],
  'by1': ["red", "blue", 1, 2, np.nan, "big", 1, 2, "red", 1, np.nan, 12],
  'by2': ["wet", "dry", 99, 95, np.nan, "damp", 95, 99, "red", 99, np.nan,
          np.nan]
})

g = df.groupby(['by1','by2'])

g[['v1','v2']].mean()

# pandas.melt(frame, id_vars=None, value_vars=None, var_name=None, value_name='value', col_level=None)
# “Unpivots” a DataFrame from wide format to long format, optionally leaving identifier variables set.
# This function is useful to massage a DataFrame into a format
# where one or more columns are identifier variables (id_vars),
# while all other columns, considered measured variables (value_vars),
# are “unpivoted” to the row axis,
# leaving just two non-identifier columns, ‘variable’ and ‘value’.
df = pd.DataFrame({'A': {0: 'a', 1: 'b', 2: 'c'},
                   'B': {0: 1, 1: 3, 2: 5},
                   'C': {0: 2, 1: 4, 2: 6}})
df
pd.melt(df, id_vars=['A'], value_vars=['B', 'C'])

# Analogous to R's "cast", In Python the best way is to make use of pivot_table():

df = pd.DataFrame({
     'x': np.random.uniform(1., 168., 12),
     'y': np.random.uniform(7., 334., 12),
     'z': np.random.uniform(1.7, 20.7, 12),
     'month': [5,6,7]*4,
     'week': [1,2]*6
})
df

mdf = pd.melt(df, id_vars=['month', 'week'])
mdf

pd.pivot_table(mdf, values='value', index=['variable','week'],
                 columns=['month'], aggfunc=np.mean)


# df.describe is analogous to R's summary
# Describe shows a quick statistic summary of your data

df.describe()

# The **isin()** method is similar to R %in% operator:

s = pd.Series(np.arange(5),dtype=np.float32)
s
s.isin([2, 4])

# pandas "eval" is similar to R "with" for easily referencing series in dataframe
#  In R, with(df, a + b)
# In pandas the equivalent expression, using the eval() method, would be:
df = pd.DataFrame({'a': np.random.randn(10), 'b': np.random.randn(10)})
df
df.eval('a + b')

# See http://pandas.pydata.org/pandas-docs/stable/10min.html#min

### Slicing
# Selecting multiple columns by name in pandas is straightforward

df = pd.DataFrame(np.random.randn(10, 3), columns=list('abc'))

df[['a', 'c']]

# df.a is equivalent to df['a'], and is the simplest way to reference series
df.a

### Selection
# Note While standard Python / Numpy expressions for selecting and setting are
# intuitive and come in handy for interactive work, for production code,
# we recommend the optimized pandas data access methods,
#   .at, .iat, .loc, .iloc and .ix.

# set up some dates for index (rownames) of dataframe
dates = pd.date_range('20150101', periods=np.shape(df)[0])
df.index=dates
df

# Selecting via [], which slices the rows.
df[2:4]  # either by row number
df['2015-01-05':'2015-01-08'] # or row label

# Selection by Label - row vector selected
df.loc[dates[0]]

# slicing selection for multiple dimension, with .loc
df.loc[:,:]
df.loc[:,'a':'b']
df.loc['20150102':'20150104',['a','c']]

# slicing Selection by Position (integer indexed slices) with **.iloc**

#Select via the position of the passed integers
df.iloc[3]  # returns the row

# By integer slices in both dimensions, acting similar to numpy/python
df.iloc[3:5,0:2]

# By lists of integer position locations, similar to the numpy/python style
df.iloc[[1,2,4],[0,2]]

# For slicing rows explicitly
df.iloc[1:3,:] 
    
# For slicing columns explicitly
df.iloc[:,1:3]

# For getting a value explicitly
df.iloc[1,1]

# For getting fast access to a scalar (equiv to the prior method)
df.iat[1,1]

### Boolean Indexing

# Using a single column’s values to select data.
df[df.a > 0]

# A where operation for getting.
df[df>0]


### Apply

# Applying functions to the data is easy with df.apply()
df.apply(np.cumsum)

df.apply(lambda x: x.max() - x.min())

### Grouping - .groupby() dataframe method
# By “group by” we are referring to a process involving one or more of the following steps

#  Splitting the data into groups based on some criteria
#  Applying a function to each group independently
#  Combining the results into a data structure


### Plotting
# Plotting docs.

ts = pd.Series(np.random.randn(1000), index=pd.date_range('1/1/2000', periods=1000))
ts = ts.cumsum()

ts.plot()

# On DataFrame, plot() is a convenience to plot all of the columns with labels:

df = pd.DataFrame(np.random.randn(1000, 4), index=ts.index,
                  columns=['A', 'B', 'C', 'D'])
df = df.cumsum()

plt.figure(); df.plot(); plt.legend(loc='best')

### CSV

# Writing to a csv file
df.to_csv('foo.csv')

# Reading from a csv file
pd.read_csv('foo.csv')

### Excel

# Reading and writing to MS Excel

# Writing to an excel file
df.to_excel('foo.xlsx', sheet_name='TestDF')

# Reading from an excel file
pd.read_excel('foo.xlsx', 'TestDF', index_col=None, na_values=['NA'])
