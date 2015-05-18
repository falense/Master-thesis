import random
import os
import numpy
import traceback,sys

from deap import algorithms
from bootstrap import bootstrap
from progress import Progress
from utility import load_config

def main(conf):
    
    pop, toolbox, hof, stats =   bootstrap(conf)
    prog = Progress(conf)
    
            
    pop, logbook = algorithms.eaMuPlusLambda(pop, toolbox, mu=conf.MU, lambda_=conf.LAMBDA, 
            cxpb=conf.CXPB, mutpb=conf.MUTPB, ngen=0, stats=stats, halloffame=hof)
    prog.update(0,pop,hof)
    for gen in range(conf.NGEN/5):
        pop, logbook = algorithms.eaMuPlusLambda(pop, toolbox, mu=conf.MU, lambda_=conf.LAMBDA, 
                cxpb=conf.CXPB, mutpb=conf.MUTPB, ngen=5, stats=stats, halloffame=hof)
        prog.update((gen+1)*5,pop,hof)
    
    #prog.hold()
    
    return pop, stats, hof
                 
if __name__ == "__main__":
    conf = load_config("StepDevConf")
    main(conf)                 

