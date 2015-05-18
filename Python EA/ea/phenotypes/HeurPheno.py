

GENOME = "genome"
PHENOME = "phenome"
FITNESS = "fitness"
import json

class Phenotype(object):
    def __init__(self,genome):
        self.genome = genome
        self.fit = None
    def fitness(self):
        return self.fit
    def set_fitness(self,fit):
        self.fit = fit
    def __repr__(self):
        output = {}
        output[GENOME] = self.genome.heur_params
        output[PHENOME] = self.get_heur_params()
            
        output[FITNESS] = self.fit
        
        output_string = json.dumps(output)
        return output_string
    def get_heur_params(self):
        params = []
        params.append(self.genome.heur_params[0])
        
        angles = map(lambda i: i * 360.0, self.genome.heur_params[1:])
        params.extend(angles)
        
        return params
    def get_genome(self):
        return self.genome
        
    def combine(self,other):
        child1, child2 = self.genome.combine(other.get_genome())
        return Phenotype(child1),Phenotype(child2)
        
