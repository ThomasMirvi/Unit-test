# -*- coding: utf-8 -*-
# verze 090926
# upravena verze pro externi pouziti
"""help manipulate with os filesystem and directory tasks"""

import glob
import os
import unicodedata

# log = log.info = log.debug = lambda x : None # as dummy logger, if you import own logger it will be owerwritten
# from manipulator_globals import *       # can be delete it connect loger and other global parts  # or it can be replaced by your own module with logger



def listDirs(dirname):
    """return list subdirectories in directory"""
    log.info(u'Start ')
    subDirs = []

    for entry in os.listdir(dirname):
        item = os.path.normcase(os.path.join(dirname, entry))
        if os.path.isdir(item):
            subDirs.append(item)
    log.info(u'End__ ')
    return subDirs

def listDirsMulti(dirs=[]):
    """list subdirectories in multiple directories"""
    log.info(u'Start dirs: ...' + repr(dirs)[-25:])

    subDirs = []
    
    for dir in dirs:
        subDirs = subDirs + (listDirs(dir))

    log.info(u'End__ ')
    return subDirs

def listDirsOnlevel(rootDirs=['.'], level=0):
    """list subdirectories on some level depth in rootDirectory"""
    log.info(u'Start dirs: ...' + repr(rootDirs)[-25:]  +' level:' + repr(level))
    if level <= 0:
       return rootDirs
    else:   
       return listDirsOnlevel(listDirsMulti(rootDirs), level -1)
   
def listFilesOnLevel(rootDirs=['.'], fileMasks=['*.*',], level=0):
    """find and return files according to fileMasks in some subdirectory level of rootDirs"""
    log.info(u'Start ' +' dirs: ...' +repr(rootDirs)[-25:]  + ' Filemasks: ' + repr(fileMasks) + ' level:' + repr(level))
    dirs = listDirsOnlevel(rootDirs, level)
    files=[]
    log.debug('Listed dirs: ...' + repr(dirs)[-25:])
    for dir_ in dirs:
        for mask in fileMasks:
            log.debug('Dir: ...' + repr(dir_)[-25:] + ' Mask ' + mask )
            matchFiles = glob.glob(os.path.join(dir_,mask))
            files.extend(matchFiles)
            
    log.info(u'End__ ')
    return list(set(files))
    
def changeDestinationFile(oldDest, newDest):
    """change filename in path to destFile"""
    if (oldDest == None) or (newDest == None) : return None
    path = os.path.split(oldDest)
    return os.path.join(path[0], newDest)
    
    
import zipfile

def unzip_all(path, zip_file):
    """Unzip all archive with directory structure to path"""
    zip_ = zipfile.ZipFile(zip_file, 'r')
    isdir = os.path.isdir
    join = os.path.join
    norm = os.path.normpath
    split = os.path.split
    for each in zip_.namelist():
        if not each.endswith('/'):
            root, name = split(each)
            directory = norm(join(path, root))
            if not isdir(directory):
                os.makedirs(directory)
            file(join(directory, name), 'wb').write(zip_.read(each))
    zip_.close()


def unzip_archives_on_level(rootDirs=['.'], fileMasks=['*.zip',], level=0):
    """Extract all .zip archives in one directory level"""
    archives = listFilesOnLevel(rootDirs, fileMasks, level)
    print(archives)
    for archive in archives:
        unzip_all(os.path.dirname(archive), archive)
        

def zip_files(files = [], archive_name = ''):
    """zip files to archive
       not preserve archives
    """
    if len(files) < 1: raise InputError('No files for packing', 'Need files')
    if archive_name == '': raise InputError('No archive_path_name', 'path and filename of output archive')
    archive = zipfile.ZipFile(archive_name, "w")
    for file_name in files:
        archive.write(file_name, os.path.basename(file_name), zipfile.ZIP_DEFLATED)
    archive.close()
    
    
def deaccent(unistr):
    """Normalize unicode string
    useful for conversion of unicode chars in filenames to ascii
    """
    return "".join(aChar for aChar in unicodedata.normalize("NFD", unistr) if not unicodedata.combining(aChar))

    
    
