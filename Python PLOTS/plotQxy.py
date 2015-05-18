#!/usr/bin/python

import argparse
import os
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import pylab as pl
import numpy as np
import matplotlib.ticker as plticker

from matplotlib.patches import *
from mpl_toolkits.mplot3d import Axes3D
from random import randint, seed
from math import cos, sin, sqrt, pi

from nllsCuda import pyPredict, pyQxy, pyMultipleFitness, pyFitnessAlt
from Environment import Environment
        
def make_receiver(base_position, angle, distance):
    r = [base_position[0]+distance*cos((pi/180.0)*angle),base_position[0]+distance*sin((pi/180.0)*angle)]
    return r

def distance(pos1, pos2):
	return sqrt(sum(map(lambda x: (x[0]-x[1])**2, zip(pos1,pos2))))
    

def compute(sample_positions, emitter_position, grid_size, step_size, resolution, base_position):

    env = Environment(emitter_position, 10.0, 0.5)

    
    samples = []
    for x,y in sample_positions:
        
        t = (x,y,env.MeasuredPower(x,y))
        samples.append(t)
    
    return pyQxy(samples, resolution, grid_size)
    
def generate_plot(c, step_size, grid_size, emitter_position, sample_positions, filename):
    c = np.log10(c)
    print c[0,0], c[512,512]
    
    plt.figure(1)

    dx, dy = step_size

    y, x = np.mgrid[slice(-dy, grid_size[1] + dy, dy),
                    slice(-dx, grid_size[0] + dx, dx)]

    plt.pcolormesh(x[:-1, :-1]+ dx/2.,y[:-1, :-1]+ dy/2.,c, cmap='GnBu_r', vmin=-1.1, vmax=3.5)
    plt.axis([-step_size[0],grid_size[0]+step_size[0],-step_size[1],grid_size[1]+step_size[1]])
   
    plt.plot(emitter_position[0],emitter_position[1],'d',mfc='r',mec='k',ms=14,label="Emitter",alpha=0.6)
	
   
    for x,y in sample_positions:
        plt.plot(x,y,'o',mfc='b',mec='k',ms=10,label="Receiver",alpha=0.6)

    em = RegularPolygon((0,0), 4, 3, 3.14/2.0,facecolor='r',edgecolor='k',alpha=0.8)
    recv = Circle((0,0),3,facecolor='b',edgecolor='k',alpha=0.8)

    plt.legend([em,recv],  ["Emitter", "Receiver"],loc=4)
    
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")

    loc = plticker.MultipleLocator(base=grid_size[0]/10.0)
    plt.gcf().gca().xaxis.set_major_locator(loc)
    plt.gcf().gca().yaxis.set_major_locator(loc)
    plt.colorbar().set_label("Log(Qxy) (Error, lower is better)")


    plt.savefig("%s.png" % filename)

    plt.clf()  

def main(final_receiver, filename):
    
    resolution = [1024,1024]
    grid_size = [100.0,100.0]
    step_size = grid_size[0]/resolution[0], grid_size[1]/resolution[1]
    emitter_position = [grid_size[0]/2,grid_size[1]/2]
    base_position = [grid_size[0]/2,grid_size[1]/2]
    max_radius = min(grid_size)/2.0
    
    sample_positions = []
    sample_positions.append(final_receiver)
    
    t = [85.0,70.0]#make_receiver(base_position, 30, 0.85*max_radius)
    sample_positions.append(t)
    t = [85.0,30.0]#make_receiver(base_position, -30, 0.85*max_radius)
    sample_positions.append(t)

    Qxy = compute(sample_positions, emitter_position, grid_size, step_size, resolution, base_position)
    generate_plot(Qxy, step_size, grid_size, emitter_position, sample_positions, filename)
   


if __name__ == '__main__':
    s = 3
    seed(s)
    main([35,50], "trianglebad")
    seed(s)
    main([25,50], "trianglegood")
    s = 4
    seed(s)
    main([84,50], "linegood")
    seed(s)
    main([87,50], "linebad")
