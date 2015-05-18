
import os

import traceback,sys
CONFIG_FOLDER = "Configs"

def load_config(name):
    try:
        module = __import__("%s.%s" % (CONFIG_FOLDER,name), fromlist=["Config"])
    except ImportError:
        # Display error message
        traceback.print_exc(file=sys.stdout)
        raise ImportError("Failed to import module {0} from folder {1} using fromlist {2}".format(name,CONFIG_FOLDER,listofimports))
    conf = module.Config()
    conf.filename = os.path.join(CONFIG_FOLDER, "%s.py" % name)
    conf.name = name
    print "Loading config %s. Loading completed" % name
    return conf 
