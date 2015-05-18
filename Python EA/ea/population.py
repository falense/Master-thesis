#!/usr/bin/python

from math import sqrt

class Population(object):
    def __init__(self, phenos):
        self.__phenos = phenos
        #Below done in order to lazy read avg
        self.__avg = None
        self.__stddev = None
        self.__max = None
        self.__min = None
        self.__sum = None

    def get_phenos(self):
        return self.__phenos

    def get_sum(self):
        if self.__sum == None:
            fit = self.__phenos
            s = reduce(lambda acc, n: acc + n.fitness(), fit, 0)
            self.__sum = s
        return self.__sum

    def get_avg(self):
        if self.__avg == None:
            fit = self.__phenos
            self.__avg = self.get_sum() / len(fit)
        return self.__avg

    def sort(self):
        self.__phenos.sort(key=lambda f: f.fitness())

    def get_stddev(self):
        if self.__stddev == None:
            avg = self.get_avg()
            fit = self.__phenos
            s = reduce(lambda acc, n: acc + (n.fitness()-avg)**2, fit, 0)
            self.__stdev = sqrt(s / len(fit))
        return self.__stdev
    
    def get_min_pheno(self):
        if self.__min == None:
            fit = self.__phenos
            self.__min = min(fit, key=lambda t: t.fitness())
        return self.__min

    def get_max_pheno(self):
        if self.__max == None:
            fit = self.__phenos
            self.__max = max(fit, key=lambda t: t.fitness())
        return self.__max

    def get_min(self):
        return self.get_min_pheno().fitness()

    def get_max(self):
        return self.get_max_pheno().fitness()

    def __getitem__(self,index):
        return self.__phenos[index]

    def __iter__(self):
        return self.__phenos.__iter__()

    def __len__(self):
        return len(self.__phenos)

    def __contains__(self, item):
        return item in self.__phenos
