
#!/usr/bin/python
from random import randint, random, gauss
from BaseGeno import *
gr = None
gth = None
def make_receiver(settings):
    r = randint(settings.get_min_radius(),settings.get_max_radius())
    th = random()*2.0*3.14
    return (r,th)
    #global gr, gth
    #return (gr,gth)

def make_receiver_set(settings):
    receiver_set = []

    global gr, gth
    gr = randint(settings.get_min_radius(),settings.get_max_radius())
    gth = random()*2.0*3.14

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
    def parse_mutation(self,config):
        self.mutation_rate = config.getfloat(GENOTYPE_SECTION, 'mutation_rate')
        self.radius_mutation_stddev = config.getfloat(GENOTYPE_SECTION, 'radius_mutation_stddev')
        self.theta_mutation_stddev = config.getfloat(GENOTYPE_SECTION, 'theta_mutation_stddev')
    def __init__(self,config):
        super(GenoSettings,self).__init__(config)
        self.parse_mutation(config)
    def parse_receiver_freedom(self,config):
        self.max_radius = config.getfloat(GENOTYPE_SECTION, 'max_radius')
        self.min_radius = config.getfloat(GENOTYPE_SECTION, 'min_radius')
    def get_max_radius(self):
        return self.max_radius
    def get_min_radius(self):
        return self.min_radius
def unserialize_receiver_set(serialized_receiver_set):
    receiver_set = []
    index = 0
    while(index+2 <= len(serialized_receiver_set)):
        t = (serialized_receiver_set[index+0],serialized_receiver_set[index+1])
        receiver_set.append(t)
        index = index + 2
    return receiver_set
class Genotype(BaseGenotype):
    def __init__(self,settings,receiver_set):
        super(Genotype,self).__init__(settings,receiver_set)
    def combine(self,other):
        c1 = self.serialize()
        c2 = self.serialize()
        assert len(c1)==len(c2), "Lengths of genos vary! This should never happen"
        n1 = []
        n2 = []
        crossover = randint(0,len(c1))
        mutation_rate = self.settings.mutation_rate
        theta_mutation_stddev = self.settings.theta_mutation_stddev
        radius_mutation_stddev = self.settings.radius_mutation_stddev

        for i in range(len(c1)):
            if i%2 == 0:
                mutation_step = radius_mutation_stddev
            else:
                mutation_step = theta_mutation_stddev

            t1 = c1[i]
            t2 = c2[i]

            if randint(0,100) < mutation_rate:
                t1 = t1 + gauss(0.0,mutation_step)
                t2 = t2 + gauss(0.0,mutation_step)
            
            if i%2 == 1:
                if t1 > 6.28:
                    t1 = t1 - 6.28
                if t2 > 6.28:
                    t2 = t2 - 6.28
            else:
                if t1 > self.settings.max_radius:
                    t1 = self.settings.max_radius
                if t2 > self.settings.max_radius:
                    t2 = self.settings.max_radius

                if t1 < self.settings.min_radius:
                    t1 = self.settings.min_radius
                if t2 < self.settings.min_radius:
                    t2 = self.settings.min_radius


            if i < crossover:
                n1.append(t1)
                n2.append(t2)
            else:
                n1.append(t2)
                n2.append(t1)
            
        n1 = unserialize_receiver_set(n1);
        n2 = unserialize_receiver_set(n2);
        return (Genotype(self.settings,n1),Genotype(self.settings,n2))
