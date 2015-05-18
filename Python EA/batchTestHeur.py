
from ea.fitness_heuristics import simulate
from ea.heuristics.AttractionAgent import AttractionAgent
from random import getstate, setstate, seed
import numpy as np
from ea.fitness_heuristics import make_receiver
from ea.utility import degToRad
from nllsCuda import pyMultipleFitness
from math import sqrt

def make_uav_positions(num_receivers, base_position, angles):
        
    uavPositions = []
    
    for i, angle in enumerate(angles):
        rads = degToRad(angle)
        uavPositions.append(make_receiver(base_position,rads,50))
    
    return uavPositions 
    
def generate_table(uav_count, noise_stddev, distance, max_steps):
    print uav_count, noise_stddev, distance, max_steps
    
    filename = "UAVCount%s_Noise%s_Distance%s.csv" % (uav_count, noise_stddev, distance)
    f = open(filename, "w")
    
    seed(1)
    state = getstate()
    
    base_point = [330.0 + distance/sqrt(2.0), 330.0 + distance/sqrt(2.0)]
    
    for force in np.arange(0.0,1.0,0.05):
        for offset in np.arange(0,360,20):
        
            heuristics_params = [force] #force, 225+offset,45-60+offset,45+60+offset]
            
            step_angle = 360.0 / uav_count
            
            for i in xrange(uav_count):
                angle = step_angle * i
                heuristics_params.append(45.0 + angle + offset)
                
            
            uav_positions = make_uav_positions(len(heuristics_params)-1,base_point, heuristics_params[1:])
            
            position_sets = []
            steps = []
            
            for t in xrange(10):
                setstate(state)
                samplesUsed, samplePositions = simulate(10, [1000,1000], [330.0,330.0], noise_stddev, uav_positions, AttractionAgent, heuristics_params, max_steps)
                position_sets.append(samplePositions)
                steps.append(samplesUsed)
                
            vals = pyMultipleFitness(position_sets,[330.0,330.0], 100, noise_stddev, 4, [1000,1000])
            
            
            fits = []
            for i, (fit, avg_dev, max_dev, min_dev, variance, abs_bias) in enumerate(vals):
                fits.append(fit)
            
            fits = np.array(fits)
            fit_avg = fits.sum()/len(fits)
            
            steps = np.array(steps)
            steps_avg = steps.sum()/len(steps)
            
            fit_norm = 100.0/(1.0+fit_avg*0.0001)
            
            f.write(str(fit_norm) + "\t")
        
            print heuristics_params, fit_avg, steps_avg, fit_norm
        f.write("\n")
        f.flush()
    f.close()

base_positions = [(4,300),(8,500),(12,700)]
for uav_count in xrange(3,6):
    for noise_stddev in xrange(1,4):
        for max_steps, distance in base_positions:
            generate_table(uav_count, noise_stddev, distance, max_steps)
