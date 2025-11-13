# -*- coding: utf-8 -*-
from __future__ import with_statement
u"""Pomocne podprogramky """

__author__    = u"Filip Vaculik (mintaka@post.cz)"
__version__   = u"Revision: 0.4"
__date__      = u"Date: 2020/11/06 20:00:05"
__copyright__ = u"Copyright (c) 2007 Filip Vaculik"
__license__   = u"GNU GPL"


"""
# verze 061120
# dopleny lambda funkce na ziskani aktualniho datumu a casu
"""


import time

log = log.info = log.debug = log.warning = lambda *args, **kwargs: None # as dummy logger, if you import own logger it will be owerwritten
# from manipulator_globals import *       # can be delete it connect loger and other global parts  # or it can be replaced by your own module with logger

TODAY = lambda : time.strftime("%y%m%d", time.localtime())
NOW = lambda : time.strftime("%H%M%S", time.localtime())
DATETIME = lambda : time.strftime(prefix+"%y%m%d_%H%M%S"+postfix, time.localtime())
DATETIM = lambda : time.strftime("%y%m%d_%H%M%S", time.localtime())


#SED_EXEC_COMMAND  = u'd:/Prg/SED/bin/sed.exe'        # command for execution sed Streamed Editor http://en.wikipedia.org/wiki/Sed
SED_EXEC_COMMAND  = u'sed'
EXEC_COMMAND_CODEPAGE = u'cp1250'

#---------------------------------------------------------------------------
class Timer:
    """pro mereni doby behu casti programu"""
    def __init__(self):
        self.start()
    def start(self):
        self.start_time = time.gmtime()
        print("START time: "+ time.strftime("%H:%M:%S", self.start_time))
    def stop(self):
        self.stop_time = time.gmtime()
        print("STOP time: " + time.strftime("%H:%M:%S", self.stop_time))
    def elapse(self):
        pass
        #print ' Elapse: ' + time.strftime("%y%m%d - %H:%M:%S", time.gmtime() - self.start_time)
    def act_time(self):
        return time.strftime("%y%m%d", time.gmtime())
        
        
        
# --------------------------------------------------------------------------
def replace_by_sed(file_names, replacement_rules, sed_execution = SED_EXEC_COMMAND, exec_command_codepage = EXEC_COMMAND_CODEPAGE):
    u"""replace strings by replacemnt rules
    using sed Streamed editor
    permanetly change input files
    
    if replacement == 'DELETE LINE', delete line
    """
    log.info(u'Start replacemnts: ' + repr(len(replacement_rules)) + ' filenames: ' + repr(file_names))
    import subprocess

    if isinstance(file_names, str):  # if file is only one string, is expected one file
        file_names = [file_names]            # encapsulate it into list


    def escape_for_sed(string):
        u"""Escape characters which can makde troubbles in SED command // Need better testing """
        string = string.replace(u'\\',u'\\\\')
        string = string.replace(u'"',u'\"')
        string = string.replace(u"'",u"\'")
        return string

    for file_name in file_names:
        file_name = file_name.replace(' ', '\ ')  # preserver spaces in filename
        #file_name = '"'+ file_name + '"'
        for searched, replacement in replacement_rules:
            #argument = u""" -i "s/%(searched)s/%(replacement)s/g" %(file_name)s""" % ( vars() )
            searched = escape_for_sed(searched)
            if replacement == 'DELETE LINE':
                argument = u""" -i "/%(searched)s/d" %(file_name)s""" % ( vars() )
            elif replacement == 'KEEP LINE':
                argument = u""" -i "/%(searched)s/!d" %(file_name)s""" % ( vars() ) # negace smazani /!d
            else:
                replacement = escape_for_sed(replacement)
                argument = u""" -i "s/%(searched)s/%(replacement)s/g" %(file_name)s""" % ( vars() )
            command = sed_execution + argument
            command = command.encode(exec_command_codepage)
            log.info('RUN ->'+ sed_execution)
            output = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
            for line in output.stdout:
                print(line)

    log.info(u'End__ ')


# --------------------------------------------------------------------------
def get_platform():
    u"""return system identificator"""
    platform = sys.platform
    return platform

# --------------------------------------------------------------------------
def get_working_dir():
    u"""return pwd  """
    working_dir = os.path.abspath(os.getcwd())
    return working_dir
    
# --------------------------------------------------------------------
def create_working_copies(file_names, copy_file_names = None, add_date_to_name = False, skip_if_exist = False):
    u"""Create working copies of files
       if copy_file_names is None generate default names
       
       return copy_file_names
    """

    log.info(u'Start ')
    log.debug('FILENAMES> ' + repr(file_names) + '\ncopy_file_names >>' + repr(copy_file_names))
    if isinstance(file_names, str):  # if in csv_files is only one string, is expected one file
        file_names = [file_names]            # encapsulate it into list

    if file_names is None:
        raise InputError('create_working_copies', 'file_names is None, cannot copy None')

    if copy_file_names is None:              # default generating names for working copies
        copy_file_names = []
        if add_date_to_name:
            date = '_' + time.strftime("%y%m%d", time.gmtime())
        else:
            date = ''
            
        for file_name in file_names:
            filepath, filename = os.path.split(file_name)
            shortname, extension = os.path.splitext(filename)
            copy_file_names.append(filepath+'/'+shortname+'_copy'+date+extension)
            log.debug(repr(copy_file_names))
    else:
        if len(file_names) != len(copy_file_names):
            raise InputError('create_working_copies', 'len of file_names and copy_file_names is different')
        
    for file_name, copy_file_name in map(None, file_names, copy_file_names):
        if skip_if_exist:
            if os.path.isfile(copy_file_name):
                log.debug('skip existing copy ' + repr(file_name) + ' -> ' +  repr(copy_file_name) )
                continue
        log.debug('copy ' + repr(file_name) + ' -> ' +  repr(copy_file_name) )
        shutil.copyfile(file_name, copy_file_name)
    log.debug( repr(copy_file_names) )
    
        
    log.debug('RETURN copy_file_names' + repr(copy_file_names) )
    log.info(u'End__ ')

    return copy_file_names

        

# --------------------------------------------------------------------------
def marshaling(stuff, file_name):
    u"""ulozi hodnotu objektu do souboru pro externi pouziti
    Pro velke mutable objekty, velmi POMALE vytvareni
    Pro slovnikove objekty pomale vytvareni, rychle nacitani
    """
    from marshal import dumps as  marshal_dumps
    log.info(u'Start ' + repr(type(stuff)) + ' ' + file_name)
    stuff = marshal_dumps(stuff)
    fh = open(file_name, 'wb')
    fh.write(stuff)
    log.info(u'Konec marshaling ------> DONE')

# --------------------------------------------------------------------------
def unmarshaling(file_name):
    u"""nacte marshalovanou hodnutu ze souboru a vrati ji jako hodnotu noveho objektu"""
    from marshal import loads as marshal_loads
    log.info(u'Start ' + repr(type(object)) + file_name)
    fh = open(file_name, 'rb')
    stuff = marshal_loads(fh.read())
    log.info(u'Konec ' + repr(type(stuff)))
    return stuff

# --------------------------------------------------------------------------
def pickle_to_file(stuff, file_name, prefix = '', postfix=''):
    u"""ulozeni dumpu promenne"""
    from cPickle import dump as pickle_dump
    with open(prefix + file_name.split('.')[0] + postfix + '.pickle', 'wb') as fw:
        pickle_dump(stuff, fw, True)

# --------------------------------------------------------------------------
def pickle_from_file(file_name, prefix = '', postfix=''):
    u"""nacteni dumpu do promenne"""
    from cPickle import load as pickle_load
    with open(prefix + file_name.split('.')[0] + postfix + '.pickle', 'rb') as fr:
        stuff = pickle_load(fr)
    return stuff

# --------------------------------------------------------------------------
def repr_to_dump(stuff, file_name, prefix = '', postfix=''):
    u"""ulozeni repr hodnoty jako dumpu promenne"""
    from codecs import open as codecs_open
    with codecs_open(file_name + '_stuff_utf8.py', 'w', 'utf8') as fw:
        fw.write('# -*- coding: utf8 -*- \n')
        fw.write('stuff=')
        fw.write(repr(stuff))
        fw.close()

# --------------------------------------------------------------------------
def repr_from_dump(file_name, prefix = '', postfix=''):
    u"""ulozeni repr hodnoty jako dumpu promenne
    Problemy s velkymi polozkami
    """
    from codecs import open as codecs_open
    from test_stuff import stuff
    return stuff
    with codecs_open(file_name + '_stuff_utf8.py', 'r', 'utf8') as fr:
        stuff = fr.read()
        stuff = eval(stuff)
        fr.close()
        return stuff
        
# --------------------------------------------------------------------------
def cjson_to_file(stuff, file_name, add_default_extension = False):
    u"""ulozeni cjson dumpu promenne"""
    from cjson import encode as cjson_encode
    json_object = cjson_encode( stuff )
    if add_default_extension:
        file_name += '.cjson'
    with open(file_name, 'wb') as fw:
        fw.write(json_object)
        fw.close()

# --------------------------------------------------------------------------
def cjson_from_file(file_name):
    u"""nacteni cjson dumpu do promenne"""
    from cjson import decode as cjson_decode
    with open(file_name, 'rb') as fr:
        stuff = cjson_decode(fr.read())
    return stuff
    
# ------------------------------------------------------------------
def flatten(x):
    u"""Flattenise multidimensional arrays to one dimensional """
    ans = []
    for i in range(len(x)):
        if isinstance(x[i],list):
            ans.extend(flatten(x[i]))
        else:
            ans.append(x[i])
    return ans

# --------------- EXCEPTIONS --------------------------------------------
class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

class TransitionError(Error):
    """Raised when an operation attempts a state transition that's not
    allowed.

    Attributes:
        previous -- state at beginning of transition
        next -- attempted new state
        message -- explanation of why the specific transition is not allowed
    """

    def __init__(self, previous, next, message):
        self.previous = previous
        self.next = next
        self.message = message

