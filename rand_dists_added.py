# -*- coding: utf-8 -*-
"""
rand_dists_added.py
Additional random functions needed to replicate some @risk functionality
"""
import numpy

def risk_discrete(xvals=[],probs=[],count=1):
    """generate values from the enumerated elements of a discrete distribution.\n
       probs and xvals are lists of discrete probabilities and values.\n
       Expect sum of probs should be 1.0, len(prob)==len(xvals)  
       Return a randomly sampled value from xvals
    """
    urv = numpy.random.random(count)    # a numpy array of uniform rvs over 0 to 1.0
    rv = numpy.ones(count)*numpy.NaN
    if count<len(xvals):    # sample small
        for m in range(count):    # loop over possible xvals
            cprob = 0.0
            for n in range(len(xvals)):
                cprob += probs[n]
                if urv[m] <= cprob:
                    rv[m] = xvals[n]
                    break
    else:    # sample is large compared to number of discrete alternative
        cprob = 0.0
        cprobs = []
        for n in range(len(xvals)):
            cprob += probs[n]
            cprobs.append(cprob)
        cprobs[-1]=1.0    # make sure of this.
        test1 = urv>0.0
        for n in range(len(xvals)):
            test2 = urv<=cprobs[n]
            test1 = test1 * test2    # above last and below next bound?
            rv[test1] = xvals[n]    # assign matching value for bin
            test1 = ~test2        # this is array negation, unlike "not"
    return(rv)

def risk_triangular(XLowBnd,XMode,XUpBnd,count=1):
    """generate values from a triangular distribution.\n
       Expect XLowBnd <= XMode <= XUpBnd.\n
       Returns "count" randomly sampled values between XlowBnd and XUpBnd.
    """
    if (XLowBnd>=XUpBnd):
        return(numpy.ones(count)*XLowBnd)
    else:
        return numpy.random.triangular(XLowBnd,XMode,XUpBnd,count)

def risk_rtriangular(XUpBnd,XMode,XLowBnd,count=1):
    """generate values from a triangular distribution.\n
       (Triangle parameters in reverse order (XUpBnd, XMode, XLowBnd, count)).\n
       Expect XLowBnd <= XMode <= XUpBnd.\n
       Returns "count" randomly sampled values between XlowBnd and XUpBnd.
    """
    if (XLowBnd>=XUpBnd):
        return(numpy.ones(count)*XLowBnd)
    else:
        return numpy.random.triangular(XLowBnd,XMode,XUpBnd,count)    
    
def risk_cumul(XLowBnd,XUpBnd,CumProbList=[],XList=[],count=1,debug=False):
    """generate values sampled from the distribution specified as a piecewise
       linear CDF.\n
       XList and CumProbList are lists of values and corresponding cumulative probabilities.
       CDF is assumed linear between specified points.
       Expect CumProbList probs in increasing order, each >0 and <1.0
       Returns "count" randomly sampled values between XlowBnd and XUpBnd.
    """
    xvals = numpy.array([XLowBnd]+XList+[XUpBnd])
    cprobs = numpy.array([0.0]+CumProbList+[1.0])
    urv = numpy.random.random(count)    # a numpy array of uniform rvs over 0 to 1.0
    if debug:
        print "xvals ",xvals
        print "cprobs ", cprobs
        print "urv: ",urv
    rv = numpy.ones(count)*numpy.NaN
    if count< 2: #len(xvals):
        for m in range(count):    # loop over each sample
            x_previous = xvals[0]
            cp_previous = 0.0
            for n in range(len(xvals))[1:]:
                if urv[m] <= cprobs[n]:
                    if debug:
                        print "urv[m]", urv[m], "n", n, "cprobs[n]", cprobs[n]
                        print "x_previous", x_previous, "cp_previous", cp_previous
                        if urv[m] <= cprobs[1]:
                            print m,urv[m]
                    rv[m] = x_previous + (xvals[n]-x_previous)*(urv[m]-cp_previous)/(cprobs[n]-cp_previous)
                    break
                else:
                    x_previous = xvals[n]
                    cp_previous = cprobs[n]
            # NOT NEEDED: rv[m] = xvals[-1]    # default is to return the last value
    else:    # sample is large compared to number of discrete alternative
        rvbins = numpy.ones(count,dtype=numpy.int)    # array of indices must be of type intarray
        bslope = numpy.zeros(len(xvals))
        bbase = numpy.zeros(len(xvals))
        for n in range(len(xvals))[1:]:    # start with second prob, since first constructed to be zero
            bslope[n] = (xvals[n]-xvals[n-1])/(cprobs[n]-cprobs[n-1])
            bbase[n] = xvals[n-1] - cprobs[n-1]*bslope[n]
        test1 = urv>0.0    # an array of booleans. Assume cprobs[0]=0.0.
        rv[~test1] = xvals[0]            # deal with rare/impossible boundary rv
        for n in range(len(xvals))[1:]:    # start with second prob, since first constructed to be zero
            test2 = urv<=cprobs[n]
            test1 = test1 * test2    # in this bin if above last and below this bound
            rvbins[test1] = n
            # assign value for cases in this bin 
            # WARNING: possibility of zero-probability-width bin leading to divide by zero?  but should have no observations
            # rv[test1] = xvals[n-1] + (xvals[n]-xvals[n-1])*(urv-cprobs[n-1])/(cprobs[n]-cprobs[n-1])
            test1 = ~test2        # this is array negation, unlike "not"
        if debug: print "rvbins",rvbins
        rv = bbase[rvbins] + urv*bslope[rvbins]    # use trick indexing by integers arrays
    return(rv)

risk_function_dict = {
"risk_triangular":    risk_triangular,
"risk_rtriangular":   risk_rtriangular,
"risk_discrete":      risk_discrete,
"risk_cumul":         risk_cumul,
}

