import numpy as np
import collections

from math import *
from nllsCuda import pyPredict, pyQxy
from random import gauss, randint
import random

from Environment import Environment



GPUSTEPS = [256,256]

def calcPredictions(numTrials, samplePositions, env, gridSize):	
    global GPUSTEPS
    samples = []
    for trial in xrange(numTrials):
        t = []
        for i in xrange(len(samplePositions)):
            x,y = samplePositions[i]
            t.append((x,y,env.MeasuredPower(x,y)))
        samples.append(t)
    results = pyPredict(samples,GPUSTEPS,gridSize)

    return results

def simulate(numTrials, gridSize, emitterPosition, noiseStdDev, uavPositions, aiClass, heurParams, maxSteps = None):
    emitterPosition = list(emitterPosition)
    
    numReceivers = len(uavPositions)

    env = Environment(emitterPosition, 10, noiseStdDev)

    uavPositions = uavPositions[:]
    samplePositions = uavPositions[:]

    ai = aiClass(uavPositions,heurParams)
    
    while True: 
        
        results = calcPredictions(numTrials, samplePositions, env, gridSize)
        
        ai.update_state(results)
        for i,uavPosition in enumerate(uavPositions):
            oldPosition = uavPosition
            newPosition = ai.step(i)
            uavPositions[i] = newPosition
            samplePositions.append(oldPosition)
        
        
        
        predictions = results
        sum_x = sum(map(lambda x: x[0],predictions))
        sum_y = sum(map(lambda x: x[1],predictions))
        avg_x = round(sum_x / len(predictions),2)
        avg_y = round(sum_y / len(predictions),2)
        avg = (avg_x,avg_y)
        
        error_avg = round(distance(avg, emitterPosition),5)
        stddev = sum(map(lambda pos: ((pos[0]-avg_x)**2 +  (pos[0]-avg_x)**2), predictions))
        stddev /= len(predictions)
        
        if ((error_avg < 50.0 and stddev < 20.0) or len(samplePositions) > 100) or (maxSteps is not None and len(samplePositions)/len(uavPositions) >= maxSteps):
            return len(samplePositions)/len(uavPositions), samplePositions
    
def make_receiver(base_position, angle, distance):
    r = (base_position[0]+distance*cos(angle),base_position[1]+distance*sin(angle))
    return r
    
def distance(pos1, pos2):
    return sqrt(sum(map(lambda x: (x[0]-x[1])**2, zip(pos1,pos2))))
        

        

