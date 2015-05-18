#!/usr/bin/python

from main import main
from ea.config import GLOBAL_SECTION
from ea.genotypes.BaseGeno import GENOTYPE_SECTION
from ExperimentParser import *


TEST = False

def batch_completepath():
    c = 1
    for sample_count in xrange(1,11):
        for uav_count in xrange(1,13):
            if uav_count * sample_count > 40 or uav_count * sample_count < 3:
                continue
            if c <= 24:
                c += 1
                continue
            config_parameters = []
            config_parameters.append((GLOBAL_SECTION, "num_receivers", str(uav_count)))
            
            config_parameters.append((GENOTYPE_SECTION, "receiver_step_count", str(sample_count)))
            population_size = max(40,uav_count*sample_count*20)
            
            config_parameters.append((GLOBAL_SECTION, "population_size", str(population_size)))
            main("./configs/PathComplete.ini", config_parameters)
def batch_test_statistics():
    uav_count = 3
    num_steps = 4
    for seed in xrange(3,100):
        config_parameters = []
        config_parameters.append((GLOBAL_SECTION, "num_receivers", str(uav_count)))
        config_parameters.append((GLOBAL_SECTION, "seed", str(seed)))
        
        config_parameters.append((GENOTYPE_SECTION, "receiver_step_count", str(num_steps)))
        
        population_size = max(40,uav_count*num_steps*10)
        
        config_parameters.append((GLOBAL_SECTION, "population_size", str(population_size)))
        main("./configs/PathComplete.ini", config_parameters)
        

def batch_incremental_prefix():
    for uav_count in xrange(1,11):
        for num_steps in xrange(2,4):
            config_parameters = []
            config_parameters.append((GLOBAL_SECTION, "num_receivers", str(uav_count)))
            
            config_parameters.append((GENOTYPE_SECTION, "receiver_step_count", str(num_steps)))
            
            population_size = max(40,uav_count*num_steps*20)
            config_parameters.append((GLOBAL_SECTION, "population_size", str(population_size)))
            
            main("./configs/PathComplete.ini", config_parameters)
            
def batch_incremental():
    
    load_experiments("experiments_ref")
    for base_steps in xrange (2,4):
        for uav_count in xrange(1,11):
            if base_steps * uav_count < 3: 
                continue
            for num_steps in xrange(2,5):
                experiment = find_experiment([("num_receivers",uav_count),("receiver_step_count",2)])
                if experiment is None:
                    print "Error experiment not found"
                    exit(1)
                
                best_pheno = experiment.get_phenome(100, 0, "FITNESS",True)
                base_pheno_decoded_positions = best_pheno['decoded_positions']
                base_pheno_list = []
                for position in base_pheno_decoded_positions:
                    base_pheno_list.append(" ".join(map(str,position)))
                    
                base_pheno_str = ",".join(base_pheno_list)
                
                config_parameters = []
                config_parameters.append((GENOTYPE_SECTION, "base_pheno", base_pheno_str))
                
                config_parameters.append((GLOBAL_SECTION, "num_receivers", str(uav_count)))
                
                config_parameters.append((GENOTYPE_SECTION, "receiver_step_count", str(num_steps)))

                population_size = max(40,uav_count*num_steps*20)
                config_parameters.append((GLOBAL_SECTION, "population_size", str(population_size)))
                    
                    
                main("./configs/PathIncr.ini", config_parameters)
                
def batch_problem2():
    for seed in xrange(10):
        config_parameters = []
        config_parameters.append((GLOBAL_SECTION, "seed", str(seed)))
        
        main("./configs/Problem2 - Polar.ini", config_parameters)
def batch_heuristic():
    c = 1
    for uav_count in xrange(3,4):
        for seed in xrange(0,20):
            if c <= 4:
                c += 1
                continue
            config_parameters = []
            config_parameters.append((GLOBAL_SECTION, "num_receivers", str(uav_count)))
            config_parameters.append((GLOBAL_SECTION, "seed", str(seed)))
            
            population_size = (uav_count+1)*10
            config_parameters.append((GLOBAL_SECTION, "population_size", str(population_size)))
            
            main("./configs/Heuristics.ini", config_parameters)
    
    
if __name__ == '__main__':
    #batch_complete_lessthan40()
    #batch_complete_lessthan20()
    #batch_test_statistics()
    #batch_incremental()
    #batch_incremental_prefix()
    #batch_problem2()
    batch_heuristic()
    #batch_completepath()
