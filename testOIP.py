# -*- coding: utf-8 -*-
"""
testOIP.py

Revised 2018_07_03

@author: P.N. Leiby
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import pprint
import pandas as pd

# os.chdir("d:/")         # for Windows system at work
os.chdir("/Users/pzl/Documents")   # for Mac/OSx system
os.chdir("papers/2006OilImportPremium/Analysis/OIPpySecurityPremium")
os.chdir("OIP_py")

import OIP
import rand_dists_added as rda
import sheet_utils as su
import utilities


"""
vals = [1, 2, 3]
probs = [0.2,0.7,0.1]

rv = rda.risk_discrete(vals,probs,100000)
currplot = plt.hist(rv,3)
plt.hist(rv,7,label="discrete dist")
plt.title("Experimenting with Distributions")
plt.ylabel("Count")

# testing cumulative dist
rv = rda.risk_cumul(0,6,[0.1,0.5,0.9],[0.25,1,4],10)

kl = OIP.alt_parameter_casesparameter_probabilities.keys()
for k in kl:
    OIP.parameter_probabilities[k].append(OIP.alt_parameter_cases[k][:-1])
"""

# Objective: Use dataframe object from pandas
# Update: the pandas dataframe is far more established at this point, and is preferred

# For each random variable $X$ in the dictionary *rvDict*, generate *samplesz* samples $X_i$ according to the specified distribution type and parameters.

def gen_test_means(rvDict, samplesz=10, debug=False):
    """generate random sample for random variables in dictionary 'OIP.parameter_probabilities'

    rvDict -- dictionary of random variables, each entry giving name and list
    samplesz -- number of samples for each r.v. (default = 10)
    debug -- boolean if debug printouts wanted (default = False)
    return dictionary with samples for each random variable
    """
    # get keys to random parameters
    kl = rvDict.keys()

    # for k in kl:    # pick up probabilities and append alternative values (dropping right columns with mean and a given sample)
    #     OIP.parameter_probabilities[k].append(OIP.alt_parameter_cases[k][:-2])
    samples = {}
    for k in kl:
        # pick up probabilities and append alternative values (dropping right columns with mean and a given sample)
        pp = rvDict[k]
        xv = OIP.alt_parameter_cases[k][:-2]
        if pp[0] == "risk_discrete":
            samples[k] = rda.risk_function_dict[pp[0]](xv,pp[1],count=samplesz)
        elif (pp[0] == "risk_triangular" or pp[0] == "risk_rtriangular"):
            samples[k] = rda.risk_function_dict[pp[0]](*xv,count=samplesz)
        elif pp[0] == "risk_cumul":
            xv.sort()
            samples[k] = rda.risk_function_dict[pp[0]](pp[1][0],pp[1][1],pp[1][2],xv,count=samplesz)
        else:
            samples[k] = np.zeros(samplesz)*np.NaN
        if debug:
            expected_mean = OIP.alt_parameter_cases[k][3]
            if (expected_mean==0.0):
                if (samples[k].mean() ==0.0):
                    mratio = 1.0
                else:
                    mratio = np.NaN
            else:
                mratio = samples[k].mean()/expected_mean
            # print k, "samplesz=", len(samples[k]), "mean:",samples[k].mean(), "ratio:",mratio
            print "%30s samplesz: %7d mean: %8.5f ratio: %8.5f" % (str(k)[:30], len(samples[k]), samples[k].mean(), mratio)
    # Special treatment of this one element (ugly)
    samples["Elas:Other NonOPEC Demand"] = - samples["Elas:Other NonOPEC Supply"]
    return(samples)


def linkto_workbook():
    # os.chdir(r"\Papers\2009LCFSTradableCredits\Analysis\EnergySecurity\OIP_py")
    wb_name ="Oil_Import_Premium_2005_risk_v21main_2011Dev_v14.xls"
    book = su.xlrd.open_workbook(wb_name)
    return(book)


def read_OIPRandomFix(book):
    # Warning: no error checking on read
    wbdata = su.read_openbook_namedsheet_range(book, sheetname='OilImportPremium2005',startrow=0,startcol=su.colname_to_num(cn='A'),endrow=72,endcol=su.colname_to_num(cn='T'))
    #wbdata = sheet_utils.read_sheet_range(filename=wb_name,sheetnum=2)
    KeyParameterDescriptors = utilities.column_from2DList(wbdata,0)[4:29]
    # print(KeyParameterDescriptors)
    KeyParameterRandomFix = utilities.column_from2DList(wbdata,su.colname_to_num(cn='S'))[4:29]
    # get the solution:
    KeyParameterDescriptors.append(wbdata[65][0])
    KeyParameterRandomFix.append(wbdata[65][4])
    kp_rfix = {}
    kp_pairs = zip(KeyParameterDescriptors,KeyParameterRandomFix)
    for kp,kf in kp_pairs:
        kp_rfix[kp] = kf
    return(kp_rfix)

def read_OIPswitches(book):
    # Warning: no error checking on read
    wbdata = su.read_openbook_namedsheet_range(book, sheetname='OilImportPremium2005',startrow=0,startcol=su.colname_to_num(cn='A'),endrow=10,endcol=su.colname_to_num(cn='H'))
    switches = [int(round(wbdata[0][su.colname_to_num(cn='G')])),    # 2010 Switch_AEOVersion
                int(round(wbdata[2][su.colname_to_num(cn='G')])),    # 2015,    # Switch_Year
                wbdata[3][su.colname_to_num(cn='G')],    # 1.0,     # Switch_DomDem_ElasMult
                wbdata[4][su.colname_to_num(cn='G')]]    # 1.0     # Switch_ConstrOECDEurDemand      return(kp_rfix)
    return(switches)

def reload_OIPRandomFix():
    random_fix_index=4
    bk = linkto_workbook()
    kprf = read_OIPRandomFix(bk)
    for k in kprf:
        if k in OIP.alt_parameter_cases:
            OIP.alt_parameter_cases[k][random_fix_index]= kprf[k]
        else:
            print("Skipping: ",k)
    OIP.OIP_default_switches = read_OIPswitches(bk)
    print("OIP switches: ",OIP.OIP_default_switches)
    # solve the case and compare
    OIP_solution_for_pi = OIP.test_mult_cases(num_samples = -1)
    print(OIP_solution_for_pi)
    if (kprf["Total"] ==0.0):
        if (OIP_solution_for_pi[0] ==0.0):
            mratio = 1.0    # indicate match
        else:
            mratio = np.NaN
    else:
        mratio = OIP_solution_for_pi[0]/kprf["Total"]
        # print k, "samplesz=", len(samples[k]), "mean:",samples[k].mean(), "ratio:",mratio
        print "%30s samplesz: %7d value: %8.5f ratio: %8.5f" % ("Total pi", 1, OIP_solution_for_pi[0], mratio)
    return(kprf)

def read_OIP_market_data(book):
    """ Read oil market data (corresponding to some AEO version) from OIP worksheet.

    book -- opened workbook object. Warning: no error checking on read.\n
    return dictionary of data series (each a numpy array)
    """
    wbdata = su.read_openbook_namedsheet_range(book, sheetname='AEOData',startrow=556,startcol=su.colname_to_num(cn='B'),endrow=577,endcol=su.colname_to_num(cn='AI'))
    market_data = {}
    for r in wbdata:
        market_data[r[0]] = np.array(r[2:])    # drop blank col and 2005 col w/ incomplete data
    return(market_data)

def set_market_data_for_year(md,year=2015):
    for n in range(len(md["Year"])):
        if int(round(md["Year"][n])) == year:
            break
    # print "Year %4d is element %3d in md." % (year,n)
    curr_mkt_parameter_cases = {}
    for k in OIP.oilmkt_parameter_cases:
        if k not in md:
            print "Missing market data for: ",k
        else:
            curr_mkt_parameter_cases[k] = md[k][n]
            OIP.oilmkt_parameter_cases[k][1] = md[k][n]    # WARNING: sets only the Midcase values for AEO
    return(curr_mkt_parameter_cases)

pi_component_names = ["pi_tot",               "pi_m",               "pi_di",                    "pi_dm",              "pi_d",
                     "E_MCdis_vul_monops_k",  "E_MCdis_vul_dGDP_k", "E_MCdis_vul_dDWL_k",       "E_MCdis_vul_dFC_k",  "E_MCdis_vul_deGDP_k",
                     "E_MCdis_size_dSSdDWL_k","E_MCdis_size_dFC_k", "E_MCdis_size_dGNPdDelP_k", "MCmonopsony_k"]

def simulate_OIP(num_samples = 1):
    global alt_parameter_cases,disrSizes,dirsProbs, OIP_default_switches
    global pi_component_names
    num_tracked_vars = len(pi_component_names)
    switches = OIP.OIP_default_switches
    if num_samples == -1:    # debug - use default values
        sample_results = np.array(OIP.eval_one_case(OIP.alt_parameter_cases,OIP.disrSizes,OIP.disrProbs,switches,debug=True))
    else:
        sam = gen_test_means(rvDict=OIP.parameter_probabilities, samplesz=num_samples)    # random values for random parameters
        random_fix_index=4
        sample_results = np.ones([num_samples,num_tracked_vars])
        for n in range(num_samples):
            for k in sam:    # loop over parameters in dictionary of sampled parameters
                if k in OIP.alt_parameter_cases:
                    OIP.alt_parameter_cases[k][random_fix_index]= sam[k][n]
                else:
                    print("Skipping: ",k)
            # switches[2] = 1.0+np.random.normal(0.0,0.25) # Switch_DomDem_ElasMult
            sample_results[n]= np.array(OIP.eval_one_case(OIP.alt_parameter_cases,OIP.disrSizes,OIP.disrProbs,switches)[:14])    # gather all returned values, truncating if necessary
            if np.isnan(sample_results[n][0]):
                print OIP.eval_one_case(OIP.alt_parameter_cases,OIP.disrSizes,OIP.disrProbs,switches)
                pprint.pprint(switches)
                for k in OIP.alt_parameter_cases:
                    if not k== "KEY_PARAMETERS_ASSUMPTIONS":
                        print "%30s  %8.5f" % (str(k)[:30], OIP.alt_parameter_cases[k][random_fix_index])
            if n % 1000 == 0: print "  iteration ",n
    return sample_results

from scipy import stats
def result_stats(results, component_names, debug = False):
    """return a numpy array of statistics for each variable in component names

    results -- array of random outcomes for each variable in component_names
    component_names -- list of random variate names
    debug -- boolean indicating if debugging info to be printed (default = False)
    """
    numstats = 6    # number of statistics tracked
    numvars = len(component_names)
    ystats = np.zeros([numstats,numvars])
    ystats[0] = np.mean(results,axis=0)    # "Mean:            "  axis is dimension across which statistic is calculated (rows)
    ystats[1] = np.std(results,axis=0)     # "Stddev           "
    ystats[2] = np.min(results,axis=0)     # "Min:             "
    for n in range(numvars):
        ystats[3,n] = stats.scoreatpercentile(results[:,n],5.0)     # "5th percentile:  "
        ystats[4,n] = stats.scoreatpercentile(results[:,n],95.0)    # "95th percentile:  "
    ystats[5] = np.max(results,0)     # "Min:             "

    if debug:
        print "Mean:            ", (np.mean(results,0))    # these functions work along specified axis for all variables
        print "stddev:          ", (np.std(results,0))
        print "Min:             ", (np.min(results,0))
        print "5th percentile:  ", (stats.scoreatpercentile(results[:,0],5.0))
        print "95th percentile: ", (stats.scoreatpercentile(results[:,0],95.0))
        print "Max:             ", (np.max(results,0))
        plt.plot(ystats.transpose())
    return(ystats)

def sim_OIP_over_years(num_samples=1,yearlist=[]):
    """Execute OIP model for samplesize "num_samples", across years specied in "yearlist"
       Returns
         "yrly_rslts", a dictionary of simulation results for each year.
    """
    bk = linkto_workbook()
    md = read_OIP_market_data(bk)
    yrly_rslts = {}
    for year in yearlist:
        set_market_data_for_year(md,year)
        print "Starting year: %5d, base oil price %8.3f" % (year, OIP.oilmkt_parameter_cases["import oil price"][1])
        yrly_rslts[year]= simulate_OIP(num_samples)
    return(yrly_rslts)

def gen_yearly_result_stats(yrly_rslts, component_names):
    """Generate statistics by year from a "yrly_rslts", a dictionary of simulation results by year
       Returns
         "yearly_stats" dictionary of summary statistics for each year, and
    """
    yrly_stats = {}
    for year in yrly_rslts:
        yrly_stats[year]= result_stats(yrly_rslts[year],component_names)
    return(yrly_stats)

def run_OIP(num_samples=1,yearstep=5):
    """Execute OIP model for samplesize "num_samples", across full time horizon with time step "yearstep"

       num_samples -- number of samples to run in Monte Carlo process (default=1)
       yearstep -- interval between the years for which simulations are to be done (default=5)
       Returns
         "yearly_stats" dictionary of summary statistics for each year, and
         "yearly_results" dictionary of simulation results for each year.
    """
    global pi_component_names
    years = range(2010,2036,yearstep)
    yearly_rslts = sim_OIP_over_years(num_samples,years)
    yearly_stats = gen_yearly_result_stats(yearly_rslts,pi_component_names)
    return(yearly_stats,yearly_rslts)

import pickle
def save_results(full_results):
    outfileptr = open("results1.pkl","wb")
    pickle.dump(full_results,outfileptr)
    outfileptr.close()

def read_results(filename = ""):
    pkl_file_ptr = open(filename,"rb")
    return(pickle.load(pkl_file_ptr))

def dict_to_array(d):
    # assumes that each element of dictionary is of same shape
    ar = np.zeros([len(d.keys()),np.shape(d[d.keys()[0]])])
    print("Key  "+d.keys())
    print("Key length "+str(len(d.keys())))
    for i in range(len(d.keys())):
        ar[i] = d[d.keys()[i]]
        # ???Where was this going?
        # Will not work if dictionary elements are anything other than equal-length vectors

# FIX/IMPROVE: (20151205)
# Better to do all of the following with dataframes, and
# library routines to write (melted/long-form) dataframes to csv

#"""
#    writer = csv.writer(open("OIPV014_BaseStatsR2.csv","wb"))
#    for s in range(6):
#        writer.writerow(rslts[1].keys())
#        for p in range(len(pi_component_names)):
#            writer.writerow(rsltstats[:,s,p])
#    writer = None
#"""

import csv

def save_stats_to_CSV(rslts,filename=""):
    """write each row of the results data structure to specified filename

    Returns nothing
    Warning: no error-checking of I/O
    """
    if filename=="":
        filename = "OIPV014_BaseStats.csv"
    writer = csv.writer(open(filename,"wb"))
    for y in rslts[0]: # loop over years
        writer.writerow(y)
        writer.writerows(rslts[0][y])

# Execution area
annual_stats,annual_rslts = run_OIP(num_samples=10000,yearstep=5)

np.size(annual_rslts)  # annual_rslts is a dictionary, so size gives little info
annual_rslts.keys()
np.size(annual_rslts[2020])

# save_stats_to_CSV(annual_rslts,"testResults.csv") # does not work b.c. expects an array, not dictionary
