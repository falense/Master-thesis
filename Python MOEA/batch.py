
import traceback

from main import main
from utility import load_config


def batch_vardev():
    conf = load_config("VarDevConf")
    
    try:
        main(conf)
    except:
        print traceback.format_exc()
    
def batch_countdev():
    c = 1
    for num_steps in xrange(3+c,7):
        
        conf = load_config("CountDevConf")
        conf.NUM_STEPS = num_steps
        conf.reinit()
        try:
            main(conf)
        except:
            print traceback.format_exc()


def batch_stepdev():
    c = 0
    for num_uavs in xrange(3,9):
        for num_steps in xrange(3,5):
            if c < 7:
                print "Skipping (%s,%s)" % (num_uavs,num_steps)
                c += 1
                continue
            conf = load_config("StepDevConf")
            conf.NUM_UAVS = num_uavs
            conf.NUM_STEPS = num_steps
            conf.reinit()
         
            try:
                main(conf)
            except:
                print traceback.format_exc()
    
    
if __name__=="__main__":
#    batch_countdev()
#    batch_vardev()
    batch_stepdev()
    
