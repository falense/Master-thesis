
#!/usr/bin/python
from random import randint, uniform, gauss
from BaseGeno import *
from math import cos, sin, acos, asin, pow, sqrt
import os, json, ConfigParser

def make_receiver(settings, base_pos):

    receiver = []
    receiver.append(base_pos[-1][0])#uniform(0,settings.get_max_receiver_x()))
    receiver.append(base_pos[-1][1])#uniform(0,settings.get_max_receiver_y()))

    for i in xrange(settings.get_receiver_step_count()):
        angle = uniform(0,360)
        receiver.append(angle)
        
    return receiver
    
def make_receiver_set(settings):
    receiver_set = []
    base_positions = settings.get_base_positions()
    for i in range(settings.get_num_receivers()):
		receiver = make_receiver(settings, base_positions[i])
		receiver_set.append(receiver)
    return receiver_set
    
def make_generation(population_size,configuration):
	settings = GenoSettings(configuration)

	pop = []
	for i in xrange(population_size):
		t = Genotype(settings,make_receiver_set(settings))
		pop.append(t)
	return pop

class GenoSettings(BaseSettings):
    def __init__(self,config):
        super(GenoSettings,self).__init__(config)
        self.base_positions = self.parse_base_points(config)
    def parse_receiver_freedom(self,config):
        self.mutation_rate = config.getfloat(GENOTYPE_SECTION, 'mutation_rate')
        self.crossover_rate = config.getfloat(GENOTYPE_SECTION, 'crossover_rate')
        self.mutation_step = config.getfloat(GENOTYPE_SECTION, 'mutation_step')
        self.receiver_step_count = config.getint(GENOTYPE_SECTION, 'receiver_step_count')

    def get_receiver_step_count(self):
		return self.receiver_step_count
    def get_base_positions(self):
        return self.base_positions
    def parse_base_points(self,config):
        step_count = self.get_receiver_step_count()
        try:
            base_pheno_text = config.get(GENOTYPE_SECTION,"base_pheno")
            
            positions_texts = base_pheno_text.split(",")
            positions = []
            for position_text in positions_texts:
                t = position_text.split(" ")
                t = map(float,t)
                positions.append(t)
            
            base_num_uavs = self.get_num_receivers()
            base_num_steps = len(positions)/base_num_uavs
            
            assert base_num_uavs*base_num_steps==len(positions), "Invalid base configuration"
                                                                         
            
            result = []
            for x in xrange(base_num_uavs):
                base_receiver = []
                base_receiver.append(self.get_base_pos())
                for y in xrange(base_num_steps):
                    base_receiver.append(positions[x*base_num_steps+y])
                result.append(base_receiver)
            return result
        
            
        except ConfigParser.NoOptionError:
            print "Warning defaulting to base position in config"
            
            temp = []
            for x in xrange(self.get_num_receivers()):
                temp.append([self.get_base_pos()])
            return temp
            
            
            

    
class Genotype(BaseGenotype):
    def __init__(self,settings,receiver_set):
        super(Genotype,self).__init__(settings,receiver_set)
        
    def unserialize(self,serialized_receiver_set):
        receiver_step_count = self.settings.get_receiver_step_count()
        
        receiver_set = []
        index = 0
        for index in xrange(0, len(serialized_receiver_set), 2 + receiver_step_count):
            t = []
            t.append(serialized_receiver_set[index])
            t.append(serialized_receiver_set[index+1])
            
            for i2 in xrange(receiver_step_count):
                t.append(serialized_receiver_set[index+2+i2])
            receiver_set.append(t)
        return receiver_set 
    def combine(self,other):
        
        c1 =  self.serialize()
        c2 =  other.serialize()
        
        assert len(c1)==len(c2), "Lengths of genos vary! This should never happen"
        
        if self.settings.crossover_rate > uniform(0,100):
            n1,n2 = self.crossover(c1,c2)
        else:
            n1,n2 = c1,c2
            
        if self.settings.mutation_rate > uniform(0,100):
            n1,n2 = self.mutation(n1,n2)
        
        n1 = self.unserialize(n1)
        n2 = self.unserialize(n2)
        
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
        
        ruav = randint(0,self.settings.get_num_receivers()-1)
        rangle = randint(0,self.settings.get_receiver_step_count()-1)
        
        rindex = ruav * (self.settings.get_receiver_step_count()+2)+2 + rangle
        
        n1[rindex] += gauss(0,mutation_step)
        n2[rindex] += gauss(0,mutation_step)
        
        return n1,n2
