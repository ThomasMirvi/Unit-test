# -*- coding: utf-8 -*- 

u"""
 Manipulator with a two-dimensional list
 it was primarily based on mangling data in a Python list, loaded from CSV or SQL sources.

 changes

 2022/05/27 - min_col repair

 2020/10/15 - semiconversion to Python3 format

 2015/12/06 - change In putError to ValueError

"""

__author__    = u"Filip Vaculik (mintaka@post.cz)"
__version__   = u"Revision: 0.9.3"
__date__      = u"Date: 2020/10/15 09:31:23"
__copyright__ = u"Copyright (c) 2007 Filip Vaculik"
__license__   = u"GNU GPL 3"

log = log.info = log.debug = log.warning = lambda *args, **kwargs: None # as dummy logger, if you import own logger it will be overwritten
# from manipulator_globals import *            # can be delete it connect loger and other global parts  # or it can be replaced by your own module with logger
# from globales import log
import datetime
import itertools
from utils import replace_by_sed, create_working_copies
from osutils import listFilesOnLevel
from collections import OrderedDict

from list_2D_manipulator import * # import self


STRIPPED_CHARS = globals().get('STRIPPED_CHARS', ' \'\\"\r\n\t') # space, quote, backslash, double quote, line feed, new line, tabulator
OUTPUT_EOL =  globals().get('OUTPUT_EOL', "\r\n")

# --------------------------------------------------------------------
def enumerate_iter(iterable, start=0):
    u"""Return tuples (index, object), (index, object)
    example: list_2D = [['header1', 'header2'], ['value1', 'value2'],]
    for index, item in enumerate_iter(list_2D[1:], start=1 ): # skip header
        print item
    """
    return itertools.izip(itertools.count(start), iterable)
    

# ------------------------------------------------------------------
def flatten_list_2D(list_2D):
    u"""[['a','b'],['c','d']] -> ['a','b','c','d'] """
    return list(itertools.chain.from_iterable(list_2D))

# ------------------------------------------------------------------
def deflatten_list_2D(flat_iterable):
    u"""['a','b','c','d'] -> [['a'],['b'],['c'],['d']] """
    out = []
    for item in flat_iterable:
        out.append([item])
    return out
    
# --------------------------------------------------------------------
def index_of_value(list_2D, row = 0, value = None):
    """Return numeric index of column, where value is matched
    if not found, return None
    """
    for index, item in enumerate(list_2D[row]):
        if item == value: return index
    else:
        return None
        
# --------------------------------------------------------------------
def indexes_of_values(list_2D, row=0, headers=[], raise_error=True):
    """Return numeric indexes of columns, where values is matched
    if not found, return None
    not check duplicit header names (TODO duplicite check)
    is case sensitive (TODO case sensitive switch)
    """
    log.info(u'Start '+ repr(headers)[:500])
    indexes = []
    for header in headers:
        index = index_of_value(list_2D, row = row, value = header)
        if index is None:
            err_message = 'Invalid List_2D Input Data, header :' + repr(header)[:50]  +' not found'
            log.warning(err_message )
            if raise_error:
                raise ValueError('Invalid List_2D Input Data', err_message)
        else:
            indexes.append(index)

    if len(indexes)==0 and raise_error:
        raise ValueError('Invalid List_2D Input Data', 'Invalid List_2D Input Data, header :'+ repr(header)[:50]  +' not found')
    return indexes
    
# --------------------------------------------------------------------
def indexes_of_values_as_dict(list_2D, row=0, headers=[], raise_error=True):
    """Return indexes of columns as dictionary
    key = header name
    value = index on row
    if not found, return None
    not check duplicit header names (TODO duplicite check)
    is case sensitive (TODO case sensitive switch)
    """
    log.info(u'Start '+ repr(headers)[:500])
    indexes = {}
    for header in headers:
        index = index_of_value(list_2D, row = row, value = header)
        if index is None:
            err_message = 'Invalid List_2D Input Data, header :' + repr(header)[:50]  +' not found'
            log.warning(err_message )
            if raise_error:
                raise ValueError('Invalid List_2D Input Data', err_message)
        else:
            indexes[header] = index

    if len(indexes)==0 and raise_error:
        raise ValueError('Invalid List_2D Input Data', 'Invalid List_2D Input Data, header :'+ repr(header)[:50]  +' not found')
    return indexes
    

# --------------------------------------------------------------------
def col_names_from_firts_row(list_2D, headers = None, try_validate = True, stripped_case_insensitive = False, keep_headers_on_first_row = False,  delete_headers_from_data = True, min_cols = None):
    """Parse first row as header
        validate and return that values in list_2D
        remove all rows which first col have same value like first header
        
        stripped_case_insensitive: headers names are validated stripped and case_insensitive
    """
    log.info(u'Start ')
    # ---- validate not empty
    if list_2D == None or len(list_2D) < 2:  # minimum is 2 rows
        log.warning('Invalid List_2D Input Format:'+ repr(list_2D)[:50]  +'...' )
        raise ValueError('Invalid List_2D Input Format', 'None or less then 2 rows')

    # ----  inital settings
    first_row = list_2D[0]
    
    if headers is None:
        headers = first_row

    first_header = headers[0]
    if stripped_case_insensitive:
        first_header = first_header.strip(' \'-*/\\"').upper()

    # ---- validate min_cols
    if min_cols is None:
        min_cols = 1

    if len(headers) < min_cols:
        log.warning('Expected len:'+ repr(min_cols)  +' Get: '+ repr(len(headers))[:50] )
        raise ValueError('Header Validation', 'Data contain less header cols then min_cols')

    # ---- validate compare
    valid = True
    if try_validate and headers != [ ]:
        if valid and len(headers) != len(first_row):
            valid = False

        if valid and stripped_case_insensitive is True:
            for header, first_row_header in map(None,headers, first_row):
                if header is None or first_row_header is None and first_row_header != header:
                    valid = False
                    break
                elif header.strip(' \'-*/\\"').upper() != first_row_header.strip(' \'-*/\\"').upper():
                    valid = False
                    break

        if valid and stripped_case_insensitive is False:
            if first_row != headers:
                valid = False

    if not valid:
        log.warning('Expected:'+ repr(headers)  +' Get: '+ repr(first_row))
        raise ValueError('Header Validation', 'Data contain non valid header. Expected:'+ repr(headers)  +' Get: '+ repr(first_row))

    # ---- delete headers from first row
    delete_row_counter = 0
    if not keep_headers_on_first_row:
        del list_2D[0]
        delete_row_counter += 1

    # ---- delete another rows with headers
    if delete_headers_from_data:
        if stripped_case_insensitive:
            for i in range(len(list_2D)-1, -1, -1):
                if list_2D[i][0].strip(' \'-*/\\"').upper() == first_header:
                    del list_2D[i]
                    delete_row_counter += 1
        else:
            for i in range(len(list_2D)-1, -1, -1):
                if list_2D[i][0] == first_header:
                    del list_2D[i]
                    delete_row_counter += 1
                

                
    # ----

    log.info(u'End__ '+ repr(headers) +' Deleted headers:'+ repr(delete_row_counter))
    return (list_2D, headers, delete_row_counter)
    

# --------------------------------------------------------------------
def check_header(list_2D, headers, subset, same_index, raise_error):
    u"""Check values in first row od list_2D
    subset = test only presence of header values in first row, skip another values
    if subset is False == false if on first row are another another headers then checked

    same_index == test if values on first row are on same indexes as values in headers (if subset s True, same_index have no consequence)
    raise_error if false
    
    Normaly return false or true
    """
    log.info(u'Start headers:'+repr(headers) +' list_2D[0]'+ repr( list_2D[0]) )
    list_headers = list_2D[0]
    result = True

    if not subset:
        if len(list_headers) != len(headers):
            result = False
            log.info('Differnt lenght of list_2D[0] and headers')
            if raise_error:
                raise ValueError('Differnt lenght of list_2D[0] and headers')

        if same_index and list_headers !=  headers:
            result = False
            log.info('Not Expected headers ')
            if raise_error:
                raise ValueError('Not Expected header. Was expected: ' + repr(headers) + '  get: ' + repr(list_headers))
                
    if subset:
        for value in headers:
            if value not in list_headers:
                result = False
                log.info('Value: ' + repr(value) + ' not found in ' + repr(list_headers))
                if raise_error:
                    raise ValueError(u'Value: ' + unicode(value) + u' not found in ' + u"; ".join(   unicode(value) for value in list_headers ), None )
                break

    return result



# --------------------------------------------------------------------
def insert_column(list_2D, headers=None, on_position = None,  default_value = None, new_header=u'None'):
    u"""Insert column with default value
    if on_position == None    added col on the tail
    if  default_value == None     added None
    if new_header == u'None'      added u'None'

    if  headers is None and new_header is not none, new_header is added to list_2D[0][col_index]
    
    """
    log.info(u'Start len List2D[0]:'+repr(len(list_2D[0])) +' Headers[:50]'+ repr(headers)[:50] +' position:' + repr(on_position) +' position type:' + repr(type(on_position)) + ' DefValue:' + repr(default_value) + ' NewHeader: ' + repr(new_header))
    if on_position is None:                     #  Where to insert column
        col_index = len(list_2D[0])
    elif type(on_position) == int:
        col_index = on_position
    elif isinstance(on_position, str):
        col_index = headers.index(on_position)
    else:
        log.warning(u'Unknown on_position type '+ repr(type(on_position)) )
        raise ValueError('Unknown on_position type ', u'Unknown on_position type '+ repr(type(on_position)))

    if (col_index) > len(list_2D[0]):
        log.warning('Wrong integer position for new column')

    for row_index in range(len(list_2D)):
        list_2D[row_index].insert(col_index, default_value)

    # ----- headers
    if headers is None:
        if (new_header is not None) and (new_header != 'None') and (new_header != u'None'):
            list_2D[0][col_index] = new_header
        log.debug('First row: ' + repr(list_2D[0]))
        return list_2D
    else:
        headers.insert(col_index, new_header)
        log.info('First row: ' + repr(list_2D[0]) +' headers:' + repr(headers) )
        return (list_2D, headers)
        
        
# ------------------------------------------------------------------
def create_duplicate_column(list_2D, source_col, dest_col, transform = lambda x: x):
    u"""Create new column where value is used from source_col
    on the value is aplicated transform function
    """
    log.info(u'Start list len:' + repr(len(list_2D)) + ' source_col: '+ repr(source_col)  )

    for index, row in enumerate_iter(list_2D):
        list_2D[index].insert(dest_col, transform( row[source_col] ) )

    log.info(u'End__' )
    return list_2D


# --------------------------------------------
def col_name_to_index(col_headers, col_header, allow_duplicities = True):
    """Find index of name in array
    if not found, return None
    if found more then one and allow_duplicities is False  return None"""
    log.info(u'Start ' + col_header)
    evidences = col_headers.count(col_header)
    if evidences == 0 or (evidences > 1 and not allow_duplicities):
        output = None
    else:
        output = col_headers.index(col_header)

    log.info(u'End__ ' + repr(output))
    return output

# ------------------------------------------------------------------
def homogenity_check(list_2D, default_min = None, default_max = None, raise_error = False, delete_not_matched = False, return_boolean = False):
    u"""Check if min and max row have same no. of items"""
    log.info(u'Start list_2D len: '+repr(len(list_2D)) +'raise_error :' + repr(raise_error) + ' delete_not_matched :'+ repr(delete_not_matched) )
    log.debug('list_2D[0] '+repr(list_2D[0]))
    
    if list_2D == [ ]:
        log.warning(u'End__ EMPTY List_2D')
        return False

    min_cols = len(list_2D[0]) if default_min is None else default_min
    max_cols = len(list_2D[0]) if default_max is None else default_max
    result   = True
    difference_counter = 0
    
    for i in range(len(list_2D)-1, -1, -1):
        row = list_2D[i]
        if len(row) >= min_cols and len(row) <= max_cols:
            pass
        else:
            difference_counter += 1
            result = False
            if raise_error:
                log.warning(u'Walk from tail, max rows now '+ repr(len(list_2D)) +u' AT ROW '+ str(i) + ' BAD ROW:'+repr(row)[:1000] )
                raise ValueError('Inhomogenous List_2D ', 'Min and Max len(row) are not same.')
                break
            if delete_not_matched:
                del list_2D[i]
            
            # log.debug('min: '+ repr(min_cols) +' max: '+  repr(max_cols) +'row[:50]: ' + repr(row)[:50] )

    log.info(u'End__ ' + repr(result) +' ' + repr(difference_counter) + ' list_2D len: '+ repr(len(list_2D)) )
    if return_boolean:
        if difference_counter > 0: return False
        else: return True
    return list_2D

# ------------------------------------------------------------------
def inhomogeneities_finder(list_2D, default_min = None, default_max = None, delete_not_matched = False):
    u"""serarch for inhomogeneities in lenght of rows
        return inhomogenous lines
    """
    log.info(u'Start len: ' + str(len(list_2D)))

    if list_2D == [ ]:
        log.warning(u'End__ EMPTY List_2D')
        return False

    min_cols = len(list_2D[0]) if default_min is None else default_min
    max_cols = len(list_2D[0]) if default_max is None else default_max
    
    inhomogenous_lines = []
    for i in range(len(list_2D)-1, -1, -1):
        row = list_2D[i]
        if len(row) >= min_cols and len(row) <= max_cols:
            pass
        else:
            inhomogenous_lines.append(row)
            if delete_not_matched:
                del list_2D[i]
            
    log.info(u'End__ len: ' + str(len(list_2D)) )
    return (list_2D, inhomogenous_lines)


# ------------------------------------------------------------------
def longest_row_in_list_2D(list_2D):
    u"""return max length of row"""
    log.info(u'Start ')
    max_len_row = 0
    for row in list_2D:
        if len(row) > max_len_row: max_len_row = len(row)
    log.info(u'End__ max_row:' + repr(max_len_row))
    return max_len_row


# ------------------------------------------------------------------
def delete_columns(list_2D, columns, headers = None, exclude = False, first_row_is_longest = False):
    """Delete cols
    exclude == False   named columns will be deleted
    exclude == True    named columns will be excluded from deletion others are deleted

    first_row_is_longest == True  can speed up searching for max columns if exclude == True
    """
    log.info(u'Start len list_2D[0]: ' + repr(len(list_2D[0])) + ' headers: ' + repr(headers) +' exclude: ' + repr(exclude) +' first_row_is_longest: ' + repr(first_row_is_longest) )
    # ------
    def delete_column(list_2D, column):
        log.debug('Delete column' + repr(column) + ' in list_2D ' + repr(list_2D[0]))
        for i in range(len(list_2D)):
            try:
                del(list_2D[i][column])
            except IndexError:                      # skip errors if column of that index not exist
                continue
        return list_2D

    # ------
    if exclude:                                     # detect indexes of columns that can be deleted
        if first_row_is_longest:
            max_rows = len(list_2D[0])
        else:
            max_rows = longest_row_in_list_2D(list_2D)

        all_rows = range(max_rows)
        colls_to_delete = set(all_rows) - set(columns)
        colls_to_delete = list(colls_to_delete)
        colls_to_delete.sort(reverse=True)
    else:
        colls_to_delete = columns
        columns.sort(reverse=True)

    colls_to_delete.sort(reverse=True)                # deletion more then one column is made from tail of list, higher indexes first

    log.debug('---DEL COLS---> ' + repr(colls_to_delete) )
    for i in colls_to_delete:
        list_2D = delete_column(list_2D, i)
        if headers is not None and len(headers) > i:
            del(headers[i])                            #  delete in headers


    if headers is not None:
        log.info(u'End__ cols: ' + repr(len(list_2D[0])) +' headers : ' + repr(headers) )
        return (list_2D, headers)
    else:
        log.info(u'End__ cols: ' + repr(len(list_2D[0])) )
        return list_2D
        
# ------------------------------------------------------------------
def take_out_columns(list_2D, columns):
    u"""Delete remove columns one by one, teke out create new list of list from given columns.
        If you just need few columns from many it is faster, but need another memmory until
        you delete old list_2D.
     """
     # TODO
        
# ------------------------------------------------------------------
def swap_columns(list_2D, from_index, to_index, headers = None,  delete_small_rows = False):
    u"""indexes are from 0
       swap from 2 on 0 mean shift third column to first position
       expect shifts in homogenous list or in homogenous part of list
       
       [['a','b','c'], [1,2,3] ]  ---> [['c','b','a'], [3,2,1] ]  ! NOT [['c','a','b'], [3,1,2] ]

    """
    log.info(u'---MOVE COLS---> from '+repr(from_index)+ ' to '+ repr(to_index) +' list_2D len:' + repr(len(list_2D)))

    min_len = max(from_index, to_index)

    if delete_small_rows:
        for i in range(len(list_2D)-1, -1, -1):
            if len(list_2D[i]) <= min_len:
                del list_2D[i]

    if min(from_index, from_index) < 0 or max(from_index, to_index) > len(list_2D[0]) or from_index==to_index:
        log.warning(u'swap_columns cannot do that swap indexes are out of range. from: ' + str(from_index) + ' to: ' + str(to_index))
        raise ValueError('swap_columns', 'Index are out of range.')

    line_index = 0
    try:
        for row in list_2D:
            line_index += 1
            row[from_index], row[to_index] = row[to_index], row[from_index]
    except:
        log.error(u'-swap_columns---> from '+repr(from_index)+ ' to '+ repr(to_index) +' row len:' + repr(len(row)) + ' row: '+ repr(row) + ' line_index: ' + repr(line_index) )
        raise ValueError('swap_columns', 'Index are out of range.')

    if headers is not None:
        headers[from_index], headers[to_index] = headers[to_index], headers[from_index]
        log.info(u'End__ row[0]...: ' + repr(list_2D[0])[:50] +' headers : ' + repr(headers) +' list_2D len:' + repr(len(list_2D)) )
        return (list_2D, headers)
    else:
        log.info(u'End__ row[0]...: ' + repr(list_2D[0])[:50] +' list_2D len:' + repr(len(list_2D)) )
        return list_2D
        
# ------------------------------------------------------------------
def swap_columns_feeder(list_2D, swap_rules, headers = None, delete_small_rows = False):
    u"""feed swap_columns function from swap_rules
    [[p,q][r,s][t,u]]  --> swap_columns(   p,q)
    """
    log.info(u'Start ')
    for swap_rule in swap_rules:
        from_index, to_index = swap_rule
        if headers is not None:
            list_2D, headers = swap_columns(list_2D, from_index, to_index, headers, delete_small_rows)
        else:
            list_2D          = swap_columns(list_2D, from_index, to_index, headers, delete_small_rows)

    if headers is not None:
        log.info(u'End__ row[0]...: ' + repr(list_2D[0])[:50] +' headers : ' + repr(headers) )
        return (list_2D, headers)
    else:
        log.info(u'End__ row[0]...: ' + repr(list_2D[0])[:50] )
        return list_2D
        
# ------------------------------------------------------------------
def rearrange_cols(list_2D, new_arrange):
    """Rearrange cols by first row in list_2D as header and new_arrange as new headers
       Do this rearrange on place
       ['1','2','3'],
       ['a','b','c']  rearranged by  ['3','2','1'], ==>   ['3','2','1'],
                                                          ['c','b','a']

    """
    header = list_2D[0]
    header_len = len(header)
    d_headers = {}

    log.info(u'Start old:' + repr(list_2D[0]) + ' new: ' + repr(new_arrange))

    if len(new_arrange) != header_len:
        log.warning('Different headers lengh')
        raise ValueError('rearrange_cols', 'Different headers lengh')
    if len(new_arrange) != len(set(new_arrange)):
        log.warning('Duplicates names of column')
        raise ValueError('rearrange_cols', 'Duplicates names of column')
    for index, value in enumerate(new_arrange):
        if value not in header:
            log.warning('Cannot find column header ' + repr(value))
            raise ValueError('rearrange_cols', 'Cannot find column header')
        else:
            d_headers[index] = header.index(value)
    for row in list_2D:
        if len(row) != header_len:
            log.warning('Different numbers of cols on row' + repr(row))
            raise ValueError('rearrange_cols', 'Different numbers of cols on row')

    for row_index, row in enumerate(list_2D):
        new_row = []
        for new_col_index in range(len(d_headers)):
            new_row.append(list_2D[row_index][d_headers[new_col_index]])
        list_2D[row_index] = new_row

    log.info(u'End__ ')
    return list_2D
    
# ----------------------------------------------------------------------------
def value_to_unicode(value):
    """Input is ('  value  ')
       strip chars and others try to unicode convert to unicode,
       If cannot be converted or is empty return None
    """
    #log.debug('Start: value_to_unicode')
    try:
        retval = unicode(value.strip(STRIPPED_CHARS))
    except:
        return None

    if retval == u"":
        return None
    else:
        return retval

# ----------------------------------------------------------------------------
def value_to_float(value, replace_comma = True, remove_spaces = True):
    """Input is ('  value  ')
       strip chars, convert coma to dot and try convert to float
       If cannot be converted or is empty return None
    """
    #log.debug('Start: value_to_float')
    try:
        if replace_comma:
            if isinstance(value, str):
                value = value.replace(',', '.')
        if remove_spaces:
            if isinstance(value, str):
                value = value.replace(' ','')
                value = value.replace('\xa0', '') # nbsp
        retval = float(value)
    except:
        return None
    return retval

# ----------------------------------------------------------------------------
def value_to_int(value):
    """Input is ('  value  ')
       strip chars and try convert to integer
       If cannot be converted or is empty return None
    """
    #log.debug('Start: value_to_int')
    try:
        retval = int(value)
    except:
        return None
    return retval

# ----------------------------------------------------------------------------
def value_to_date(value, do_raise=True):
    """Input is ('  value  ')
       strip chars and try convert to date
       If cannot be converted or is empty return None
    """
    #log.debug('Start: value_to_int')
    raw_date = value

    if raw_date in [None, ""]:
        ret_date = u""

    elif len(raw_date) == len("1979-12-19T00:00:00"): # --- format from .xls 1979-12-19T00:00:00 ----
        date_part = raw_date[0:10]
        date1Y, date1M, date1D = date_part.split('-')
        ret_date = datetime.date(int(date1Y), int(date1M), int(date1D))

    elif len(raw_date) == len("1979-12-19T00:00:00.000Z"): # --- format from webix javascriptu 1979-12-19T00:00:00.000Z ----
        date_part = raw_date[0:10]
        date1Y, date1M, date1D = date_part.split('-')
        ret_date = datetime.date(int(date1Y), int(date1M), int(date1D))

    elif type(raw_date) == tuple and len(raw_date) == 6:     #--- format (yyyy, mm, dd, hh, mm, ss)
        ret_date = datetime.datetime( *(raw_date)  ).date()

    elif len(raw_date) == 8 and raw_date.isdigit():    #--- format  YYYYmmdd
        ret_date = datetime.date(int(raw_date[0:4]), int(raw_date[4:6]),  int(raw_date[6:8]) )

    elif len(raw_date) >= len("1.1.2000") and len(raw_date) <= len("01.01.2000") and len(raw_date.split(".")) == 3 and len(raw_date.split(".")[2]) == 4 and raw_date.split(".")[2].isdigit():
        date_splitted = raw_date.split(".")
        ret_date = datetime.date( int(date_splitted[2]), int(date_splitted[1]), int(date_splitted[0]))

    elif len(raw_date) == 10 and raw_date[4] == "-" and raw_date[7] == "-":                      #            0123456789
        ret_date = datetime.date(int(raw_date[0:4]), int(raw_date[5:7]),  int(raw_date[8:10]) )  #--- format  YYYY-mm-dd

                                                                                                 #         012345678901
                                                                                                 # format '(2008, 9, 2, 0, 0, 0)'
    elif type(raw_date) in [unicode, str] and len( raw_date.split(",")) == 6:# and  False not in [ raw_date.split(",")[0].strip("(").isdigit(), raw_date.split(",")[1].isdigit(), raw_date.split(",")[2].isdigit()]:
        ret_date = datetime.datetime( int(raw_date.split(",")[0].replace("(","")), int(raw_date.split(",")[1]), int(raw_date.split(",")[2]) ).date()

    elif type(raw_date) in [unicode, str] and len( raw_date.split(".") ) == 3 and not False in [ raw_date.split(".")[0].isdigit(), raw_date.split(".")[1].isdigit(), raw_date.split(".")[1].isdigit() ]:
        splited_raw_date = raw_date.split(".")                #--- format (dd.mm.yyyy,  nebo  dd.mm.yy)
        if len(splited_raw_date[2]) == 2:
            if int(splited_raw_date[2]) <= 25: #TODO it is only for 10 years ahead
                splited_raw_date[2] = "20" + splited_raw_date[2]
            else:
                splited_raw_date[2] = "19" + splited_raw_date[2]

        ret_date = datetime.datetime( int(splited_raw_date[2]), int(splited_raw_date[1]), int(splited_raw_date[0]) ).date()  #TODO, can be converted directly to date
    else:
        ret_date = u""
        log.warning(u"-------> prepare_date Unknown datum: " + repr([ type(ret_date), ret_date, type(raw_date), raw_date])  )

    if do_raise:
        if type(ret_date) not in [datetime.datetime, datetime.date]:
            raise ValueError(u'Cannot convert value: ' + repr(raw_date) + ' to date format')
    return ret_date

# ----------------------------------------------------------------------------
def value_length_histogram(list_2D, col, max_length = None, return_match_rows = False, match_rule = ">999"):
    """
       Count length values in one column
       and save this values to histogram
       
       can retrun rows where value match rule   >1  ==1  <1
       max_lenght is necessary for max index
    """
    log.info('Start:')

    if max_length is None:                    # if max_length not set find longest value
        max_length = longest_row_in_list_2D(list_2D)

    hist = [0] * (max_length + 1)

    if return_match_rows:                  #  create new list of matched
        exec ('match_rows = filter(lambda row: len(row['+str(col)+'])'+ match_rule + ' , list_2D)' )

    for row in list_2D:                    # create histogram
        l = len(row[col])
        hist[l] += 1
        
    # convert hist to list_2D
    hist_2D = []
    for index, value in enumerate(hist):
        hist_2D.append([index, value])

    log.info(u'End__ ')
    if return_match_rows:
        return (hist_2D, match_rows)
    else:
        return  hist_2D
        
# ------------------------------------------------------------------
def histogram_substring_evidences_in_cols(list_2D, value, max_length = None, return_match_rows = False):
    """
       Search in all rows and cols for substring "value"
       Count evidences of value in columns and save this values to histogram

       max_length precount max columns on row
       can retrun rows where value is found
    """
    log.info('Start:')

    if max_length is None:                    # if max_length not set find longest value
        max_length = longest_row_in_list_2D(list_2D)

    hist = [0] * (max_length + 1)
    match_rows = []

    for row in list_2D:                    # create histogram
        found_in_row = False
        for col, item in enumerate(row):
            if item.find(value) > -1:
                hist[col] += 1
                found_in_row = True
        if found_in_row:
            match_rows.append(row)
                
    # convert hist to list_2D
    hist_2D = []

    for index, value in enumerate(hist):
        hist_2D.append([index, value])

    log.info(u'End__ ')
    if return_match_rows:
        return (hist_2D, match_rows)
    else:
        return  hist_2D
        


# ------------------------------------------------------------------
def histogram_unicates_in_col(list_2D, col, skip_values = []):
    """
       Count evidences of every unicate value and save this values to histogram.
       col in which column search
       Can skip rows with this values
    """
    log.info('Start:')

    max_length = longest_row_in_list_2D(list_2D)
    if col >= max_length:
        log.warning('Invalid col setting, some rows are shor then '+ repr(col))
        raise ValueError('Invalid col setting, some rows are shor then', '')

    if len(skip_values) > 0:
        hist = {'**skip_values**': 0}
    else:
        hist = {}

    for row in list_2D:                    # create histogram
        value = row[col]
        if value in skip_values:
            hist['**skip_values**'] += 1
            continue
        if value not in hist:
            hist[value] = 0

        hist[value] += 1

    hist_2D = dict_to_two_column_list_of_list(hist)

    log.info(u'End__ ')
    return hist_2D

        
        
        
# ----------------------------------------------------------------------------
def histogram_rows_length(list_2D, max_length = None, return_match_rows = False, match_rule = ">999"):
    """
       Count how many values (columns) are on rows
       and save this values to histogram

       can retrun rows where value match rule   >1  ==1  <1
       max_lenght for max items in histogram
    """
    log.info('Start list_2D len:' + repr(len(list_2D)) )

    if max_length is None:                    # if max_length not set find longest value
        max_length = longest_row_in_list_2D(list_2D)

    hist = [0] * (max_length + 1)

    if return_match_rows:                  #  create new list of matched
        exec ('match_rows = filter(lambda row: len(row)'+ match_rule + ' , list_2D)' )

    for row in list_2D:                    # create histogram
        l = len(row)
        hist[l] += 1

    # convert hist to list_2D
    hist_2D = []
    for index, value in enumerate(hist):
        hist_2D.append([index, value])

    if return_match_rows:
        log.info(u'End__ match_rows len: '+ repr(len(match_rows)))
        return (hist_2D, match_rows)
    else:
        log.info(u'End__ : ')
        return  hist_2D
        
        
# ------------------------------------------------------------------
def convert_tuple_of_tuples_to_list_of_lists(tuple_2D):
    """Conversion ((1,2,3),('a','b','c'),(4,5,6))  --to->  [[1,2,3],['a','b','c'],[4,5,6]]"""
    log.info(u'Start')
    list_2D = []
    for row in tuple_2D:
        list_2D.append(list(row))

    log.info(u'End')
    return list_2D
    
    

# ------------------------------------------------------------------
def convert_values_on_rows(list_2D, rows, conversion_dict, raise_error):
    u"""On selected rows = [x,y,z,...]
    find and convert values by dict
    
    raise_error == if value from dict not found on row
    """
    
    for row in rows:
        for old_value, new_value in conversion_dict.items():
            if old_value not in list_2D[row]:
                if raise_error:
                    log.warning(u'Cannot convert value: ' + repr(old_value) + ' to '+ repr(new_value) +' In row ' + repr(list_2D[row]) )
                    raise ValueError(u'Cannot convert value: ' + repr(old_value) + ' to '+ repr(new_value) +' In row ' + repr(list_2D[row]))
            else:
                list_2D[row][  list_2D[row].index(old_value)  ] = new_value
                
    return list_2D



        
# ------------------------------------------------------------------
def convert_values_in_column(list_2D, col_index, convert_to = ['float', 'int', 'unicode', 'date'][0], min_ = None, max_ = None, delete_invalid = True, default_value_if_invalid = ['none', 'keep'][0], report_file=None):
    u"""Convert values in column
    can test range from min to max

    default_value_if_invalid set to None or 'keep' last value  // can be set to another default value, like 0.0

    """
    log.info(u'Start__ ' + ' col index:' + repr(col_index) +' convert to: '+ repr(convert_to)
                         + ' min: '+ repr(min_) +' max: '+ repr(max_) + ' delete_invalid: ' + repr(delete_invalid)
                         + ' default_value_if_invalid' +  repr(default_value_if_invalid)
            )
    invalid_counter = 0
    deleted_rows = []

    if convert_to == 'float':
        convert_to =  value_to_float
    elif convert_to == 'int':
        convert_to =  value_to_int
    elif convert_to == 'unicode':
        convert_to =  value_to_unicode
    elif convert_to == 'date':
        convert_to = value_to_date
    else:
        log.warning('convert_to> ' + repr(convert_to))
        raise ValueError('convert_column', 'unknown destination type')

    if default_value_if_invalid == 'none':
        default_value_if_invalid = lambda : None
    elif default_value_if_invalid == 'keep':
        default_value_if_invalid = lambda : list_2D[row_index][col_index]
    else:
        default_value = default_value_if_invalid
        default_value_if_invalid = lambda : default_value

    for row_index in range(len(list_2D)-1, -1, -1):
        valid = True
        if len(list_2D[row_index]) > col_index:
            value = convert_to(list_2D[row_index][col_index])
            if value is not None:
                # ---
                if min_ == max_ == None:
                    pass
                # ---
                elif min_ is not None and max_ is not None:
                    if min_ <= value <= max_:
                        pass
                    else:
                        valid = False
                # ---
                elif min_ is not None:
                    if value >= min_:
                        pass
                    else:
                        valid = False
                # ---
                elif max_ is not None:
                    if value <= max_:
                        pass
                    else:
                        valid = False

            else:
                valid = False
        else:
            valid = False


        if valid:
            list_2D[row_index][col_index] = value
        else:
            invalid_counter += 1
            if delete_invalid:
                deleted_rows = [list_2D[row_index]]
                del list_2D[row_index]
            else:
                try:        # --- for  IndexError: list index out of range
                    list_2D[row_index][col_index] = default_value_if_invalid()
                except:
                    pass   # --- kepp empty cell

    if report_file is not None:
        report_file.write('---------- Value Conversion ------------ col index:' + repr(col_index)
                            +'convert to: '+ repr(convert_to)  +' min: '+ repr(min_)
                            +' max: '+ repr(max_) + ' delete_invalid: ' + repr(delete_invalid) +
                           'default_value_if_invalid' +  repr(default_value_if_invalid) + '\n')
        for row in deleted_rows:
            report_file.write(repr(row)+'\n')
        report_file.write('---------- Value Conversion ----- Invalid values: ' + repr(invalid_counter) + ' deleted rows: '+ repr(len(deleted_rows) ) )

    log.info(u'End__ deleted rows: '+ repr(len(deleted_rows)) +'invalid counter: '+ repr(invalid_counter) )
    return list_2D
    
# ------------------------------------------------------------------
def dict_to_two_column_list_of_list(dict_):
    u"""Convert dict to list_2D with 2 columns
    {a:b, c:d} -->  [[a,b][c,d]]
    """
    log.info(u'Start ' + repr(len(dict_) ) )
    list_2D = []
    for key, value in dict_.items():
        list_2D.append([key, value])

    log.info(u'End__ ' + repr(len(list_2D) ) )
    return list_2D
    
# ------------------------------------------------------------------
def dict_with_lists_to_list_2D(dict_):
    u"""Convert dict to list_2D
    {a:[b,c,d], e:[f,g,h]} -->  [[a,b],[a,c],[a,d],[e,f],[e,g],[e,h]]
    """
    log.info(u'Start ' + repr(len(dict_) ) )
    list_2D = []
    for key, sub_list in dict_.items():
        for value in sub_list:
            list_2D.append([key, value])

    log.info(u'End__ ' + repr(len(list_2D) ) )
    return list_2D
    
# ------------------------------------------------------------------
def dict_with_lists__sub_lists_to_list_2D(dict_):
    u"""Convert dict to list_2D
    {a:[b,c,d], e:[f,g,h]} -->  [[b,c,d],[f,g,h]]
    """
    log.info(u'Start ' + repr(len(dict_) ) )
    list_2D = []
    for key, sub_list in dict_.items():
        list_2D.append(sub_list)

    log.info(u'End__ ' + repr(len(list_2D) ) )
    return list_2D
    
# ------------------------------------------------------------------
def dict_with_dicts_to_list_2D(dict_):
    u"""Convert dict to list_2D
    {a:{b:c, d,x}, e:{f:g,h:i)} -->  [[a,b,c],[a,d,x],[e,f,g],[e,h,i]]
    """
    log.info(u'Start ' + repr(len(dict_) ) )
    list_2D = []
    for key, sub_dict in dict_.items():
        for sub_key, sub_value in sub_dict.items():
            list_2D.append([key,sub_key,sub_value])

    log.info(u'End__ ' + repr(len(list_2D) ) )
    return list_2D
    
# ------------------------------------------------------------------
def dict_with_lists_to_list_2D_only_values(dict_):
    u"""Convert dict to list_2D
    {a:[b,c,d,e], f:[g,h,i,j]} -->  [[b,c,d,e],[g,h,i,j],]
    """
    log.info(u'Start ' + repr(len(dict_) ) )
    list_2D = []
    for sub_list in dict_.values():
        list_2D.append(sub_list)

    log.info(u'End__ ' + repr(len(list_2D) ) )
    return list_2D
    
    
# ------------------------------------------------------------------
def dict_to_list_of_dicts(dict_):
    u"""Convert dict to list of dicts
    {a:b, c:d, e:f} -->  [{a:b},{c:d},{e:f}]
    """
    log.info(u'Start ' + repr(len(dict_) ) )
    list_of_dicts = []
    for key, value in dict_.items():
        list_of_dicts.append({key: value})
    log.info(u'End__ ' + repr(len(list_of_dicts) ) )
    return list_of_dicts

# ------------------------------------------------------------------
def one_row_from_list_to_dict(list_2D, row, values_first = True):
    u"""Convert values from one row = simple list to dictionary
    values or key values are index  depend on values_first
    """
    log.info(u'Start, row' + repr(row) )
    if (len(list_2D)-1) < row:
        log.warning(u'In the list_2D is not such row: ' + repr(row))
        raise ValueError(u'In the list_2D is not such row: ' + repr(row))

    if type(list_2D[row]) not in [list, tuple]:
        log.warning(u'Cannot convert' + type(list_2D[row])  )
        raise ValueError(u'Cannot convert' + type(list_2D[row]))
        
    dict_ = {}
    for index, value in enumerate(list_2D[row]):
        if values_first:
            if value in dict_:
                log.warning(u'Duplicit values on the row: ' + repr(value) + ' Cannot convert to dict')
                raise ValueError(u'Duplicit values on the row: ' + repr(value) + ' Cannot convert to dict')
            dict_[value] = index
        else:
            dict_[index] = value

    log.info(u'End__ ' + repr(len(dict_) ) )
    return dict_
    
# ------------------------------------------------------------------
def one_col_to_list(list_2D, col):
    u"""Take values from one column and return them as one flat list
    input [[1,2,3],[4,5,6],[7,8,9] ] output(col1) [2,5,8]
    """
    log.info(u'Start, row[0]' + repr(list_2D[0]) + 'col: ' + repr(col) )
    if (len(list_2D[0])) < col+1:
        log.warning(u'In the list_2D is not such row: ' + repr(row))
        raise ValueError(u'In the list_2D is not such row: ' + repr(row))

    if type(list_2D) not in [list, tuple]:
        log.warning(u'Cannot convert' + type(list_2D)  )
        raise ValueError(u'Cannot convert' + type(list_2D))

    list_ = []
    for row in list_2D:
        list_.extend([row[col]])

    log.info(u'End__ ' + repr(len(list_) ) )
    return list_

# ------------------------------------------------------------------
def two_columns_to_dict(list_2D, keys_col, values_col):
    u"""Convert two columns to dictionary
    [[a,b][c,d]] --0..1-->  {'a':b, 'c':d}
    can operate on list_2D with many other cols, create copy

    [[a,b,c,d], [e,f,g,h] ]  --1..3--> {'b':d, 'f':h}
    """
    log.info(u'Start ' + repr(len(list_2D) ) )
    dict_ = dict(map(lambda row: (row[keys_col], row[values_col]), list_2D))
    log.info(u'End__ ' + repr(len(dict_) ) )
    return dict_
    
    
# ------------------------------------------------------------------
def two_columns_to_dict_ordered(list_2D, keys_col, values_col):
    u"""Convert two columns to dictionary
    [[a,b][c,d]] --0..1-->  {'a':b, 'c':d}
    can operate on list_2D with many other cols, create copy

    [[a,b,c,d], [e,f,g,h] ]  --1..3--> {'b':d, 'f':h}
    """
    log.info(u'Start ' + repr(len(list_2D) ) )
    dict_ = OrderedDict(map(lambda row: (row[keys_col], row[values_col]), list_2D))
    log.info(u'End__ ' + repr(len(dict_) ) )
    return dict_
    
# ------------------------------------------------------------------
def two_columns_to_dict_of_list(list_2D, keys_col, values_col):
    u"""Convert two columns to dictionary
    [[a,b],[a,x],[c,d]] --0..1-->  {a: [b,x], c:[d]}
    can operate on list_2D with many other cols, create copy
    """
    log.info(u'Start ' + repr(len(list_2D) ) )
    dict_ = {}
    for row in list_2D:
        if row[keys_col] not in dict_:
            dict_[row[keys_col]] = []
        dict_[row[keys_col]].append(row[values_col])

    log.info(u'End__ ' + repr(len(dict_) ) )
    return dict_


# ------------------------------------------------------------------
def three_columns_to_dict_of_dicts(list_2D, upper_key_col, keys_col, values_col):
    u"""convert list_2D to
    [[X,a,b,][X,c,d][Y,e,f]] --0..1..2-->  {X: {'a':b, 'c':d}, Y: {'e':f}}
    """
    log.info(u'Start ' + repr(len(list_2D) ) )


    out_dict = {}
    map(
         lambda row:

             out_dict.setdefault(row[upper_key_col], {}).update(
                                                     {row[keys_col]: row[values_col]}
                                                   )
         , list_2D
       )

    log.info(u'End__ ' + repr(len(out_dict) ) )
    return out_dict

# ------------------------------------------------------------------
def filter_rows_by_col_value(list_2D, col, values, keep_match = True, values_as_substring = False, return_deleted_rows = False):
    u""" delete or keep rows which match one of the value
    values are some iterable structure where can be "in" opererator used

    if keep_match == True - matched are not deleted
    values_as_substring == match even if the value is substring of col value
    """
    len_list_2D = len(list_2D)
    log.info(u'Start,  column: '+ repr(col) +' len list_2D: '+repr(len_list_2D) +' len values: '+ repr(len(values)) + ' values: ' + repr(values)[:100])

    if len_list_2D == 0:
        log.warning('list_2D is empty')
        #raise ValueError()
        
    deleted_rows = []

    if not values_as_substring:
        if keep_match:
            for i in range(len(list_2D)-1, -1, -1):
                #print i, col, values
                if list_2D[i][col] in values:
                    pass
                else:
                    deleted_rows.append(list_2D[i])
                    del list_2D[i]
        else:
            for i in range(len(list_2D)-1, -1, -1):
                try:
                    if list_2D[i][col] in values:
                        deleted_rows.append(list_2D[i])
                        del list_2D[i]
                except IndexError: # delete row if not value on index present
                    deleted_rows.append(list_2D[i])
                    del list_2D[i]
                else:
                    pass
                    

    if values_as_substring:
        if keep_match:
            for i in range(len(list_2D)-1, -1, -1):
                for value in values:
                    if list_2D[i][col].find(value) == -1:
                        deleted_rows.append(list_2D[i])
                        del list_2D[i]
                    else:
                        pass
        else:
            for i in range(len(list_2D)-1, -1, -1):
                for value in values:
                    if list_2D[i][col].find(value) == -1:
                        pass
                    else:
                        deleted_rows.append(list_2D[i])
                        del list_2D[i]


    log.info(u'End_, len list2D: '+repr(len(list_2D)) +' deleted: '+ repr(len_list_2D-len(list_2D))  )
    if return_deleted_rows:
        return (list_2D, deleted_rows)
    else:
        return list_2D

# ------------------------------------------------------------------
def intersection_of_two_cols(list_2D, col1, col2, secondary_list_2D = None):
    u"""return intersection of two cols
    only unique values
    alternatively compare cols from different lists
    """
    log.info(u'Start ')

    list1 =  map(lambda row: row[col1], list_2D)
    if secondary_list_2D is None:
        secondary_list_2D = list_2D
    list2 = map(lambda row: row[col2], secondary_list_2D)
    intersection=filter(lambda x:x in list1,list2)

    log.info(u'End__ intersection len: ' + repr(len(intersection)))
    return intersection
    

# ------------------------------------------------------------------
def unique_values_from_col(list_2D, col, skip_if_none, return_in_column, skip_this = []):
    u"""return list of unique values found in column
    skip_if_none = skip rows with less columns
    skip_this = skip values in list
    return_in_column = return uniques in list of list
    """
    log.info(u'Start list len:' + repr(len(list_2D)))
    if skip_if_none:
        uniques =  list(set(map(lambda row : row[col] if len(row) > col else None, list_2D)))
        if None in uniques: uniques.remove(None)     # remove None if exist
    else:
        uniques = list(set(map(lambda row : row[col], list_2D)))

    for item in skip_this:
        if item in uniques: uniques.remove(item)

    if return_in_column:   # TODO not clear return_in_column function
        temp = []
        uniques = map(lambda value : temp.append([value]), uniques)
        uniques = temp

    log.info(u'End__ uniques len: ' + repr(len(uniques)))
    return uniques
    
# ------------------------------------------------------------------
def rows_by_unique_values_from_col(list_2D, col, skip_if_none, skip_this = []):
    u"""return list of lists rows by unique values found in column
    skip_if_none = skip rows with less columns, else exception
    skip_this = skip values in list
    """
    log.info(u'Start list len:' + repr(len(list_2D)))
    rows_with_uniques = []
    uniques = {}
    for row in list_2D:
        if len(row) < (col + 1):
            if skip_if_none == True:
                continue # skip row
            else:
                raise ValueError('Invalid List_2D Input Data in Row: ' + repr(row)[0:500], err_message)

        act_val = row[col]
        if act_val not in uniques and act_val not in skip_this:
            rows_with_uniques.append(row)
            uniques[act_val] = True
        else:
            continue # skip non uniques

    log.info(u'End__ rows by unique values len: ' + repr(len(uniques)))
    return rows_with_uniques
    
    
# ------------------------------------------------------------------
def find_duplicate_values_from_col(list_2D, col, skip_if_none):
    u"""return rows where duplicate value in col was found
    first sorted by col value
    then walk thru all rows and search for duplicates
    return list of duplicate rows
    """
    log.info(u'Start list len:' + repr(len(list_2D)))

    import operator
    index0 = operator.itemgetter(col)
    sorted_data = sorted(list_2D, key=index0)

    row_with_duplicities = []
    last_value = '@@SET_NON_EXIST_VALUE@@' # init by different value
    dup_detect = False
    for row_index in range(len(sorted_data)):
        actual_value = sorted_data[row_index][col]
        if skip_if_none and ( actual_value is None or actual_value==''):
            continue
        if actual_value != last_value:
            last_value = actual_value
            dup_detect = False
        else:  # duplicity found
            if not dup_detect:
                row_with_duplicities.append(sorted_data[row_index-1])   # append row before this row
                dup_detect = True
            row_with_duplicities.append(sorted_data[row_index])

    log.info(u'End__ duplicates len: ' + repr(len(row_with_duplicities)))
    return row_with_duplicities

# ------------------------------------------------------------------
def replace_values_in_cols(list_2D, cols, old, new, maxCount = -1, skip_bad_length = True):
    u"""replace substring values in cols
    cols can be list of columns where replacing should be made [0,1,2,3,4]
    cals can be 'ALL'  string then colums will be searched
    """
    log.info(u'Start list len:' + repr(len(list_2D)) +' cols: ' + repr(cols)  )
    
    if isinstance(cols, str) and cols == 'ALL':
        cols = range(longest_row_in_list_2D(list_2D))
    elif type(cols) == int:
        cols = [cols,]
    else: pass # expect [x,y,z] format

    for row_index, row in enumerate(list_2D):
        for col_index in cols:
            if skip_bad_length:
                if len(list_2D[row_index]) <= col_index: continue
            list_2D[row_index][col_index] = row[col_index].replace(old, new, maxCount)
    log.info(u'End__')
    return list_2D
    
# ------------------------------------------------------------------
def replace_values_in_col_by_dict(list_2D, col, repl_dict, error_if_not_in_dict = False, default_value_if_not_in_dict = u'***Not Replace, keep it***'):
    u"""replace whole values in col using translation dictionary

    default value can by:
                     ***DELETE ROW***
                     ***Not Replace, keep it***
    """
    log.info(u'Start list len:' + repr(len(list_2D)) + ' dict len: '+ repr(len(repl_dict))  )

    if error_if_not_in_dict:
        for row in list_2D:
            if row[col] not in repl_dict:
                log.info(u'Value: '+ repr(row[col]) +' cannot be repalced. Not found in replace dictionary.')
                raise ValueError(u'Value: '+ repr(row[col]) +' cannot be repalced. Not found in replace dictionary.')
                
    if default_value_if_not_in_dict == u'***Not Replace, keep it***':
        for index, row in enumerate(list_2D):
            if row[col] in repl_dict:
                list_2D[index][col] = repl_dict[row[col]]

    elif default_value_if_not_in_dict == u'***DELETE ROW***':
        for i in range(len(list_2D)-1, -1, -1):
            value = list_2D[i][col]
            if value in repl_dict:
                list_2D[i][col] = repl_dict[value]
            else:
                del list_2D[i]
    
        for index, row in enumerate(list_2D):
            if row[col] in repl_dict:
                list_2D[index][col] = repl_dict[row[col]]

    else:                               # replace with default values
        for index, row in enumerate(list_2D):
            list_2D[index][col] =  repl_dict.get(row[col], default_value_if_not_in_dict)

    log.info(u'End__ replace_values_in_col_by_dict len: ' + repr(len(list_2D)))
    return list_2D
    
    
# ------------------------------------------------------------------
def replace_values_in_col_by_dict_values_in_other_col(list_2D, col_set, col_test, repl_dict, error_if_not_in_dict = False):
    u"""replace whole values in col using translation dictionary
        replace value in col_set if match value in col_test to repl_dict

    default value can by:
                     ***DELETE ROW***
                     ***Not Replace, keep it***
    """
    log.info(u'Start list len:' + repr(len(list_2D)) + ' dict len: '+ repr(len(repl_dict))  )

    if error_if_not_in_dict:
        for row in list_2D:
            if row[col_test] not in repl_dict:
                log.info(u'Value: '+ repr(row[col_test]) +' cannot be repalced. Not found in replace dictionary.')
                raise ValueError(u'Value: '+ repr(row[col_test]) +' cannot be repalced. Not found in replace dictionary.')

    for index, row in enumerate(list_2D):
        if row[col_test] not in repl_dict:
            continue
            
        value = repl_dict[row[col_test]]
        if value.startswith('='):
            exec("value = " + value[1:])

        list_2D[index][col_set] = value


    log.info(u'End__ replace_values_in_col_by_dict_values_in_other_col len: ' + repr(len(list_2D)))
    return list_2D
    
    
    
# ------------------------------------------------------------------
def sort_by_col(list_2D, col, reverse=False, use_locale=False):
    u"""Return sorted list by values in one column
    """
    log.info(u'Start list len:' + repr(len(list_2D)) + ' col: '+ repr(col)  )

    if use_locale:
        import locale
        locale.setlocale(locale.LC_ALL, '')
        act_loc = locale.getlocale()
        list_2D.sort(key=lambda x: locale.strxfrm( x[col].encode(act_loc[1]) ), reverse=reverse)
    else:
        list_2D.sort(key=lambda x: x[col], reverse=reverse)

    log.info(u'End__' )
    return list_2D

# ------------------------------------------------------------------
def combine_lists_special(list_2D_one, list_2D_two, combine_mechanism = 'add_col_2'):
    u"""
    Quite specific function how to combine values from two list_2D

    Input: two list of list:
    Output: one list with merged values
    """
    
    
    log.info(u'Start list1 len:' + repr(len(list_2D_one)) + '  list2 len:' + repr(len(list_2D_two))  )


    if combine_mechanism == 'add_col_2':
        """list_2D_one extended by column 2 in list_2D_two
           if values in cols 0 and 1 matched
           Not optimalized for long lists, working brute force
        """
        counter = 0
        for index, row_in_1 in enumerate(list_2D_one):                           # for every row in list 1
            #if counter % 10 == 0: print counter, ', ' ,
            counter += 1
            if len(row_in_1) < 2: continue                                       # skip short ones
            for row_in_2 in list_2D_two:                                            # for every row i list 2
                if len(row_in_2) < 3: continue                                      # # skip short ones
                if row_in_1[0] == row_in_2[0] and row_in_1[1] == row_in_2[1]:       # if the value in first and second column are same
                    list_2D_one[index] = row_in_1 + [row_in_2[2]]                   # add value from list_2D_two col 2
                    break;


    log.info(u'End__' )
    return list_2D_one






         
