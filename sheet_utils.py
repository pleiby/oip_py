"""sheet_utils:
   Functions for reading Excel workbook sheets or ranges in a specified sheet.
   Ver. 0.1. by P.N. Leiby
"""

from xlrd import open_workbook, cellname, cellnameabs, colname
import xlrd
import numpy

_A2Z = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_029 = "0123456789"

def colnum_to_name(col=0):
    """convert integer column number to characters(s) used in Excel
       Duplicates xlrd.colname
    """
    global _A2Z
    if col>25:
        return(_A2Z[col/26]+_A2Z[col % 26])
    else:
        return(_A2Z[col % 26])

def colname_to_num(cn=''):
    """convert character string used in Excel to designate columns to integer column number
       Assume column string is case insensitive.  Return -1 if invalid column string.
    """
    global _A2Z
    cnu = cn.upper()
    if len(cnu) == 2:
        base = 26*(_A2Z.find(cnu[0])+1)
        offset = _A2Z.find(cnu[1])
    elif len(cnu) == 1:
        base = 0
        offset = _A2Z.find(cnu[0])
    else:
        return(-1)    # error code
    return(base+offset)
    
def cellname_to_rowcolnum(cn=''):
    """convert character string used in Excel to designate column-row cell reference to integer column number and row number
       Returns ordered pair of integers (row,col), where A1 maps to (0,0) and A2 maps to (1,0).
       Assume column string is case insensitive.  Return -1 if invalid column string.
    """
    global _A2Z, _029
    cnu = cn.upper()
    colchars = []
    rowchars = []
    for c in cnu:
        # FIXME: current logic allows mixed ordering of letters and digits
        if c in _A2Z:    # this is very crude.  Need to use re module
            colchars.append(c)
        if c in _029:
            rowchars.append(c)
    return(int(''.join(rowchars))-1,colname_to_num(''.join(colchars)))
    
def test_cellname(cellnamestr=''):
    rc = cellname_to_rowcolnum(cellnamestr)
    return(cellname(rc[0],rc[1]))        # should return cellnamestr

def sheet_find_errors(sheet,startrow=0,startcol=0,endrow=-1,endcol=-1,verbose=False):
    if verbose:
        print('Sheet name: ',sheet.name)
        print('with ',sheet.nrows,' rows and ',sheet.ncols,' cols')
    # default is to read entire sheet, if endrow, endcol not specified.
    if (endrow==-1): endrow = sheet.nrows    # slight violation of convention that -1 is index of last element
    if (endcol==-1): endcol = sheet.ncols
    # Tests type of each cell (cell.ctype)    
    # Type symbol    Type number    Python value
    #  XL_CELL_EMPTY    0    empty string u''
    #  XL_CELL_TEXT     1    a Unicode string
    #  XL_CELL_NUMBER   2    float
    #  XL_CELL_DATE     3    float
    #  XL_CELL_BOOLEAN  4    int; 1 means TRUE, 0 means FALSE
    #  XL_CELL_ERROR    5    int representing internal Excel codes; for a text representation, refer to the supplied dictionary error_text_from_code
    #  XL_CELL_BLAN     6    empty string u''. Note: this type will appear only when open_workbook(..., formatting_info=True) is used.
    # If type is XL_CELL_Error, then uses xlrd.error_text_from_code (variable)
    # This dictionary can be used to produce a text version of the internal codes that Excel uses for error cells. Here are its contents:
    #  0x00: '#NULL!',  # Intersection of two cell ranges is empty
    #  0x07: '#DIV/0!', # Division by zero
    #  0x0F: '#VALUE!', # Wrong type of operand
    #  0x17: '#REF!',   # Illegal or deleted cell reference
    #  0x1D: '#NAME?',  # Wrong function or range name
    #  0x24: '#NUM!',   # Value range overflow
    #  0x2A: '#N/A!',   # Argument or function not available
    for row_index in range(startrow,endrow):
        if (row_index) in range(startrow,endrow):
            if verbose: print("Row ",row_index)
            row_cells = sheet.row_slice(row_index,startcol,endcol)
            for cell in row_cells:
               if cell.ctype == xlrd.XL_CELL_ERROR:
                   print(xlrd.error_text_from_code[cell.value]),
    
def read_range(sheet,startrow=0,startcol=0,endrow=-1,endcol=-1,verbose=False,substitute_errors=True):
    """Reads the designated range from the specified spreadsheet sheet object.
    Defaults are to read all of the sheet.
    Returns a list of sheet rows, each a list of cell values.
    """
    if verbose:
        print('Sheet name: ',sheet.name)
        print('with ',sheet.nrows,' rows and ',sheet.ncols,' cols')
    # default is to read entire sheet, if endrow, endcol not specified.
    if (endrow==-1): endrow = sheet.nrows    # slight violation of convention that -1 is index of last element
    if (endcol==-1): endcol = sheet.ncols

    cell_values_read = []
    #for row_index in range(sheet.nrows):
    for row_index in range(startrow,endrow):
        # following faster approach does not check for error values
        cell_values_read.append(sheet.row_values(row_index,startcol,endcol))
        if substitute_errors:
            cell_types = sheet.row_types(row_index,startcol,endcol)
            for n in range(len(cell_types)):
                if cell_types[n] == xlrd.XL_CELL_ERROR:
                    if cell_values_read[-1][n]==0x2A:
                        cell_values_read[-1][n] = numpy.NaN
                    else:
                        cell_values_read[-1][n]= xlrd.error_text_from_code[cell_values_read[-1][n]]
        # if verbose: print(" Row ", row_index, cell_values_read[-1])
        # cell-by-cell approach needed if we are to handle excel error cells
        # (still do no specially process cells of type Text, Date, Boolean, or Empty)
        # if (row_index) in range(startrow,endrow):
        #    row_cells = sheet.row_slice(row_index,startcol,endcol)
        #    cell_values_read.append([])
        #    if verbose: print("Row ",row_index)
        #    for col_index in range(sheet.ncols):
        #        if (col_index) in range(startcol,endcol):
        #            values_read[row_index-startrow].append(sheet.cell(row_index,col_index).value)
        #            cell_values_read[-1].append(sheet.cell(row_index,col_index).value)
        #            if verbose: print(" Col ", col_index, " Value: ",sheet.cell(row_index,col_index).value)
        #    if verbose: print   # follow each row with linefeed
    return(cell_values_read)

def read_sheet_test(sheet):
    print(sheet.row_slice(0,1))
    print(sheet.row_slice(0,1,2))
    print(sheet.row_values(0,1))
    print(sheet.row_values(0,1,2))
    print(sheet.row_values(5,0))             # print row 5, col0 to end
    print(sheet.row_values(5,0,sheet.ncols))   # print row 5, col0 to ncols
    print(sheet.row_values(5,0,-1))            # print row 5, col0 to ncols
    


def read_openbook_numberedsheet_range(book,sheetnum=0,startrow=0,startcol=0,endrow=-1,endcol=-1,verbose=False):
    """Opens an excel workbook 'filename', and reads the designated range from the designated sheet number.
    Defaults are to read all of first sheet.
    Returns a list of sheet rows, each a list of cell values.
    """
    sheet = book.sheet_by_index(sheetnum)
    return(read_range(sheet,startrow,startcol,endrow,endcol,verbose))

def read_openbook_namedsheet_range(book, sheetname='',startrow=0,startcol=0,endrow=-1,endcol=-1,verbose=False):
    """Given an open excel workbook 'book', reads the designated range from the designated sheet number.
    Defaults are to read all of first sheet.
    Returns a list of sheet rows, each a list of cell contents (values, text or error)
    """
    sheet = book.sheet_by_name(sheetname)
    return(read_range(sheet,startrow,startcol,endrow,endcol,verbose))

def read_book_numberedsheet_range(filename='',sheetnum=0,startrow=0,startcol=0,endrow=-1,endcol=-1,verbose=False):
    """Opens an excel workbook 'filename', and reads the designated range from the designated sheet number.
    Defaults are to read all of first sheet.
    Returns a list of sheet rows, each a list of cell values.
    """
    # TODO Badly in need of exception handling (for no file or numbered sheet)
    book = open_workbook(filename)
    return(read_openbook_numberedsheet_range(book,sheetnum,startrow,startcol,endrow,endcol,verbose))

def read_book_namedsheet_range(filename='',sheetname='',startrow=0,startcol=0,endrow=-1,endcol=-1,verbose=False):
    """Opens an excel workbook 'filename', and reads the designated range from the sheet designated by name.
    Defaults are to read all of named sheet.
    Returns a list of sheet rows, each a list of cell values.
    """
    # TODO Badly in need of exception handling (for no file or named sheet)
    book = open_workbook(filename)
    return(read_openbook_namedsheet_range(book,sheetname,startrow,startcol,endrow,endcol,verbose))


# def read_named_sheetcontent_range(filename='',sheetname='',startrow=0,startcol=0,endrow=-1,endcol=-1,verbose=False):
#     """Opens an excel workbook 'filename', and reads the designated range from the designated sheet number.
#     Defaults are to read all of first sheet.
#     Returns a list of sheet rows, each a list of cell contents (values, text or error)
#     """
#     book = open_workbook(filename)
#     return(read_sheetcontent_range(book, sheetname, startrow, startcol, endrow, endcol, verbose))

# Examplse usage of cellname, cellnameabs,colname
# print(cellname(0,0),cellname(10,10),cellname(100,100))
# print(cellnameabs(3,1),cellnameabs(41,59),cellnameabs(265,358))
# print(colname(0),colname(10),colname(100))

def read_book_rangenames(filename,sheetnum=0):
    """open an excel workbook and return the dictionary of named ranges
    """
    book = open_workbook(filename)
    return book.name_map

def compare_sheet_ranges(filename1,filename2,sheet=0,sr=0,sc=0,er=-1,ec=-1,offsetrow=0,offsetcol=0):
    """ returns numpy array of differences, file2-file1, over range
    """
    data1 = numpy.array(read_book_numberedsheet_range(filename=filename1,sheetnum=sheet,startrow=sr,startcol=sc,endrow=er,endcol=ec))
    data2 = numpy.array(read_book_numberedsheet_range(filename=filename2,sheetnum=sheet,startrow=sr+offsetrow,
                                      startcol=sc+offsetcol,endrow=er+offsetrow,endcol=ec+offsetcol))
    diff = data2-data1
    return diff

