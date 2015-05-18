
import matplotlib.pyplot as plt
import numpy as np
import json
import collections

from math import *
from nllsCuda import pyPredict, pyQxy
from random import gauss, randint, seed
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from time import sleep

from simulator.Environment import Environment
from simulator.AttractionAgent import *
from simulator.WhackAgent import *
from simulator.RandomAgent import *
from simulator.FMM import *
from simulator.GUI import GUI, distance


#Use cases: 
    #Testing result formations
        #Statistics
    #Playing around (selected samples move around)
        #Disable AI
    #Heuristics testing 
        #Optional GUI
        #Disable interactivity

class Receiver(object):
    def __init__(self,pos):
        assert(len(pos) == 2)
        self.pos = pos


GPUSTEPS = [256,256]
NUMTRIALS = 10
BUFFERMULTIPLIER = 50#1000/NUMTRIALS

def simulate(samplePositions, env, gridSize):	
    global NUMTRIALS, GPUSTEPS
    samples = []
    for trial in xrange(NUMTRIALS):
        t = []
        for i in xrange(len(samplePositions)):
            x,y = samplePositions[i]
            t.append((x,y,env.MeasuredPower(x,y)))
        samples.append(t)
    results = pyPredict(samples,GPUSTEPS,gridSize)

    return results

def run(gridSize, emitterPosition, noiseStdDev, uavPositions, ai, title):
    aiEnabled = ai is not None
    guiEnabled = True
    emitterPosition = list(emitterPosition)
    
    numReceivers = len(uavPositions)
    receivers = []

    env = Environment(emitterPosition, 10, noiseStdDev)

    if guiEnabled:
        g = GUI(gridSize, GPUSTEPS, env, title, interactive=not aiEnabled )

    components = None

    predictionHistory = collections.deque(maxlen=NUMTRIALS*BUFFERMULTIPLIER)

    uavPositions = uavPositions[:]
    samplePositions = uavPositions[:]

    
    while True: 
        
        results = simulate(samplePositions, env, gridSize)
        #components = emFit(results, 3)
        
        if aiEnabled:
            ai.update_state(results)
            for i,uavPosition in enumerate(uavPositions):
                oldPosition = uavPosition
                newPosition = ai.step(i)
                uavPositions[i] = newPosition
                samplePositions.append(oldPosition)
        else:
            samplePositions = uavPositions
        
        predictionHistory.extend(results)
        
        
        predictions = results
        num_predictions = len(predictions)
        if num_predictions == 0:
            return
        sum_x = sum(map(lambda x: x[0],predictions))
        sum_y = sum(map(lambda x: x[1],predictions))
        avg_x = round(sum_x / num_predictions,2)
        avg_y = round(sum_y / num_predictions,2)
        avg = (avg_x,avg_y)
        
        error_avg = round(distance(avg, emitterPosition),5)
        stddev = sum(map(lambda pos: ((pos[0]-avg_x)**2 +  (pos[0]-avg_x)**2), predictions))
        stddev /= num_predictions
        stddev = round(sqrt(stddev),5)
        #from time import sleep
        #sleep(1)
        
        if guiEnabled:
            g.update(emitterPosition, uavPositions, samplePositions, results, predictionHistory, components)
    
        if aiEnabled and ((error_avg < 50.0 and stddev < 20.0) or len(samplePositions) > 50):
            return len(samplePositions)/len(uavPositions)
    
    if guiEnabled:
        g.close()
def make_receiver(base_position, angle, distance):
    r = (base_position[0]+distance*cos(angle),base_position[1]+distance*sin(angle))
    return r

def degToRad(deg):
    return deg/360.0 * 3.14*2.0
    
def radToDeg(rad):
    return rad/3.14 * 180.0
def ai_mode():
    agents = [AttractionAgent, WhackAgent]#, RandomAgent]
    gridSize = (1000,1000)
    emitterPosition = (330,330)
    noiseStdDev = 1.0
    numReceivers = 3
    
    #from simulator.AttractionAgent import opt_angles 
    
    print "MAX, MIN, AVG, STDDEV, MEDIAN"
    f = open("log.txt","w")
    for agent in agents:
        results = []
        for s in xrange(100):
            seed(s)
            
                    
            offset = 0
            #heurParams =  [0.35, 225+60+offset,225-60+offset,45+offset]#, 215+90+60] 
            heurParams =  [0.35, 225, 225+90,225-90,45]
            #heurParams =  [0.5, 45+72*2, 45-72*2, 45+72,45-72,45]
            base_position = [670,670]
            
            uavPositions = []
            
            for i, angle in enumerate(heurParams[1:]):
                rads = degToRad(angle)
                uavPositions.append(make_receiver(base_position,rads,50))
            
            if agent == RandomAgent:
                ai = agent(uavPositions)
            else:
                ai = agent(uavPositions, heurParams)
            
            samplesUsed = run(gridSize, emitterPosition, noiseStdDev, uavPositions, ai, "AI Mode %s %s" % (agent.__name__,0))
            #print s, samplesUsed
            #print samplesUsed
            results.append(float(samplesUsed))
        print
        results = np.array(results)
        avg = (results.sum()/len(results))
        stddev = sum(map(lambda v: v**2, results-avg))
        stddev /= len(results)
        stddev = sqrt(stddev)
        rmax = results.max()
        rmin = results.min()
        
        results = sorted(results)
        median = results[len(results)/2]
        output = (agent.__name__, rmax, rmin, avg, stddev, median)
        f.write(json.dumps(output) + "\n")
        f.flush()
        
        print output
    f.close()
def interactive_mode():
    gridSize = (1000,1000)
    emitterPosition = (330,670)
    noiseStdDev = 1.0
    
    
    numReceivers = 4
    receiverPositions = []
    
    for i in xrange(numReceivers):
        
        angle = 2.0*pi/float(numReceivers) * i
        receiverPositions.append(make_receiver((670,330),angle, 20))
    run(gridSize, emitterPosition, noiseStdDev, receiverPositions, None, "Interactive mode")

def demo_ai():
    
    agents = [AttractionAgent, WhackAgent, RandomAgent]
    gridSize = (1000,1000)
    emitterPosition = (330,330)
    base_position = [670,670]
    noiseStdDev = 1.0
    
    param_sets = []
    param_sets.append( [0.3, 215])
    param_sets.append( [0.3, 215-30, 215+30])
    param_sets.append( [0.3, 215, 215 + 45, 215 - 45])
    
    
    
    for agent in agents:
        results = []
        for uav_count in xrange(1,4):
            for s in xrange(5):
                seed(s+1)
                        
                heurParams =  param_sets[uav_count-1]
                
                
                num_receivers = len(heurParams)-1
                uavPositions = []
                angle_step = 360 / num_receivers
                for i in xrange(num_receivers):
                    rads = degToRad(45+180+i*angle_step)
                    uavPositions.append(make_receiver(base_position,rads,50))
                
                if agent == RandomAgent:
                    ai = agent(uavPositions)
                else:
                    ai = agent(uavPositions, heurParams)
                
                samplesUsed = run(gridSize, emitterPosition, noiseStdDev, uavPositions, ai, agent.__name__)
                
def formation_test_mode():
    gridSize = (1000,1000)
    emitterPosition = (gridSize[0]/2,gridSize[1]-gridSize[1]/2)
    noiseStdDev = 1.0
    
    data = json.loads('{"MAX_DEV": 410.53964224123655, "AVG_DEV": 142.01262515669967, "decoded_positions": [[695.6764198508154, 627.0963700411648], [718.470395826294, 582.594295266731], [699.5684890557019, 536.3047940765492], [746.1822890862004, 518.2174049140223], [689.1709295717617, 716.1787338431291], [699.7963871679951, 667.3207800293369], [741.7899497530325, 640.1814966670859], [766.1665259364495, 596.5262274138323], [621.6598848392962, 657.2237225198461], [599.4882867244859, 612.4083207361363], [639.5048071103122, 582.4303605618559], [665.5184689806853, 539.7303676333565], [683.1638638863283, 718.2360102784447], [697.4624577775357, 766.147910811969], [741.2544359859374, 742.017791777972], [791.1826570398982, 744.6959893783802]], "MIN_DEV": 11.495795766822756, "genome": [[670, 670, 301.0517620443709, -3.779519335229253, 310.82382299885194, 91.0507997215411], [670, 670, 67.48861433434901, 214.92399244072638, 44.8798431645804, 332.2203594594865], [670, 670, 194.9035364431753, 48.897000304119, 79.52504110175248, 338.36045027461114], [670, 670, 74.77329341712505, 358.8295736103076, 257.89218551014505, 31.942157116536315]], "FITNESS": 0.6047861738791979, "VAR_DEV": 11572.752430868337}')
    receiverPositions = data['decoded_positions']
    run(gridSize, emitterPosition, noiseStdDev, receiverPositions)

if __name__=="__main__":
    ai_mode()
    #interactive_mode()
    #demo_ai()
    exit(1)
