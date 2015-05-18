
#saved_calls = []


#import inspect

#def foo():
   #print inspect.stack()[0][3]


#def add(a,b):
    #if a < 0 or b < 0:
        #return 1
    ##print .
    #print locals().keys()
    #print locals().values()
    
    #saved_calls.append((add,(a-1,b-2)))
    #return a+b
    
#add (2,3)

#print add.func_code.co_varnames
#print add.func_code.co_argcount
#print add.func_name


#for func,inputs in saved_calls:
    #func(*inputs)

import yaml
import os
import argparse
from os import listdir,makedirs
from os.path import isfile, join, exists
import traceback,sys
import hashlib

figure_folder = "figures"

def save_fig(module, func, var_values, filename=None):
    func_name = func.__name__
    var_names = func.func_code.co_varnames[:func.func_code.co_argcount]
    var_values["saved_fig"] = True
    
    prepared_list = []
    for var_name in var_names:
        prepared_list.append(var_values[var_name])
    
    data = yaml.dump(prepared_list)
    
    if filename is None:
        filename = func_name
    else:
        filename = hashlib.sha256(filename).hexdigest()
    
    if not os.path.exists(figure_folder):
        os.makedirs(figure_folder)
        initfile_full = os.path.join(figure_folder,"__init__.py")
        f = open(initfile_full,"w")
        f.close()
    
    filename_full = os.path.join(figure_folder, "%s.py" % filename)
    
    f = open(filename_full, "w")
    
    f.write("import yaml\n")
    f.write("from %s import %s\n" % (module, func_name))
    f.write("def main():\n")
    f.write("\tdata_raw = '''%s'''\n" % data)
    f.write("\tdata = yaml.load(data_raw)\n")
    f.write("\t%s(*data)\n" % func_name)
    f.write("if __name__=='__main__':\n")
    f.write("\tmain()\n")
    
    f.close()
    
def list_modules(folder):
    types = []
    for f in listdir(folder):
        if isfile(join(folder,f)):
            name, extension = f.split(".")
            if extension == "py" and name != "__init__":
                types.append(name)
    return types
    
def load_module(name):
    try:
        module = __import__("%s.%s" % (figure_folder,name), fromlist=["main"])
    except ImportError:
        # Display error message
        traceback.print_exc(file=sys.stdout)
        raise ImportError("Failed to import module {0} ".format(name))
    return module

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", metavar="filename", type=str,default=None, help="File to regenerate")
    return parser
if __name__=="__main__":
    parser = create_parser()
    args = parser.parse_args()
    
    if args.filename is not None:
        module = load_module(hashlib.sha256("PltFit Direction UAVs 3, Trials 100, Step angle 1, Angle spread 46,  Noise 1.0 FIT  - 2").hexdigest())
        module.main()
    else:
    
        loaded_modules = map(load_module, list_modules(figure_folder))

        for index,module in enumerate(loaded_modules):
            module.main()
            print "Generated %s" % index

