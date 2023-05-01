Notes on oip_py Development
-------------------------------------

To get started: see "Notes on oip_py Workspace setup.md"

## 20230427 Progress
- Working to reproduce following spreadsheet functionality
    - model_workbook_filename = "OIP2021v30r06.xlsm"
    - model_sheet_name = "OilImportPremium2017"

## Notes on program organization and files/modules
### Python files
- OIP.py
    - imports: 
        - numpy as np
        - rand_dists_added as rda
    - `init_OIP(replicable=False)`: Initialize variables, parameters, and random functions for OIP.
    - `OIP_default_switches`
    - `test_mult_cases(num_samples=1)` test utility to complete one OIP calculation or set of variant calculations
    - `eval_one_case()`: Evaluation of a single case (Monte Carlo iteration, year, input set)
    - `calcBaseVars()`

- rand_dists_added.py
    - `risk_discrete(xvals=[],probs=[],count=1)`: generate values from the enumerated elements of a discrete distribution.\n
    - `risk_triangular(XLowBnd,XMode,XUpBnd,count=1)` generate values from a triangular distribution.\
    - `risk_rtriangular(XUpBnd,XMode,XLowBnd,count=1)`: generate values from a triangular distribution.\n (Triangle parameters in reverse order (XUpBnd, XMode, XLowBnd, count)).\n
    - `risk_cumul(XLowBnd,XUpBnd,CumProbList=[],XList=[],count=1,debug=False)`: generate values sampled from the distribution specified as a piecewise linear CDF.\n
    - `risk_function_dict`

- sheet_utils.py
    - import
        - from xlrd import open_workbook, cellname, cellnameabs, colname
    - `colnum_to_name(col=0)`: convert integer column number to characters(s) used in Excel
    - `colname_to_num(cn='')`: convert character string used in Excel to designate columns to integer column number
    - `cellname_to_rowcolnum(cn='')`: convert character string used in Excel to designate column-row cell reference to integer column number and row number
    - `test_cellname(cellnamestr='')`:
    - `sheet_find_errors(sheet,startrow=0,startcol=0,endrow=-1,endcol=-1,verbose=False)`:
    - `read_range(sheet,startrow=0,startcol=0,endrow=-1,endcol=-1,verbose=False,substitute_errors=True)`:  Reads the designated range from the specified spreadsheet sheet object.
    - `read_sheet_test(sheet)`
    - `read_openbook_numberedsheet_range(book,sheetnum=0,startrow=0,startcol=0,endrow=-1,endcol=-1,verbose=False)`:  Opens an excel workbook 'filename', and reads the designated range from the designated sheet number.
    - `read_openbook_namedsheet_range(book, sheetname='',startrow=0,startcol=0,endrow=-1,endcol=-1,verbose=False)`: Given an open excel workbook 'book', reads the designated range from the designated sheet number.
    - `read_book_numberedsheet_range(filename='',sheetnum=0,startrow=0,startcol=0,endrow=-1,endcol=-1,verbose=False)`: Opens an excel workbook 'filename', and reads the designated range from the designated sheet number.
    - `read_book_namedsheet_range(filename='',sheetname='',startrow=0,startcol=0,endrow=-1,endcol=-1,verbose=False)`: Opens an excel workbook 'filename', and reads the designated range from the sheet designated by name.
    - `read_book_rangenames(filename,sheetnum=0)`: open an excel workbook and return the dictionary of named ranges
    - `compare_sheet_ranges(filename1,filename2,sheet=0,sr=0,sc=0,er=-1,ec=-1,offsetrow=0,offsetcol=0)`: returns numpy array of differences, file2-file1, over range

- utilities.py
    - `column_from2DList(li=[],colwanted=0)`: extract a single column from a 2-dim list, return it as a list
    - `matrix_from2DList(li=[],startrow=0,startcol=0,endrow=-1,endcol=-1)`: extract a matrix (rectangular region) form a 2-dim list, return it as a list
    - `deal_with_missing_obs()`: superceded: It is more robust to use a NaN to represent a missed data point.
    - `percentile(N, percent, key=lambda x:x)`: Find the percentile of a list of values. (avail in scipy.stats)
    - `Lag(x, L=1, fillval = numpy.NaN)`: Lag an array of floating point values.
    - import
        - functools (for median)

- testOIP.py
    - imports:
        - import OIP  # for test_mult_cases, test_one_case
        - import rand_dists_added as rda  # random number generation
        - import sheet_utils as su  # specify ranges, read workbooks, sheets and ranges
        - import utilities  # for column_from2DList
    - `gen_test_means(rvDict, samplesz=10, debug=False)`: generate random sample for random variables in dictionary 'OIP.parameter_probabilities'
    - `linkto_workbook(wb_name)`
    - `read_OIPRandomFix(book)`: read model excel sheet for some key params and switches
    - `read_OIPswitches(book)`: read model excel sheet for run switch values
    - `read_OIP_market_data(book)`: Read oil market data (corresponding to some AEO version) from OIP AEOData worksheet.
    - `set_market_data_for_year(md, year=2015)`: select market data for a particular year
    - `pi_component_names` names of premium components to be calculated over sample
    - `pi_stat_names` stats to be measured for each component
    - `simulate_OIP(num_samples=1)`: simulate OIP calculation num_samples times for one year and param distributions
    - `result_stats(results, component_names, debug=False)`: return a numpy array of statistics for each variable in component names
    - `sim_OIP_over_years(num_samples=1, yearlist=[])`: Simulate OIP model for samplesize `num_samples`, across years specied in `yearlist`
    - `loadtest_OIPRandomFix()`: read model excel sheet for RandomFix param values & switches, and update values for fixed case in global `alt_parameter_cases`, and recompute premium components to test replication vs excel
    - `gen_yearly_result_stats(yrly_rslts, component_names)`: Generate statistics by year from a "yrly_rslts", a dictionary of simulation results by year
    - `run_OIP(num_samples=1, yearstep=5)`: Execute OIP model for samplesize "num_samples", across full time horizon with time step "yearstep"
    - `save_results(full_results)`:
    - `read_results(filename="")`
    - `dict_to_array(d)`
    - `save_stats_to_CSV(rslts, filename="")`: write each row of the results data structure to specified filename

- Program Basic Execution Sequence:
    - `testOIP.loadtest_OIPRandomFix()`
    - `testOIP.sim_OIP_over_years(num_samples=-1, yearlist=[2015])`



### R files
- OIP_postprocess.Rmd
    - reads all output xlsx files from OIP runs, for given `model_versionyear`, `model_subversion` and `runset <- paste0("r0", 1:4)`


