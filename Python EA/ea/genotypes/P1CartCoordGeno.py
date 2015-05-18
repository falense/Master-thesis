
#!/usr/bin/python
from random import randint, uniform
from BaseGeno import *
from math import cos, sin, acos, asin, pow, sqrt
xg = None
yg = None
def make_receiver(settings):
    global xg,yg
    #x = uniform(0,settings.get_max_receiver_x())
    #y = uniform(0,settings.get_max_receiver_y())
    x = xg
    y = yg
    #distance = sqrt(pow(x-settings.emitter[0],2)+pow(y-settings.emitter[1],2))
    #if distance < settings.exclusion_radius:
    #    return make_receiver(settings)
    return (x,y)
def make_receiver_set(settings):
    global xg,yg
    xg = uniform(0,settings.get_max_receiver_x())
    yg = uniform(0,settings.get_max_receiver_y())
    distance = sqrt(pow(xg-settings.emitter[0],2)+pow(yg-settings.emitter[1],2))
    if distance < settings.exclusion_radius:
        return make_receiver_set(settings)

    receiver_set = []
    for i in range(settings.get_num_receivers()):
        receiver_set.append(make_receiver(settings));
    return receiver_set
def make_generation(population_size,configuration):
    pop = []
    settings = GenoSettings(configuration)
    for i in xrange(population_size):
        t = Genotype(settings,make_receiver_set(settings))
        pop.append(t)
    return pop

class GenoSettings(BaseSettings):
    def __init__(self,config):
        super(GenoSettings,self).__init__(config)
    def parse_receiver_freedom(self,config):
        self.maxx = config.getint(GENOTYPE_SECTION, 'max_receiver_x')
        self.maxy = config.getint(GENOTYPE_SECTION, 'max_receiver_y')
        self.mutation_rate = config.getfloat(GENOTYPE_SECTION, 'mutation_rate')
        self.mutation_step = config.getfloat(GENOTYPE_SECTION, 'mutation_step')
        self.exclusion_radius = config.getfloat(GENOTYPE_SECTION, 'exclusion_radius')
    def get_max_receiver_x(self):
        return self.maxx
    def get_max_receiver_y(self):
        return self.maxy
def unserialize_receiver_set(serialized_receiver_set):
    receiver_set = []
    index = 0
    while(index+2 <= len(serialized_receiver_set)):
        t = (serialized_receiver_set[index+0],serialized_receiver_set[index+1])#serialized_receiver_set[index+2])
        receiver_set.append(t)
        index = index + 2
        #print t,
    #print
    return receiver_set
class Genotype(BaseGenotype):
    def __init__(self,settings,receiver_set):
        super(Genotype,self).__init__(settings,receiver_set)
    def combine(self,other):
        c1 = self.serialize(self.receiver_set)
        c2 = self.serialize(other.receiver_set)
        assert len(c1)==len(c2), "Lengths of genos vary! This should never happen"
        n1 = []
        n2 = []
        crossover = randint(0,len(c1))
        mutation_rate = self.settings.mutation_rate
        mutation_step = self.settings.mutation_step
        exclusion_radius = self.settings.exclusion_radius
        for i in range(crossover):
            if uniform(0,100) < mutation_rate:
                n1.append(c1[i]+uniform(-mutation_step,mutation_step))
                n2.append(c2[i]+uniform(-mutation_step,mutation_step))
            else:
                n1.append(c1[i])
                n2.append(c2[i])
        for i in range(crossover,len(c1)):
            if uniform(0,100) < mutation_rate:
                n1.append(c2[i]+uniform(-mutation_step,mutation_step))
                n2.append(c1[i]+uniform(-mutation_step,mutation_step))
            else: 
                n1.append(c2[i])
                n2.append(c1[i])
        emitter_x, emitter_y = self.settings.emitter
        for i in range(0,len(c1),2):
            distance1 = sqrt(pow(emitter_x-n1[i],2) + pow(emitter_y-n1[i+1],2))
            if (distance1 < exclusion_radius):
                angle = acos((n1[i] - emitter_x)/exclusion_radius)
                n1[i] = exclusion_radius*cos(angle)
                n1[i+1] = exclusion_radius*sin(angle)

            distance2 = sqrt(pow(emitter_x-n2[i],2) + pow(emitter_y-n2[i+1],2))  
            if (distance2 < exclusion_radius):
                angle = acos((n2[i] - emitter_x)/exclusion_radius)
                n2[i] = exclusion_radius*cos(angle)
                n2[i+1] = exclusion_radius*sin(angle)

            if n1[i] > self.settings.maxx:
                n1[i] = self.settings.maxx
            if n1[i+1] > self.settings.maxy:
                n1[i+1] = self.settings.maxy

            if n2[i] > self.settings.maxx:
                n2[i] = self.settings.maxx
            if n2[i+1] > self.settings.maxy:
                n2[i+1] = self.settings.maxy
            
        n1 = unserialize_receiver_set(n1);
        n2 = unserialize_receiver_set(n2);
        return (Genotype(self.settings,n1),Genotype(self.settings,n2))
