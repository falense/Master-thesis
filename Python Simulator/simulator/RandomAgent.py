
from random import randint
from math import cos, sin, pi

def degToRad(deg):
    return float(deg)/180.0 * pi
class BasicUAV(object):
    position = None
    def __init__(self, position):
        self.position = position
    def step(self):
        angle = randint(0,360)
        
        x = self.position[0] + cos(degToRad(angle))*50
        y = self.position[1] + sin(degToRad(angle))*50
        self.position = (x,y)
        return x,y
            

class RandomAgent(object):
    history = None
    uavs = None
    def __init__(self, initialPositions, uavClass = None):
        self.history = []
        self.uavs = []
        if uavClass is None:
            uavClass = BasicUAV
        for i,position in enumerate(initialPositions):
            self.uavs.append(uavClass(position))
            
            
        
        
    def update_state(self, predictions):
        self.reset_state()
        self.history = predictions
    def reset_state(self):
        pass
        
    def step(self, uavIndex):
        return self.uavs[uavIndex].step()
            
