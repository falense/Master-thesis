from BaseConf import BaseConf
import random

class Config(BaseConf):
    NUM_UAVS = 8
    NUM_STEPS = 5
    
    fixed_step = True
    fixed_uav_count = False
    
    label_objective = "UAV Count"
    

    def __init__(self):
        self.reinit()
    def gen_objective_function(self,evaluation_function):
        def evaluate(individual):
            fit, avg_dev, max_dev, min_dev, variance, distance, uav_count = evaluation_function(individual)
            return avg_dev, uav_count
        return evaluate
        
    def reinit(self):
        random.seed(1)
        self.MU = 200+50*(self.NUM_STEPS-3)
        self.LAMBDA = 100+25*(self.NUM_STEPS-3)
    
