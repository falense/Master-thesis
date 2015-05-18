
#!/usr/bin/python
from random import randint, uniform, gauss
from math import cos, sin, acos, asin, pow, sqrt
from BaseGeno import *
import os, json, ConfigParser
    
def make_params(settings):
    params = []
    for x in xrange(settings.num_receivers+1):
        params.append(uniform(0,1))
    return params
    
def make_generation(population_size,configuration):
	settings = GenoSettings(configuration)

	pop = []
	for i in xrange(population_size):
		t = Genotype(settings,make_params(settings))
		pop.append(t)
	return pop

class GenoSettings(object):
    def __init__(self,config):
        self.parse_recombination(config)
        self.parse_num_receivers(config)
    def parse_num_receivers(self,config):
        self.num_receivers = config.getint(GLOBAL_SECTION, 'num_receivers')
    def parse_recombination(self,config):
        self.mutation_rate = config.getfloat(GENOTYPE_SECTION, 'mutation_rate')
        self.crossover_rate = config.getfloat(GENOTYPE_SECTION, 'crossover_rate')
        self.mutation_step = config.getfloat(GENOTYPE_SECTION, 'mutation_step')
    
            
            

    
class Genotype(object):
    def __init__(self,settings,heur_params):
        self.settings = settings
        self.heur_params = heur_params
        
    def combine(self,other):
        c1 =  self.heur_params[:]
        c2 =  other.heur_params[:]
        
        assert len(c1)==len(c2), "Lengths of genos vary! This should never happen"
        
        if self.settings.crossover_rate > uniform(0,100):
            n1,n2 = self.crossover(c1,c2)
        else:
            n1,n2 = c1,c2
        
        if self.settings.mutation_rate > uniform(0,100):
            n1,n2 = self.mutation(n1,n2)
        
        return (Genotype(self.settings,n1),Genotype(self.settings,n2))
    def crossover(self,c1,c2):
        n1 = []
        n2 = []
        
        crossover = randint(0,len(c1))
        
        for i in range(crossover):
                n1.append(c1[i])
                n2.append(c2[i])
        for i in range(crossover,len(c1)):
                n1.append(c2[i])
                n2.append(c1[i])
          
        return n1,n2
    def mutation(self, n1,n2):
        mutation_step = self.settings.mutation_step
        
        num_params = len(n1)
        
        mut_index = randint(0,num_params-1)
        
        n1[mut_index] += gauss(0, mutation_step)
        n2[mut_index] += gauss(0, mutation_step)
        
        n1[mut_index] = max(0.0,min(1.0, n1[mut_index]))
        n2[mut_index] = max(0.0,min(1.0, n2[mut_index]))
        
        return n1,n2
