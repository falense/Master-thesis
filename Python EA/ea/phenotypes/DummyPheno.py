
#!/usr/bin/python

class Phenotype(object):
    def __init__(self,genome):
        self.__value = genome.get_value()
        self.__genome = genome
    def fitness(self):
        return self.__fit
    def set_fitness(self,fit):
        self.__fit = fit
    def __repr__(self):
        return str(self.__value)
    def get_value(self):
        return self.__value
    def get_genome(self):
        return self.__genome
    def pair(self,other):
        child1, child2 = self.__genome.pair(other.get_genome())
        return Phenotype(child1),Phenotype(child2)

