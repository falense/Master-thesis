#!/usr/bin/python

import logging
from utility import list_modules,load_module

from config import GLOBAL_SECTION

class PhenoLoader(object):
    
    def __init__(self, configuration):
        self.__name = configuration.get(GLOBAL_SECTION,"phenotype")
    def get_possible_phenotypes(self):
        path = "./phenotypes"
        return list_modules(path)
    def get_phenotype(self):
        phenotype_module = load_module("phenotypes",self.__name,["Phenotype"])
        p = phenotype_module.Phenotype
        return p

