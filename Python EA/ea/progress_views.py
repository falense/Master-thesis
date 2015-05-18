#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy as np

from config import GLOBAL_SECTION
from fitness import FITNESS_SECTION
from genotypes.BaseGeno import GENOTYPE_SECTION
from utility import create_folder
import matplotlib.ticker as plticker
import os
from random import randint

class BasicView(object):
    def __init__(self,config,drawing, experiment_folder):
        self.config = config
        self.drawing = drawing
        self.experiment_folder = experiment_folder
        
        
        self.grid_x = self.config.getint(FITNESS_SECTION,"grid_x")
        self.grid_y = self.config.getint(FITNESS_SECTION,"grid_y")

        self.emitter_x = self.config.getint(FITNESS_SECTION,"emitter_pos_x")
        self.emitter_y = self.config.getint(FITNESS_SECTION,"emitter_pos_y")
        self.noise_stddev = self.config.getfloat(FITNESS_SECTION,"noise_stddev")

        self.num_generations = self.config.getint(GLOBAL_SECTION,"loops")
    def get_experiment_subfolder(self,output):
        subfolder_name = os.path.join(self.get_experiment_folder(),output)
        if not os.path.exists(subfolder_name):
            os.makedirs(subfolder_name)
        return subfolder_name
    def update(self,current_gen, population):
        pass

class GenerationFigure(BasicView):
    
    def __init__(self,config, drawing, experiment_folder):   
        super(GenerationFigure, self).__init__(config, drawing, experiment_folder)
        self.figure_folder = create_folder(os.path.join(self.experiment_folder,"figure_generations"))
        
        plt.figure(0)
        text = "EA progress"
        plt.title(text)
        plt.grid(b=True)        
        plt.gcf().canvas.set_window_title(text)
        plt.ylabel('Fitness')
        plt.xlabel('Generation')
        self.best, = plt.plot([], label='Best')
        self.worst, = plt.plot([], label='Worst')
        self.avg, = plt.plot([], label='Average')
        self.stddev, = plt.plot([], label='Std. dev.')
        self.ax = plt.gca()
        self.ax.axis([0,self.num_generations,0,100])

        plt.legend( loc=4)
    def update(self,current_gen, population):
        plt.figure(0)
        self.best.set_xdata(np.append(self.best.get_xdata(), current_gen))
        self.worst.set_xdata(np.append(self.worst.get_xdata(), current_gen))
        self.avg.set_xdata(np.append(self.avg.get_xdata(), current_gen))
        self.stddev.set_xdata(np.append(self.stddev.get_xdata(), current_gen))

        self.best.set_ydata(np.append(self.best.get_ydata(), population.get_max()))
        self.worst.set_ydata(np.append(self.worst.get_ydata(), population.get_min()))
        self.avg.set_ydata(np.append(self.avg.get_ydata(), population.get_avg()))
        self.stddev.set_ydata(np.append(self.stddev.get_ydata(), population.get_stddev()))

        loc = plticker.MultipleLocator(base=(self.num_generations/10))
        self.ax.xaxis.set_major_locator(loc)
        loc = plticker.MultipleLocator(base=10.0)
        self.ax.yaxis.set_major_locator(loc)
        self.ax.relim()
        self.ax.autoscale_view()
        plt.savefig(os.path.join(self.figure_folder,"generation_%s.jpg" % current_gen))
        plt.draw()
        
class BestPhenoFigure(BasicView):
    
    def __init__(self,config, drawing, experiment_folder):
        
        super(BestPhenoFigure, self).__init__(config, drawing, experiment_folder)
        self.figure_folder = create_folder(os.path.join(self.experiment_folder,"figure_best"))
        plt.figure(1,figsize=(8, 8))
        text = "Best phenome"
        plt.title(text)
        plt.grid(b=True)        
        plt.gcf().canvas.set_window_title(text)
        self.bfg = plt.gcf().gca()
        self.bfg_ax = plt.gca()
        self.bfg_ax.axis([0,self.grid_x,0,self.grid_y])
        self.bfg_ax.set_aspect('equal')
    def update(self,current_gen, population):
        plt.figure(1)
        self.bfg.cla()
        
        self.bfg.set_xlabel("X-axis")
        self.bfg.set_ylabel("Y-axis")
        self.bfg.grid(b=True)
        title = "Best configuration"
        self.bfg.set_title(title)

        best = population.get_max_pheno()
        c1 = self.drawing.make_emitter_patch()
        self.bfg.add_artist(c1)
        
        self.drawing.plot_pheno(self.bfg, best)
        
        
        c1 = self.drawing.make_emitter_patch()
        rp = self.drawing.make_receiver_patch(0,0)
        plt.legend([c1, rp], ["Emitter", "Receiver"],loc=4)
        
        plt.savefig(os.path.join(self.figure_folder,"generation_%s.jpg" % current_gen))
        plt.draw()
class PopulationPhenoFigure(BasicView):
    
    def __init__(self,config, drawing, experiment_folder):
        
        super(PopulationPhenoFigure, self).__init__(config, drawing, experiment_folder)
        self.figure_folder = create_folder(os.path.join(self.experiment_folder,"figure_pop_phenomes"))
        plt.figure(5,figsize=(8, 8))
        text = "Phenomes in population"
        plt.title(text)
        plt.grid(b=True)        
        plt.gcf().canvas.set_window_title(text)
        self.bfg = plt.gcf().gca()
        self.bfg_ax = plt.gca()
        
        
        self.bfg_ax.set_aspect('equal')
        self.bfg_ax.axis([0,self.grid_x,0,self.grid_y])
    def update(self,current_gen, population):
        plt.figure(5)
        self.bfg.cla()
        
        self.bfg.set_xlabel("X-axis")
        self.bfg.set_ylabel("Y-axis")
        self.bfg.grid(b=True)
        text = "Phenomes in population"
        self.bfg.set_title(text)

        c1 = self.drawing.make_emitter_patch()
        self.bfg.add_artist(c1)
        
        for indivi in population:
            self.drawing.plot_pheno(self.bfg, indivi, draw_points=False)
        
        
        c1 = self.drawing.make_emitter_patch()
        plt.legend([c1], ["Emitter"],loc=4)
        
        plt.savefig(os.path.join(self.figure_folder,"generation_%s.jpg" % current_gen))
        plt.draw()
    
    

class PopulationSampleFigure(BasicView):
    def __init__(self,config, drawing, experiment_folder):
        super(PopulationSampleFigure, self).__init__(config, drawing, experiment_folder)
        self.figure_folder = create_folder(os.path.join(self.experiment_folder,"figure_population"))
        self.num_plots_sqrt = 3
        self.tfig,self.pf_subplots = plt.subplots(self.num_plots_sqrt,self.num_plots_sqrt)
        text = "Popluation"
        plt.gcf().canvas.set_window_title(text)
        for i in xrange(self.num_plots_sqrt):
            for j in xrange(self.num_plots_sqrt):
                self.pf_subplots[i,j].axis([0,self.grid_x,0,self.grid_y])
                
                #self.pf_subplots[i,j].ylabel("Y-axis")
                
    def update(self,current_gen, population):
        phenos = population.get_phenos()
        for i in xrange(self.num_plots_sqrt):
            for j in xrange(self.num_plots_sqrt):
                rindex = randint(0,len(phenos)-1)
                rpheno = phenos[rindex]
                self.pf_subplots[i,j].cla()
                self.pf_subplots[i,j].grid(b=True)
                self.drawing.plot_pheno(self.pf_subplots[i,j],rpheno)
        
        self.tfig.canvas.draw()
        self.tfig.savefig(os.path.join(self.figure_folder,"generation_%s.jpg" % current_gen))




class BestPhenoPredictionsFigure(BasicView):
    def __init__(self,config, drawing, experiment_folder):
        super(BestPhenoPredictionsFigure, self).__init__(config, drawing, experiment_folder)
        self.figure_folder = create_folder(os.path.join(self.experiment_folder,"figure_best_predictions"))
        plt.figure(3,figsize=(8, 8))
        text = "Best phenome with predictions"
        plt.title(text)
        plt.grid(b=True)        
        plt.gcf().canvas.set_window_title(text)
        self.bfg_predictions = plt.gcf().gca()
        self.bpf_predictions_ax = plt.gca()
        self.bpf_predictions_ax.axis([0,self.grid_x,0,self.grid_y])
        self.bpf_predictions_ax.set_aspect('equal')
        
    def simulate_predictions(self,phenome,num_trials):
        from nllsCuda import pyPredict, pyQxy, pyMultipleFitness
        from Environment import Environment
        env = Environment((self.emitter_x, self.emitter_y),10.0,self.noise_stddev)

        samples = []
        for trial in xrange(num_trials):
            t = []
            for position in phenome.get_position():
                x,y = position
                t.append((x,y,env.MeasuredPower(x,y)))
            samples.append(t)
            
            
        results = pyPredict(samples,[512,512],(self.grid_x ,self.grid_y))

        return results
    def update(self,current_gen, population):    
        best = population.get_max_pheno()
        plt.figure(3)
        self.bfg_predictions.cla()
        
        self.bfg_predictions.set_xlabel("X-axis")
        self.bfg_predictions.set_ylabel("Y-axis")
        self.bfg_predictions.grid(b=True)
        title = "Best phenome with predictions"
        self.bfg_predictions.set_title(title)
        
        predictions = self.simulate_predictions(best,1000)
        
        for x,y in predictions:
            c = self.drawing.make_prediction_patch(x,y)
            self.bfg_predictions.add_artist(c)
        
        
        self.drawing.plot_pheno(self.bfg_predictions,  best)
        
        text = "Fitness: " + str(round(best.fitness(),2))
        plt.text(0.85,0.95,text, horizontalalignment='center', verticalalignment='center',transform=self.bpf_predictions_ax.transAxes)
        
        
        
        c1 = self.drawing.make_emitter_patch()
        rp = self.drawing.make_receiver_patch(0,0)
        plt.legend([c1, rp], ["Emitter", "Receiver"],loc=4)
        
        plt.savefig(os.path.join(self.figure_folder,"generation_%s.jpg" % current_gen))
        plt.draw()
