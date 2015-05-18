#!/usr/bin/python

from random import random,randint
from math import exp
from utility import select_class

SELECTION_SECTION = "Selection"

def tournament_selection(amount,fitness_pheno_list):
    e = 0.2 #THis should be defined elsewhere
    K = 10 #This should also be defined elsewhere
    length = len(fitness_pheno_list)    
    selected = []
        
    for i in range(amount):

        erand = random()
        if e > erand:
            r = randint(0,length-1)
            selected.append(fitness_pheno_list[r][1])
        else:      
            best = None 
            for j in range(K):
                r = randint(0,length-1)
                current = fitness_pheno_list[r]
                if best is None or best[0] < current[0]:
                    best = current
            selected.append(best[1])
            
    return selected

def roulette_selection(amount, fitness_pheno_list):
    '''Roulette selection which selects the given amount of
    individuals from a list of phenotypes where the fitness
    is normalize'''
    selected = [0] * amount
    for i in xrange(amount):
	    rand = random()
	    for f,p in fitness_pheno_list:
	        rand -= f
	        if rand <= 0:
	            selected[i] = p
		    break
    assert len(selected) == amount, 'The selected amount does not equal ' + ' the desired amount, was {0} expected {1}'.format(len(selected),amount)

    return selected

def parse_config(config):
    classes = [('RouletteSelection', RouletteSelection),
            ('SigmaScalingSelection', SigmaScalingSelection),
            ('BoltzmanScalingSelection', BoltzmanScalingSelection),
            ('RankScalingSelection', RankScalingSelection)]
    clazz = config.get(SELECTION_SECTION, 'class')
    c = select_class(clazz, classes)
    if c != None:
        return c(config)
    else:
        raise NameError("Could not find the Selection class: {0}".format(clazz))

class Selection(object):
    def __init__(self, config):
        '''Do nothing by design =D'''
        pass
    def select(self, amount, population):
        #Virtual select method ;)
        pass

class RouletteSelection(Selection):
    def select(self,amount, population):
        fitness_total = population.get_sum()
        normalized_fitness_pheno = map(lambda p: (p.fitness()/fitness_total,p),population)
        #print fitness_total
        return roulette_selection(amount,normalized_fitness_pheno)

class SigmaScalingSelection(Selection):
    def select(self,amount, population):
        stddev = population.get_stddev()
        avg = population.get_avg()
        fitness_total = population.get_sum()
        sigma_scaled_fitness = map(lambda p: (1 + (p.fitness() - avg)/(2.0*stddev),p),population)
        normalized_fitness = map(lambda f: (f[0] / fitness_total,f[1]),sigma_scaled_fitness)
        return roulette_selection(amount,normalized_fitness)

class BoltzmanScalingSelection(Selection):
    def select(self,amount, population):
        T = 1 #This needs to be defined somewhere else, T = temperature
        boltzman_scaled_fitness = map(lambda p: exp(p.fitness()/T),population)
        avg_boltzman_fitness = sum(boltzman_scaled_fitness)/len(population)
        boltzman_scaled_fitness = map(lambda f: f / avg_boltzman_fitness,boltzman_scaled_fitness)
        fitness_total = sum(boltzman_scaled_fitness)
        normalized_fitness = map(lambda f: f / fitness_total,boltzman_scaled_fitness)
        return roulette_selection(amount,zip(normalized_fitness,population))
    
class RankScalingSelection(Selection):
    def select(self,amount, population):
        max_fitness = population.get_max()
        min_fitness = population.get_min()
        population.sort()
        normalized_fitness = []
        step_fitness = (max_fitness - min_fitness)/(len(population)-1)

        rank_scaled_fitness = map(lambda rank: min_fitness + step_fitness*(rank+1),range(len(population)))
        total_fitness = sum(rank_scaled_fitness)
        normalized_fitness = map(lambda f: f / total_fitness,rank_scaled_fitness)
        return roulette_selection(amount,zip(normalized_fitness,population))

        
if __name__ == "__main__":
    print "Selection is being run as main file, doing self tests:"
    from phenotype import DummyPheno
    from random import randint
    t = []
    for x in xrange(100):
        t.append(DummyPheno(randint(-100,100)))
    from population import Population
    pop = Population(t)
         
    s = RouletteSelection()
    print "RouletteSelection:"
    for p in s.select(10,pop):
        print p, "(", p.fitness() , ")"
    print

    s = SigmaScalingSelection()
    print "SigmaScalingSelection:"
    for p in s.select(10,pop):
        print p, "(", p.fitness() , ")"
    print


    s = BoltzmanScalingSelection()
    print "BoltzmanScalingSelection:"
    for p in s.select(10,pop):
        print p, "(", p.fitness() , ")"
    print


    s = RankScalingSelection()
    print "RankScalingSelection:"
    for p in s.select(10,pop):
        print p, "(", p.fitness() , ")"
    print
    d1 = DummyPheno(0)
    d2 = DummyPheno(100)
    print d1.pair(d2)

