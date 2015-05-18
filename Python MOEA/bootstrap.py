

import random
import numpy

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

from math import cos, sin, pi, sqrt
from nllsCuda import pyFitnessAlt,pyPredict

def degToRad(deg):
	return deg/360.0 * 3.14*2.0
        
def convert_ind_to_positions(conf,individual):
    positions = []
    for i in xrange(conf.NUM_UAVS):
        x = conf.BASE_POSITION[0]
        y = conf.BASE_POSITION[1]
        previous = 0.0
        index = i*(conf.NUM_STEPS+2)
        if individual[index] != 0:
            length = individual[index+1]
            for offset in xrange(conf.NUM_STEPS):
                angle = individual[index+2+offset]
                vec_x,vec_y = (cos(degToRad(previous+angle)),sin(degToRad(previous+angle)))
                abs_vector = sqrt(vec_x**2 + vec_y**2)
                
                x += vec_x/abs_vector * length
                y += vec_y/abs_vector * length
                positions.append((x,y))
                previous += angle
    return positions
    
def convert_ind_to_distance(conf,individual):
    distance = 0.0
    for i in xrange(conf.NUM_UAVS):
        index = i*(conf.NUM_STEPS+2)
        if individual[index] != 0:
            length = individual[index+1]
            part_distance = length*conf.NUM_STEPS
            if part_distance > distance:
                distance = part_distance
    return distance
    
def convert_ind_to_uav_count(conf,individual):
    uav_count = 0
    for i in xrange(conf.NUM_UAVS):
        index = i*(conf.NUM_STEPS+2)
        if individual[index] != 0:
            uav_count += 1
    return uav_count

def bootstrap(conf):
    creator.create("Fitness", base.Fitness, weights=(-1.0, -1.0))
    creator.create("Individual", list, fitness=creator.Fitness, step_count=None)

    toolbox = base.Toolbox()

    def initConfiguration(individ_class, step_count,uav_count):
        r = individ_class()
        for uav in xrange(uav_count):
            
            if conf.fixed_uav_count:
                uav_enabled = 1
            else:
                uav_enabled = random.randint(0,1)
                
            r.append(uav_enabled)
                
            if conf.fixed_step:
                step_length = 50
            else:
                step_length = random.uniform(0,conf.uav_max_step_length)
            r.append(step_length)
                
            for step in xrange(step_count):
                step_angle = random.uniform(0,360)
                r.append(step_angle)
                
                
        if convert_ind_to_uav_count(conf,r) == 0:
            del r
            return initConfiguration(individ_class,step_count,uav_count)
        else:
            return r
    
    toolbox.register("individual", initConfiguration, creator.Individual, conf.NUM_STEPS, conf.NUM_UAVS)
  
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def evaluate(individual):
        positions = convert_ind_to_positions(conf,individual)
        distance = convert_ind_to_distance(conf,individual)
        uav_count = convert_ind_to_uav_count(conf,individual)
        
        fit, avg_dev, max_dev, min_dev, variance = pyFitnessAlt(positions, conf.emitter_position, conf.num_trials,conf.noise_stddev, conf.step_size, conf.grid)
        
        return fit, avg_dev, max_dev, min_dev, variance, distance, uav_count

    evaluate = conf.gen_objective_function(evaluate)
    toolbox.register("evaluate", evaluate)
    
    
    def cxOnePoint(ind1, ind2):
        size = min(len(ind1), len(ind2))
        cxpoint = random.randint(1, size - 1)
        
        tmp_ind1 = ind2[:cxpoint] + ind1[cxpoint:]
        tmp_ind2 = ind1[:cxpoint] + ind2[cxpoint:]
        
        emergency_breakout = 10000
        while convert_ind_to_uav_count(conf,tmp_ind1) == 0 or convert_ind_to_uav_count(conf,tmp_ind2) == 0:
            cxpoint = random.randint(1, size - 1)
            tmp_ind1 = ind2[:cxpoint] + ind1[cxpoint:]
            tmp_ind2 = ind1[:cxpoint] + ind2[cxpoint:]
            
            emergency_breakout -= 1
            if emergency_breakout == 0:
                cxpoint = 0
                print "Unable to find a suitable crossover"
                break
                
        ind1[cxpoint:], ind2[cxpoint:] = ind2[cxpoint:], ind1[cxpoint:]
        
        if convert_ind_to_uav_count(conf,ind1) == 0 or convert_ind_to_uav_count(conf,ind2) == 0:
            print "Warning null uavs"
        
        return ind1, ind2
    
    toolbox.register("mate", cxOnePoint)
    
    def mutate(individual):
        uav_index = random.randint(0,conf.NUM_UAVS-1)
        step_index = random.randint(0,conf.NUM_STEPS-1)
        is_uav_enabled = random.randint(0,1)
        
        if is_uav_enabled == 1 and not conf.fixed_uav_count:
            index = uav_index*(conf.NUM_STEPS+2)
            individual[index] = 1-individual[index]
            if convert_ind_to_uav_count(conf,individual) == 0:
                individual[index] = 1-individual[index]
                return mutate(individual)
            else:
                return individual,
        
        
        is_length = random.randint(0,1)
        
        #[uav_enabled1, angle1, length1, angle2, length2, ... , uav_enabled1, angle1, length1, angle2, length2]
        
        if is_length == 1 and not conf.fixed_step:
            index = uav_index*(conf.NUM_STEPS+2)
            individual[index+1] += random.gauss(0,10.0)
            individual[index+1] = min(conf.uav_max_step_length,max(0.0,individual[index+1]))
        else:
            index = uav_index*(conf.NUM_STEPS+2) + step_index + 2
        
            individual[index] += random.gauss(0,10.0)
            if individual[index] > 360:
                individual[index] -= 360.0
            if individual[index] < 0:
                individual[index] += 360.0
        
        if convert_ind_to_uav_count(conf,individual) == 0:
            "Warning a null uav individ was generated"
        return individual,
    
    toolbox.register("mutate", mutate)
    
    toolbox.register("select", tools.selNSGA2)



    MGA_LOGFOLDER = "mga_log"    
    pop = toolbox.population(n=conf.MU)

    hof = tools.ParetoFront()
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean, axis=0)
    stats.register("std", numpy.std, axis=0)
    stats.register("min", numpy.min, axis=0)
    stats.register("max", numpy.max, axis=0)
    
    return pop, toolbox, hof, stats
