#!/usr/bin/python

from os import listdir,makedirs
from os.path import isfile, join, exists
import traceback,sys
def list_modules(folder):
    types = []
    for f in listdir(folder):
        if isfile(join(folder,f)):
            name, extension = f.split(".")
            if extension == "py" and name != "__init__":
                types.append(name)
    return types
    
def load_module(folder,name,listofimports):
    try:
        module = __import__("ea.%s.%s" % (folder,name), fromlist=listofimports)
    except ImportError:
        # Display error message
        traceback.print_exc(file=sys.stdout)
        raise ImportError("Failed to import module {0} from folder {1} using fromlist {2}".format(name,folder,listofimports))
    return module

def select_class(name, name_list):
    for n, c in name_list:
        if n == name:
            return c

def degToRad(deg):
    return 3.14/180.0*deg

def create_folder(folder):
    if not exists(folder):
        makedirs(folder)
    return folder
    
