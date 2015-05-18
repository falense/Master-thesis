
import pygame
import numpy as np

from pygame_shortcuts import *
from FMM import drawComponents
from math import sqrt

def distance(pos1, pos2):
    return sqrt(sum(map(lambda x: (x[0]-x[1])**2, zip(pos1,pos2))))
    

class GUI(object):
    def __init__(self, gridSize, gpuSteps, env, title, interactive=True):
        self.windowSize = (1000,1000)
        self.scaleFactor = map(lambda x: float(x[1])/x[0], zip(gridSize, self.windowSize))
        self.gridSize = gridSize
        self.gpuSteps = gpuSteps
        self.env = env
        self.title = title
    
        pygame.init() 
        
        self.paused = False
        self.interactive = interactive
        self.draw_emitter = True
        self.iteration = 0
        self.drag = -3
        self.dragOffsets = None
        self.uav_distance = 0.0
        self.window = pygame.display.set_mode(self.windowSize) 


    
    def __drawStatistics(self, emitterPosition, predictions):

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
        
        space = 70
        drawInfolabel(self.window, (10,920), space, "Avg:", "(%s,%s)" % avg)
        drawInfolabel(self.window, (10,945), space, "Error:", error_avg)
        drawInfolabel(self.window, (10,970), space, "Stddev:", stddev)
        
    def __drawTitle(self):
        font = pygame.font.Font(None,48)
        text = font.render(self.title, 1, (10, 10, 10))
        self.window.blit(text, (self.windowSize[0]/2.0 - 120 ,20))   
        

    def __drawHistogram(self, predictionHistory):
        x = map(lambda x: x[0],predictionHistory)
        y = map(lambda x: x[1],predictionHistory)
        
        hist, xedges, yedges = np.histogram2d(x, y, range=[[0,self.gridSize[0]],[0,self.gridSize[1]]], bins=self.gpuSteps)
        xpos, ypos = np.meshgrid(xedges[:-1]+xedges[1:], yedges[:-1]+yedges[1:])
        xpos = xpos.flatten()/2.
        ypos = ypos.flatten()/2.
        hist = hist.transpose()
        zpos = hist.flatten()
        
        max_z = zpos.max()*0.8
        
        indexes = np.where(zpos > 0)[0]
        
        
        triplets = map(lambda i: (xpos[i],ypos[i],zpos[i]), indexes)
        
        
        for x,y,z in triplets:
            p = min(1.0,z / max_z) 
            color = (int(200*(1-p)),int(200*(1-p)),200  )
            pygame.draw.circle(self.window, color, map(lambda x: int(x[0]*x[1]), zip((x,y),self.scaleFactor)),  2)

    def __drawPredictions(self, predictions):
        for prediction in predictions:
            position = map(lambda x: int(x[0]*x[1]), zip(prediction,self.scaleFactor))
            pygame.draw.circle(self.window, (0, 0,0),position ,  2)
            
    def __drawUAVs(self, uavPositions):
        for receiver in uavPositions:
            position = map(lambda x: int(x[0]*x[1]), zip(receiver,self.scaleFactor))

            drawGradientCircle(self.window, (0, 50, 255), position,  5, inverted=True, layers=6)
            
            font = pygame.font.Font(None,20)
            text = font.render(str(round(self.env.MeasuredPower(receiver[0],receiver[1]),2)), 1, (10, 10, 10))
            self.window.blit(text, position)
    
    def __drawSamples(self, samplePositions):
        for receiver in samplePositions:
            position = map(lambda x: int(x[0]*x[1]), zip(receiver,self.scaleFactor))

            drawGradientCircle(self.window, (0, 10, 50), position,  5, inverted=True, layers=6)
    
    def __drawEmitter(self, emitterPosition):
        drawGradientCircle(self.window, (255, 50, 50), map(lambda x: int(x[0]*x[1]), zip(emitterPosition,self.scaleFactor)),  8, inverted=True)

    def update(self, emitterPosition, uavPositions, samplePositions, predictions, predictionHistory, components):
        firstRun = True
        
        while self.paused or firstRun:
            
            self.window.fill((255,255,255))	
            
            if components is not None:
                self.__drawComponents(components)
            
            self.__drawHistogram(predictionHistory)
            
            self.__drawPredictions(predictions)

            self.__drawUAVs(uavPositions)
            
            self.__drawSamples(samplePositions)
            
            if self.draw_emitter:    
                self.__drawEmitter(emitterPosition)
            
            self.__drawStatistics(emitterPosition,predictions)
            
            self.__drawTitle()
            
            
            wSpace = 160
            drawInfolabel(self.window, (10,10), wSpace, "Iteration:", self.iteration)
            drawInfolabel(self.window, (10,30), wSpace, "Samples:", len(samplePositions))
            drawInfolabel(self.window, (10,50), wSpace, "Distance traversed:", round(self.uav_distance,2))
            
            pygame.display.flip()
            
            for event in pygame.event.get(): 
                if event.type == pygame.QUIT: 
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN and  event.unicode == u'p':
                    self.paused = not self.paused
                elif event.type == pygame.KEYDOWN and  event.unicode == u'e':
                    self.draw_emitter = not self.draw_emitter
                elif not self.interactive:
                    continue
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        X,Y = event.pos
                        X /= self.scaleFactor[0]
                        Y /= self.scaleFactor[1]
                        closest = emitterPosition
                        closestIndex = -1
                        for receiverIndex,uavPosition in enumerate(uavPositions):
                            if distance(closest,(X,Y)) > distance(uavPosition,(X,Y)):
                                closest = uavPosition 
                                closestIndex = receiverIndex
                        self.drag = closestIndex
                        print "Moving one, index:", self.drag
                    elif event.button == 3:
                        X,Y = event.pos
                        X /= self.scaleFactor[0]
                        Y /= self.scaleFactor[1]
                        self.drag = -2
                        self.dragOffsets = []
                        for uavX, uavY in uavPositions:
                            dragOffsetX = uavX - X
                            dragOffsetY = uavY - Y
                            self.dragOffsets.append((dragOffsetX,dragOffsetY))
                        
                        print "Moving all"
                        
                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.drag == -2:
                        self.dragOffsets = None
                    self.drag = -3
                elif event.type == pygame.MOUSEMOTION:
                    if self.drag > -3:
                        if self.drag == -1:
                            X,Y = event.pos
                            emitterPosition[:] = X/self.scaleFactor[0],Y/self.scaleFactor[1]
                            self.env.setEmitterPos(emitterPosition)
                        elif self.drag == -2:
                            X,Y = event.pos
                            X = X/self.scaleFactor[0]
                            Y = Y/self.scaleFactor[1]
                            for uavIndex, uavPosition in enumerate(uavPositions):
                                uavX = X + self.dragOffsets[uavIndex][0]
                                uavY = Y + self.dragOffsets[uavIndex][1]
                                
                                newPos = (uavX,uavY)
                                self.uav_distance += distance(uavPositions[uavIndex],newPos)
                                uavPositions[uavIndex] = newPos
                        
                        else:
                            X,Y = event.pos
                            
                            newPos = (X/self.scaleFactor[0],Y/self.scaleFactor[1])
                            self.uav_distance += distance(uavPositions[self.drag],newPos)
                            uavPositions[self.drag] = newPos
                
            if not self.paused:
                self.iteration += 1
            firstRun = False
    
    def __drawComponents(self, components):
        drawComponents(self.window, self.windowSize, self.scaleFactor, components)
    def close(self):
        pygame.quit()
