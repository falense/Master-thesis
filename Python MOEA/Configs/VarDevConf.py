from BaseConf import BaseConf
import random

class Config(BaseConf):
        
        
    NUM_UAVS = 4
    NUM_STEPS = 4

    MU = 100
    LAMBDA = 50
    
    fixed_step = True
    fixed_uav_count = True
    
    label_objective = "Variance"
    def __init__(self):
        random.seed(1)
    def gen_objective_function(self,evaluation_function):
        def evaluate(individual):
            fit, avg_dev, max_dev, min_dev, variance, distance, uav_count = evaluation_function(individual)
            return avg_dev, variance
        return evaluate
    
            
