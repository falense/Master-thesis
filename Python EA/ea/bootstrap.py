#!/usr/bin/python

from replacer import parse_config as rep_conf
from genotype import GenoLoader
from phenotype import PhenoLoader
from progress import parse_config as prog_conf
from population import Population
from config import GLOBAL_SECTION

class Bootstrap(object):
    def __init__(self, config):
        self.__config = config

    def run(self):
        '''Run the bootstrap stage which will return the needed configuration
        to execute the EA algorithm, this method will pass the configuration
        to the needed modules and will initiate all needed classes'''
        parser = rep_conf(self.__config)
        g = GenoLoader(self.__config)
        p = PhenoLoader(self.__config)
        pheno = p.get_phenotype()
        init_pop = g.get_genomes()
        pop = Population(map(pheno, init_pop))
        parser.fitness.calc_fitness(pop)
        progress = prog_conf(self.__config)
        loops = self.__config.getint(GLOBAL_SECTION, 'loops')
        return parser, pop, progress, loops
