#!/usr/bin/python

PROGRESS_SECTION = 'Progress'

import matplotlib.pyplot as plt
import matplotlib.pylab
import matplotlib.animation as animation
import matplotlib.ticker as plticker
import numpy
import datetime
import os

from utility import select_class, create_folder
from multiprocessing import Process
from shutil import copy2
from config import GLOBAL_SECTION
from fitness import FITNESS_SECTION
from progress_views import *
from progress_drawing import * 

def parse_config(config):
	clazz = config.get(PROGRESS_SECTION, 'class')
	classes = [('Progress', Progress),
			   ('GraphProgress', GraphProgress)]
	c = select_class(clazz, classes)
	if c != None:
		return c(config)
	else:
		raise NameError("Could not find the Progress class: {0}".format(clazz))

class Progress(object):
    
    def __init__(self, config):
        self.__experiment_name = str(datetime.datetime.now().strftime("%d-%m-%Y_%H%M%S"))
        config_filename = config.get(GLOBAL_SECTION,"config_filename")
        
        config_file = open(os.path.join(self.get_experiment_folder(),os.path.basename(config_filename)),"w+")
        config.write(config_file)
        config_file.close()
        
        self.dump_folder = create_folder(os.path.join(self.get_experiment_folder(),"population_dump"))
        
        self.config = config
    def get_experiment_folder(self):
        folder_name = os.path.join("./experiments/",self.__experiment_name)
        return create_folder(folder_name)
    def display_statistics(self,cur_gen,  pop):
        print "GEN%s Fitness: Avg %s, StdDev %s, Max %s, Min %s" % (cur_gen, pop.get_avg(), pop.get_stddev(), pop.get_max(), pop.get_min())
    def add(self,current_gen, population):
        self.dump_population(current_gen,population)
        self.display_statistics(current_gen, population)
    def dump_population(self,current_gen, population):
        population_file = os.path.join(self.dump_folder,"generation_%s.txt" % current_gen)
        f = open(population_file,"w")
        for pheno in population:
            f.write(str(pheno) + "\n")
        f.close()
        

class GraphProgress(Progress):
    def __init__(self, config):
        super(GraphProgress, self).__init__(config)
        plt.close("all")
        
        try:
            drawing_class = self.config.get(PROGRESS_SECTION, "drawer")
            
            if drawing_class == "Path":
                self.drawing = PathDrawing(config)
            elif drawing_class == "PathIncr":
                self.drawing = PathIncrDrawing(config)
            else:
                self.drawing = BasicDrawing(config)
        except:
            self.drawing = BasicDrawing(config)
            
        self.views = []
        
        try:
            view = GenerationFigure(self.config,self.drawing, self.get_experiment_folder())
            self.views.append(view)
        except:
            print "Generation figure crashed"
            import traceback, sys
            traceback.print_exc(file=sys.stdout)
        
        try:
            view = BestPhenoFigure(self.config,self.drawing, self.get_experiment_folder())
            self.views.append(view)
        except:
            print "Best pheno figure crashed"
            import traceback, sys
            traceback.print_exc(file=sys.stdout)
        
        try:
            view = PopulationPhenoFigure(self.config,self.drawing, self.get_experiment_folder())
            self.views.append(view)
        except:
            print "Population pheno figure crashed"
            import traceback, sys
            traceback.print_exc(file=sys.stdout)
        
        try:
            view = PopulationSampleFigure(self.config,self.drawing, self.get_experiment_folder())
            self.views.append(view)
        except:
            print "Population sample figure crashed"
            import traceback, sys
            traceback.print_exc(file=sys.stdout)
        
        try:
            view = BestPhenoPredictionsFigure(self.config,self.drawing, self.get_experiment_folder())
            self.views.append(view)
        except:
            print "Best pheno predictions figure crashed"
            import traceback, sys
            traceback.print_exc(file=sys.stdout)
        
        
        plt.ion()
        plt.show()

    def add(self,current_gen, population):
        for view in self.views:
            view.update(current_gen, population)
        self.dump_population(current_gen,population)
        


   
