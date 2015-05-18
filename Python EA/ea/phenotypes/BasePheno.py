

GENOME = "genome"
DECODED_POSITIONS = "decoded_positions"
AVG_DEV = "AVG_DEV"
MAX_DEV = "MAX_DEV"
MIN_DEV = "MIN_DEV"
VAR = "VARIANCE"
ABS_BIAS = "ABS_BIAS"
FITNESS = "FITNESS"
FITNESS_COMPONENTS = "FITNESS_COMPONENTS"

import json

class BasePhenotype(object):
    receiver_set = []
    emitter = None
    genome = None
    fit = None
    rotate = False
    prediction_stat = None
    components = None
    def __init__(self,genome):
        self.receiver_set = genome.get_receiver_set()
        self.emitter = genome.get_emitter()
        self.genome = genome
        self.prediction_stat = {}
    def fitness(self):
        return self.fit
    def set_fitness(self,fit):
        self.fit = fit
    def set_statistics(self,avg_dev, max_dev, min_dev, variance, abs_bias):
        self.prediction_stat[AVG_DEV] = avg_dev
        self.prediction_stat[MAX_DEV] = max_dev
        self.prediction_stat[MIN_DEV] = min_dev
        self.prediction_stat[VAR] = variance
        self.prediction_stat[ABS_BIAS] = abs_bias
    def get_avg_dev(self):
        return self.prediction_stat[AVG_DEV]
    def set_fitness_components(self, components):
        self.components = components
    def get_fitness_components(self):
        return self.components
    def __repr__(self):
        output = {}
        output[GENOME] = self.receiver_set
        output[DECODED_POSITIONS] = self.get_position()
        
        if self.prediction_stat.get(AVG_DEV) is not None:
            output[AVG_DEV] = self.prediction_stat[AVG_DEV]
            output[MAX_DEV] = self.prediction_stat[MAX_DEV]
            output[MIN_DEV] = self.prediction_stat[MIN_DEV]
            output[VAR] = self.prediction_stat[VAR]
            output[ABS_BIAS] = self.prediction_stat[ABS_BIAS]
            
        output[FITNESS] = self.fit
        
        
        output_string = json.dumps(output)
        return output_string
    def get_position(self):
        return None
    def get_genome(self):
        return self.genome
    def get_emitter(self):
        return self.genome.get_emitter()
