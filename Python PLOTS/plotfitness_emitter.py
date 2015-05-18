#!/usr/bin/python

import argparse
import os
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import pylab as pl
import numpy as np
import matplotlib.ticker as plticker
import time
import random

from matplotlib.patches import *
from mpl_toolkits.mplot3d import Axes3D
from random import randint
from math import cos, sin, sqrt, pi

from nllsCuda import pyPredict, pyQxy, pyMultipleFitness, pyFitnessAlt
from Environment import Environment

def make_receiver(base_position, angle, distance):
    r = (base_position[0]+distance*cos((pi/180.0)*angle),base_position[0]+distance*sin((pi/180.0)*angle))
    return r

def distance(pos1, pos2):
	return sqrt(sum(map(lambda x: (x[0]-x[1])**2, zip(pos1,pos2))))
    
def evaluate_fitness(receiver_set,emitter_positions,noise_stddev, num_trials, grid_size):
    results = []
    total_size = len(emitter_positions)
    
    state = random.getstate()
    for i in xrange(total_size):
        random.setstate(state)
        
        part_results = pyFitnessAlt(receiver_set, emitter_positions[i], num_trials, noise_stddev, [256,256],grid_size)
        results.append(part_results[1])
        
        percent = round(float(i)*100.0 / len(emitter_positions),2)
        print "%s percent complete" % str(percent)
   
    assert len(emitter_positions) == len(results), "Results length doesnt match input %s != %s" % (len(receiver_sets) ,len(results))
    
    return results
from QuickFigure import save_fig
def generate_plot(c, max_fitness, base_receiver_set, step_size, grid_size, filename, saved_fig=False):
    if not saved_fig:
        save_fig("plotfitness_emitter",generate_plot,locals(),filename)
    plt.figure(1,figsize=(8, 8))

    dx, dy = step_size[0], step_size[1]

    y, x = np.mgrid[slice(-dy, grid_size[1] + 2*dy, dy),
                    slice(-dx, grid_size[0] + 2*dx, dx)]
    plt.pcolormesh(x[:-1, :-1]+ dx/2.,y[:-1, :-1]+ dy/2.,c, cmap='GnBu_r', vmin=0, vmax=max_fitness)
    plt.axis([-step_size[0],grid_size[0]+step_size[0],-step_size[1],grid_size[1]+step_size[1]])

    for x,y in base_receiver_set:
        plt.plot(x,y,'o',mfc='b',mec='k',ms=10,label="Receiver",alpha=0.6)

    recv = Circle((0,0),3,facecolor='b',edgecolor='k',alpha=0.8)

    #plt.legend([recv],  ["Receiver"],loc=4)
    #plt.xlabel("X-axis")
    #plt.ylabel("Y-axis")

    #loc = plticker.MultipleLocator(base=100.0)
    #plt.gcf().gca().xaxis.set_major_locator(loc)
    #plt.gcf().gca().yaxis.set_major_locator(loc)
    #plt.colorbar().set_label("Avg. error in prediction")
    
    plt.savefig("%s.png" % filename,dpi=160)

    plt.clf()  
    
def compute(receiver_set,noise_stddev, num_trials, grid_size, step_size):
    emitter_positions = []
    for index_x in xrange(0, grid_size[0]/step_size[0] + 1):
        x = index_x*step_size[0]
    #for x in xrange(0,grid_size[0]+step_size[0],step_size[0]):
        for index_y in xrange(0, grid_size[1]/step_size[1] + 1):
            y = index_y*step_size[1]
        #for y in xrange(0,grid_size[1]+step_size[1],step_size[1]):
            emitter_positions.append((float(x),float(y)))
            
    values = evaluate_fitness(receiver_set,emitter_positions,noise_stddev, num_trials, grid_size)

    pmatrix = []
    max_fitness = max(values)
    num_steps = (grid_size[0]/step_size[0]+1, grid_size[1]/step_size[1]+1)
    for y in xrange(num_steps[1]):
        row = []
        for x in xrange(num_steps[0]):
            index = x*num_steps[1]+y
            row.append(values[index])
            
        pmatrix.append(row)

    npmatrix = np.array(pmatrix)
    
    return max_fitness,npmatrix


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--noise_stddev", nargs=1, metavar="SIGMA", type=float, default=1.5, help="The amount of noise")
    parser.add_argument("--uav_count", metavar="#UAVs", type=int, default=3, help="The number of UAVs")
    parser.add_argument("--uav_radius", metavar="RADIUS", type=int, default=200, help="The radius from base point to each UAV")
    parser.add_argument("--uav_base", nargs=2, metavar="X", type=int, default=None, help="Base point for UAVs")
    parser.add_argument("--num_trials", metavar="#Trials", type=int, default=40, help="The number of runs for each fitness eval.")
    parser.add_argument("--grid_size", nargs=2, metavar="X", type=int, default=[1000,1000],  help="Grid size for the plot")
    parser.add_argument("--step_size", nargs=2, metavar="X", type=int, default=[20,20],help="Step size for the grid of the plot")
    parser.add_argument("--file_prefix", metavar="PREFIX", default="PltFit Emitter", help="File prefix for generated plots")
    return parser

def main(noise_stddev, num_trials, uav_count, uav_radius, uav_base, grid_size, step_size, file_prefix):
    random.seed(1)

    if uav_base is None:
        uav_base = (grid_size[0]/2.0,grid_size[1]/2.0)
        
    base_receiver_set = []#[uav_base]#[]#
        
    angle_step = 360 / uav_count
    
    for i in xrange(uav_count):
        base_receiver_set.append(make_receiver(uav_base,angle_step*i,uav_radius))
        
    max_fitness, results = compute(base_receiver_set,noise_stddev, num_trials, grid_size, step_size)
    
    filename = file_prefix +" Trials %s, Step size %s, Grid size %s Noise %s" % (num_trials, step_size, grid_size, noise_stddev)
    generate_plot(results,max_fitness, base_receiver_set, step_size, grid_size, filename)

if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    assert (args.grid_size[0] / args.step_size[0] ) * args.step_size[0] == args.grid_size[0], "Step size X must be a factor of grid (%s / %s != %s)" % (args.grid_size[0], args.resolution[0], args.grid_size[0] / args.resolution[0])
    assert (args.grid_size[1] / args.step_size[1] ) * args.step_size[1] == args.grid_size[1], "Step size Y must be a factor of grid (%s / %s != %s)" % (args.grid_size[1], args.resolution[1], args.grid_size[1] / args.resolution[1])


    main(args.noise_stddev, args.num_trials, args.uav_count, args.uav_radius,args.uav_base, args.grid_size, args.step_size, args.file_prefix)


