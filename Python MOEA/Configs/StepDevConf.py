from BaseConf import BaseConf
import random

class Config(BaseConf):
    num_trials = 100
    
    NUM_UAVS = 4
    NUM_STEPS = 5
    
    fixed_step = False
    fixed_uav_count = True
    
    label_objective = "Longest path (m)"
    

    def __init__(self):
        self.reinit()
    def get_objective_weights(self):
        return (-1.0, -1.0)
    def gen_objective_function(self,evaluation_function):
        def evaluate(individual):
            fit, avg_dev, max_dev, min_dev, variance, distance, uav_count = evaluation_function(individual)
            return avg_dev, distance
        return evaluate
    def reinit(self):
        random.seed(1)
        self.uav_max_step_length = 400.0/self.NUM_STEPS
        
        self.LAMBDA = self.NUM_UAVS * (self.NUM_STEPS+1) * 20 
        self.MU = self.LAMBDA * 2
        
