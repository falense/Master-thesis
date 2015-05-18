from RandomAgent import RandomAgent, degToRad


import numpy as np
import collections
from random import uniform
from math import sqrt, cos, sin
from FMM import *

class UAV(object):
    velocity = None
    position = None
    def __init__(self, position):
        self.position = position
        self.velocity = None
        self.attraction_force = None
        
        
    def step(self, attraction_point):
        mass_x,mass_y = attraction_point
        cur_x,cur_y = self.position
        
        d_x = mass_x - cur_x
        d_y = mass_y - cur_y
        
        abs_xy = sqrt(d_x**2+ d_y**2)
        d_x /= abs_xy
        d_y /= abs_xy
        
        
        self.velocity = (1.0-self.attraction_force)*self.velocity + self.attraction_force*np.array([d_x,d_y])
        tot = np.linalg.norm(np.abs(self.velocity))
        self.velocity /= tot
        
        
        #print self.velocity
            
        self.position = 50.0*self.velocity + self.position
        return self.position

def distance(pos1, pos2):
    return sqrt(sum(map(lambda x: (x[0]-x[1])**2, zip(pos1,pos2))))
    
class WhackAgent(RandomAgent):
    mass_point = None
    def __init__(self, initialPositions, parameters):
        super(WhackAgent, self).__init__(initialPositions, UAV)
        self.history = collections.deque(maxlen=1000)
        
        
        for index,(uav,angle) in enumerate(zip(self.uavs,parameters[1:])):
            angle = degToRad(angle)
            uav.velocity = np.array([cos(angle),sin(angle)])
            uav.attraction_force = parameters[0]
            
    def reset_state(self):
        self.mass_point = None
    def get_mass_point(self):
        if self.mass_point is None and len(self.history) > 0:
            x_avg = sum(map(lambda x: x[0],self.history))/len(self.history)
            y_avg = sum(map(lambda x: x[1],self.history))/len(self.history)
            self.mass_point = (x_avg, y_avg)
        return self.mass_point
    def fit_fmm(self):
        if len(self.history) > 0:
            self.components = emFit(self.history, len(self.uavs))
        else:
            self.components = None
    def update_state(self, predictions):
        self.reset_state()
        self.history.extend(predictions)
        self.fit_fmm()
    def select_component(self, uavIndex):
        uav = self.uavs[uavIndex]
        closestIndex = 0
        closestComp = self.components[0]
        for index, comp in enumerate(self.components):
            if distance(comp[0], uav.position) <= distance(closestComp[0],uav.position):
                closestIndex = index
                closestComp = comp
        self.components.pop(closestIndex)
        return closestComp[0]
    def step(self, uavIndex):
        comp = self.select_component(uavIndex)
#        print uavIndex, comp
        return self.uavs[uavIndex].step(comp)
        
