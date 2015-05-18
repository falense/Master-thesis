from BasicAgent import BasicAgent

import numpy as np
from random import uniform
from math import sqrt, cos, sin

def degToRad(deg):
    return deg/360.0 * 3.14*2.0
    
def radToDeg(rad):
    return rad/3.14 * 180.0
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


class AttractionAgent(BasicAgent):
    mass_point = None
    def __init__(self, initialPositions, parameters):
        super(AttractionAgent, self).__init__(initialPositions, UAV)
        
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
    def step(self, uavIndex):
        return self.uavs[uavIndex].step(self.get_mass_point())
        
