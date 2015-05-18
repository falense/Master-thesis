#!/usr/bin/python

import logging
from utility import list_modules,load_module
from config import GLOBAL_SECTION

class GenoLoader(object):
    def __init__(self,configuration):
        self.__configuration = configuration
        self.__population_size = configuration.getint(GLOBAL_SECTION,"population_size")
        assert self.__population_size%2 == 0, "Population size must be even!"
        self.__genotype = configuration.get(GLOBAL_SECTION,"genotype")
    def get_possible_genotypes(self):
        path = "./genotypes"
        return list_modules(path)
    def get_genomes(self):
        genotype_module = load_module("genotypes",self.__genotype,["make_generation"])
        p = genotype_module.make_generation(self.__population_size,self.__configuration)
        return p




