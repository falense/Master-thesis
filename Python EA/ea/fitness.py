#!/usr/bin/python

from config import GLOBAL_SECTION
from utility import select_class, degToRad
FITNESS_SECTION = 'Fitness'

from math import pi,log, sqrt

def parse_config(config):
    classes = [('HeurFitness', HeurFitness),('GPUFitness', GPUFitness),('ProjectFitness', ProjectFitness),('DummyFitness',DummyFitness)]
    clazz = config.get(FITNESS_SECTION, 'class')
    c = select_class(clazz, classes)
    if c != None:
        return c(config)
    else:
        raise NameError("Could not find the fitness class: {0}".format(clazz))
class DummyFitness(object):
    def __init__(self,configuration):
        pass
    def calc_fitness(self,population):
        for i in population:
            t = (100.0*100.0-float(i.get_value()**2))/(100.0*100.0)
            i.set_fitness(t)
        return population
        
class BasicFitness(object): 
    def __init__(self, config):
        self.grid = self.__parse_grid(config)
        self.step_size = self.__parse_step_size(config)
        self.num_trials = self.__parse_num_trials(config)
        self.seed = self.__parse_seed(config)
        self.noise_stddev = self.__parse_noise(config)
        self.emitter_position = self.__parse_emitter_position(config)
    def __parse_noise(self,config):
        b = config.getfloat(FITNESS_SECTION, 'noise_stddev')
        return b
    def __parse_emitter_position(self,config):
        x = config.getfloat(FITNESS_SECTION, 'emitter_pos_x')
        y = config.getfloat(FITNESS_SECTION, 'emitter_pos_y')
        return (x,y)
    def __parse_grid(self, config):
        x = config.getint(FITNESS_SECTION, 'grid_x')
        y = config.getint(FITNESS_SECTION, 'grid_y')
        return (x, y)
    def __parse_step_size(self, config):
        return config.getint(FITNESS_SECTION, 'step_size')
    def __parse_num_trials(self, config):
        return config.getint(FITNESS_SECTION, 'num_trials')
    def __parse_seed(self, config):
        return config.getint(GLOBAL_SECTION, 'seed')


            

   
class GPUFitness(BasicFitness):
    def __init__(self,config):
        super(GPUFitness,self).__init__(config)
        self.mode = self.__parse_mode(config)
    def __parse_mode(self,config):
        mode = config.getint(FITNESS_SECTION, "mode")
        return mode
    def calc_gpu(self, receiver_positions):
        from nllsCuda import pyMultipleFitness

        #def pyFitness(receiverPositions, emitterPosition, numTrials, noiseStdDev, numSteps, gridMax):
        vals = pyMultipleFitness(receiver_positions,self.emitter_position, self.num_trials,self.noise_stddev, self.step_size, self.grid)
        
        return vals
    def calc_fitness(self, population):
            
            
        vals = self.calc_gpu(map(lambda pheno: pheno.get_position(), population))
        for i, (fit, avg_dev, max_dev, min_dev, variance, abs_bias) in enumerate(vals):
            population[i].set_statistics(avg_dev, max_dev, min_dev, variance, abs_bias)
            
        if self.mode == 0:
            for i, (fit, avg_dev, max_dev, min_dev, variance, abs_bias) in enumerate(vals):
               population[i].set_fitness(100.0/(1.0+avg_dev))
        elif self.mode == 1:
            for i, (fit, avg_dev, max_dev, min_dev, variance, abs_bias) in enumerate(vals):
                population[i].set_fitness(100.0/(1.0+fit*0.0001))
                
                

        return population
class ProjectFitness(GPUFitness):
    def __init__(self,config):
        super(ProjectFitness,self).__init__(config)
        self.rotate_degrees = self.__parse_rotate(config)
    def __parse_rotate(self, config):
        try:
            return config.getint(FITNESS_SECTION, 'rotate_step_degrees')
        except:
            return None
    def calc_fitness(self, population):
        results = [0] * len(population)

        num_steps = int(360/self.rotate_degrees)

        assert num_steps * self.rotate_degrees == 360, "Rotation degrees should make an even rotation"
      
        rotate_radians = degToRad(self.rotate_degrees)
        for step in range(num_steps):
            map(lambda pheno: pheno.rotate(rotate_radians*step), population.get_phenos())
            vals = self.calc_gpu(map(lambda pheno: pheno.get_position(), population))
            
            for x in range(len(population)):
                results[x] += vals[x][0]
        
        norm_value = 950*num_steps #sqrt(self.grid[0]**2 +self.grid[1]**2)*num_steps
        for i, val in enumerate(results):
            #fit = 100.0*(1-(val/norm_value))
            fit = 100.0/(1.0+val*0.0001)
            #print val, norm_value, fit
            population[i].set_fitness(fit)
        return population


class HeurFitness(BasicFitness):
    def __init__(self,config):
        super(HeurFitness,self).__init__(config)
        self.base_position = self.__parse_base_position(config)
        self.num_simulations = self.__parse_num_simulations(config)
        self.num_receivers = self.__parse_num_receivers(config)
        
    def __parse_base_position(self,config):
        x = config.getint(FITNESS_SECTION, "base_pos_x")
        y = config.getint(FITNESS_SECTION, "base_pos_y")
        return (x,y)
    def __parse_num_simulations(self,config):
        n = config.getint(FITNESS_SECTION, "num_simulations")
        return n
    def __parse_num_receivers(self,config):
        n = config.getint(GLOBAL_SECTION, "num_receivers")
        return n
    def make_uav_positions(self, num_receivers, base_position, angles):
        from fitness_heuristics import make_receiver
        from utility import degToRad
            
        uavPositions = []
        
        for i, angle in enumerate(angles):
            rads = degToRad(angle)
            uavPositions.append(make_receiver(self.base_position,rads,50))
        
        return uavPositions 
    def calc_gpu(self, receiver_positions):
        from nllsCuda import pyMultipleFitness

        #def pyFitness(receiverPositions, emitterPosition, numTrials, noiseStdDev, numSteps, gridMax):
        vals = pyMultipleFitness(receiver_positions,self.emitter_position, 100,self.noise_stddev, self.step_size, self.grid)
        
        return vals
        
    def calc_fitness(self,population):
        from fitness_heuristics import simulate
        from heuristics.AttractionAgent import AttractionAgent
        from random import getstate, setstate
        import numpy as np
        
        state = getstate()
        for i,individ in enumerate(population):
            heuristics_params = individ.get_heur_params()
            uav_positions = self.make_uav_positions(self.num_receivers,self.base_position, heuristics_params[1:])
            
            position_sets = []
            steps = []
            
            for t in xrange(self.num_simulations):
                setstate(state)
                samplesUsed, samplePositions = simulate(self.num_trials, self.grid, self.emitter_position, self.noise_stddev, uav_positions, AttractionAgent, heuristics_params, 8)
                position_sets.append(samplePositions)
                steps.append(samplesUsed)
                
            vals = self.calc_gpu(position_sets)
            
            
            fits = []
            for i, (fit, avg_dev, max_dev, min_dev, variance, abs_bias) in enumerate(vals):
                fits.append(fit)
            
            fits = np.array(fits)
            fit_avg = fits.sum()/len(fits)
            
            steps = np.array(steps)
            steps_avg = steps.sum()/len(steps)
            
            individ.set_fitness(100.0/(1.0+fit_avg*0.0001))
            
            print heuristics_params, fit_avg, steps_avg, 100.0/(1.0+fit_avg*0.0001)
            
        return population
