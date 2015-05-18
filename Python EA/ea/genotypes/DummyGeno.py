
#!/usr/bin/python
from random import randint

def make_generation(population_size,configuration):
    pop = []
    settings = GenoSettings(configuration)
    for i in xrange(population_size):
        t = Genotype(settings,randint(-100,100))
        pop.append(t)
    return pop

class GenoSettings(object):
    def __init__(self,configuration):
        pass


class Genotype(object):
    
    def __init__(self,settings,value):
        self.__settings = settings
        self.__value = value

    def get_value(self):
        return self.__value
    def __repr__(self):
        return str(self.__value)
    def pair(self,other):
        c1 = (self.__value + 2.0 * other.get_value())/3
        c2 = (2.0 * self.__value + other.get_value())/3
        return (Genotype(self.__settings,c1),Genotype(self.__settings,c2))
