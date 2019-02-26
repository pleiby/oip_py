# Utilities.py

def column_from2DList(li=[],colwanted=0):
    """extract a single column from a 2-dim list, return it as a list
    """
    return [row[colwanted] for row in li] 
    
def matrix_from2DList(li=[],startrow=0,startcol=0,endrow=-1,endcol=-1):
    """extract a matrix (rectangular region) form a 2-dim list,
       return it as a list.  
       endrow and endcol are non-inclusive range bounds, consistent with python range limits.
    """
    matlist = []
    if endrow==-1: endrow = len(li)+1
    for row in range(len(li)):
        if (row) in range(startrow,endrow):
            if endcol==-1:
                matlist.append(li[row][startcol:])
            else:
                matlist.append(li[row][startcol:endcol])
    return(matlist)

def deal_with_missing_obs():
    """It is more robust to use a NaN to represent a missed data point. Then when you 
    load your data, your arrays will be the same length. There is already some 
    support for plotting data with NaNs in it, but the preferred solution is to 
    take a further step and use a masked array to mask your missing values. For 
    example, at the ipython -pylab prompt:

    time=array([1,2,3,4,5])
    f1=array([1,2,NaN,4,5])
    f1_m=ma.masked_where(isnan(f1),f1)
    plot(f1_m)
  
    That will give you a line with a break in it at  the missed observation.
    
    > Is it possible to interpolate the missing values or to the draw the plot as:
    > on x the time values and on y the f1,f2,f3, represented as a continuous
    > line
    
    If you do not want breaks in your line due to the missed observation, you 
    could interpolate the missing values yourself, but if you just want a 
    continuous line through whatever data you have, you could use numpy's flexible 
    indexing and do:
    
    plot(time[isfinite(f1)], f1[isfinite(f1)])
    """
    return
    
    
    ## {{{ http://code.activestate.com/recipes/511478/ (r1)
import math

# a pure python implementation of percentile w/o scipy.stats library
def percentile(N, percent, key=lambda x:x):
    """
    Find the percentile of a list of values.

    @parameter N - is a list of values. Note N MUST BE already sorted.
    @parameter percent - a float value from 0.0 to 1.0.
    @parameter key - optional key function to compute value from each element of N.

    @return - the percentile of the values
    """
    if not N:
        return None
    k = (len(N)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(N[int(k)])
    d0 = key(N[int(f)]) * (k-f)
    d1 = key(N[int(c)]) * (c-k)
    return d0+d1

import numpy
def Lag(x, L=1, fillval = numpy.NaN):
    """Lag an array of floating point values.
    Returns an array lagged L times along the first axis.
    """
    xl = x.copy()
    xl.fill(fillval)
    xl[L:] = x[:-L]
    return(xl)
    
    
import functools
# median is 50th percentile.
#  median = functools.partial(percentile, percent=0.5)
## end of http://code.activestate.com/recipes/511478/ }}}