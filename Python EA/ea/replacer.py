#!/usr/bin/python

from random import random
from selection import parse_config as sel_parse
from fitness import parse_config as fit_parse
from utility import select_class
from population import Population

REPLACEMENT_SECTION_NAME = "Replacement"

def parse_config(config):
    classes = [("FullGenerationReplacement", FullGenerationReplacement),
            ("OverProductionReplacement", OverProductionReplacement),
            ("GenerationalMixingReplacement", GenerationalMixingReplacement)]
    clazz = config.get(REPLACEMENT_SECTION_NAME, 'class')
    c = select_class(clazz, classes)
    if c == None:
        raise NameError("Could not find the replacement class {c}".format(c=clazz))
    else:
        return c(config)


class Replacement(object):
    def __init__(self, config):
        self.selection_protocol = sel_parse(config)
        self.fitness = fit_parse(config)
        try:
            self.num_parents_kept = config.getint(REPLACEMENT_SECTION_NAME, 'num_parents_kept')
        except:
            import logging
            log = logging.getLogger('evo')
            log.warn("num_parents_kept is not defined in the config file")
            self.num_parents_kept = 0
    def get_parents_kept(self,population):
        list_of_phenos = population.get_phenos()
        list_of_phenos.sort(key=lambda x: x.fitness(),reverse=True)
        if self.num_parents_kept > 0:
            #print map(lambda x: x.fitness(), list_of_phenos)
            return list_of_phenos[:self.num_parents_kept]

        else:
            return []

    def replace_generation(self, population):
        pass

class FullGenerationReplacement(Replacement):
    def replace_generation(self,population):
        population_size = len(population)
        list_of_parents_kept = self.get_parents_kept(population)
        num_parents_kept = len(list_of_parents_kept)
        num_children = population_size-num_parents_kept
        selected = self.selection_protocol.select(num_children,population)
        list_of_children = []
        for i in range(0,num_children,2):
            child1,child2 = selected[i].combine(selected[i+1])
            list_of_children.append(child1)
            list_of_children.append(child2)
        
        #list_of_phenos = list_of_parents_kept
        #list_of_phenos.extend(list_of_children)
        #pop = Population(list_of_phenos)
        #pop = self.fitness.calc_fitness(pop)     
        #return pop
        
        
        list_of_phenos = self.fitness.calc_fitness(Population(list_of_children)).get_phenos()
        list_of_phenos.extend(list_of_parents_kept)        
        return Population(list_of_phenos)

class OverProductionReplacement(Replacement):
    def __init__(self, config):
        super(OverProductionReplacement, self).__init__(config)
        self.number_of_children = config.getint(REPLACEMENT_SECTION_NAME, 'num_children')
        assert self.number_of_children%2 == 0, "Number of children should be even!"

    def replace_generation(self,population):
        population_size = len(population)
        list_of_parents_kept = self.get_parents_kept(population)
        num_parents_kept = len(list_of_parents_kept)

        assert population_size < self.number_of_children, "Number of children must be greater than population size!"
        selected = self.selection_protocol.select(self.number_of_children,population)
        list_of_children = []
        for i in range(0,self.number_of_children,2):
            child1,child2 = selected[i].combine(selected[i+1])
            list_of_children.append(child1)
            list_of_children.append(child2)
        population_of_children = self.fitness.calc_fitness(Population(list_of_children))

        list_of_children = population_of_children.get_phenos()

        list_of_children.sort(key=lambda x: x.fitness(),reverse=True)
        
        list_of_phenos = list_of_parents_kept
        list_of_phenos.extend(list_of_children[:population_size-num_parents_kept])
        return Population(list_of_phenos)

class GenerationalMixingReplacement(OverProductionReplacement):
    def replace_generation(self,population):
        population_size = len(population)
        list_of_parents_kept = self.get_parents_kept(population)
        num_parents_kept = len(list_of_parents_kept)

        selected = self.selection_protocol.select(self.number_of_children,population)
        list_of_children = []
        for i in range(0,self.number_of_children,2):
	        child1,child2 = selected[i].combine(selected[i+1])
	        list_of_children.append(child1)
	        list_of_children.append(child2)
        population_of_children= self.fitness.calc_fitness(Population(list_of_children))

        
#        list_of_children.sort(key=lambda x: x.fitness(),reverse=True)

        list_of_phenos = population.get_phenos()
        list_of_phenos.extend(list_of_children)
        
        new_population = Population(list_of_phenos)
        
        selected_phenos = self.selection_protocol.select(population_size,new_population)

        selected_phenos.extend(list_of_parents_kept)

        return Population(selected_phenos)

if __name__ == "__main__":
    print "Replacer is being run as main file, doing self tests:"
    from phenotype import DummyPheno
    from random import randint
    from selection import *
    from population import Population
    t = []
    for x in xrange(100):
        t.append(DummyPheno(randint(-100,100)))

    class DummyFitness(object):
        def calc_fitness(self,population):
            return population

    def compare_population(pop1,pop2):
        sum = 0.0
        for i1,i2 in zip(pop1,pop2):
            diff = i1.get_value() - i2.get_value()
            sum += diff*diff
        return  sum

    pop = Population(t)
    selection_protocol = RouletteSelection()
    fitness = DummyFitness()
    number_of_children = 120

    fgen = FullGenerationReplacer(selection_protocol, fitness)
    npop1 = fgen.replace_generation(pop)
    print "FullGenerationReplacement: ",compare_population(pop,npop1)

    op = OverProduction(selection_protocol,fitness, number_of_children)
    npop2 = op.replace_generation(pop)
    print "OverProduction: ",compare_population(pop,npop2)

    genmix = GenerationalMixingReplacement(selection_protocol,fitness, number_of_children)
    npop3 = genmix.replace_generation(pop)
    print "GenerationalMixingReplacement: ",compare_population(pop,npop3)
        


