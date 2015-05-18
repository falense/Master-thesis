#!/usr/bin/python

import argparse, os, time, random
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import pylab as pl
import numpy as np
import matplotlib.ticker as plticker
import matplotlib.colors as colors
import matplotlib.cm as cmx

from matplotlib.patches import *
from matplotlib.patches import  Arrow
from mpl_toolkits.mplot3d import Axes3D
from random import randint
from math import cos, sin, sqrt, pi

from nllsCuda import pyPredict, pyQxy, pyMultipleFitness, pyFitnessAlt
from Environment import Environment
from QuickFigure import save_fig

PI = 3.14

def distance(pos1, pos2):
	return sqrt(sum(map(lambda x: (x[0]-x[1])**2, zip(pos1,pos2))))
    
def degToRad(deg):
	return deg/360.0 * 3.14*2.0
    
def radToDeg(rad):
	return rad/3.14 * 180.0
    
def make_path(base_position, angle, step_length, num_steps):
    positions = []
    x,y = base_position
    for step in xrange(num_steps):
        x += cos(degToRad(angle))*50
        y += sin(degToRad(angle))*50
        positions.append((x,y))
    
    return positions
    


def evaluate_fitness(receiver_sets,emitter_position,noise_stddev, num_trials, grid_size):
    results = []
    total_size = len(receiver_sets)
    for i, receiver_set in enumerate(receiver_sets):    
        random.seed(1)

        
        part_results = pyFitnessAlt(receiver_set, emitter_position, num_trials, noise_stddev, [256,256],grid_size)
        
        fit, avg, _, _, var = part_results
        fit =  100.0/(1.0+fit*0.0001)
        results.append((fit,avg,var))
        
        
        percent = round(float(i)*100.0 / len(receiver_sets),2)
        print "%s percent complete" % str(percent)
   
    assert len(receiver_sets) == len(results), "Results length doesnt match input %s != %s" % (len(receiver_sets) ,len(results))
    
    return results



def generate_plot_graph(c, base_receiver_set, step_size, filename, saved_fig = False):
    if not saved_fig:
        save_fig("plotfitness_direction",generate_plot_graph,locals(),"%s - 1" % filename)
    
    labels = ["FIT"]#,"AVG","VAR"]
    
    for index, label in enumerate(labels):
        plt.figure(1,figsize=(8, 8))
        plt.grid(b=True)
        y = map(lambda v: v[index],c)
        
        plt.plot(np.arange(0,361,step_size),y)
        
        plt.xlim(0,360)
        plt.xticks(np.arange(0,361, 30.0))
        
        plt.xlabel("Angle")
        plt.ylabel(label)
        
        plt.savefig("%s %s - 1.png" % (filename, label))
        plt.clf()  
        plt.close()

def generate_plot_radials(c, base_receiver_set, step_angle, arrow_length, filename, saved_fig = False):
    if not saved_fig:
        save_fig("plotfitness_direction",generate_plot_radials,locals(),"%s - 2" % filename)
    
    labels = ["FIT"]#,"AVG","VAR"]
    
    for index, label in enumerate(labels):
        plt.figure(1,figsize=(8, 8))
        y = map(lambda v: v[index],c)
        
        plt.xlim([0,1000])
        plt.ylim([0,1000])
        plt.grid(b=True)
        plt.gca().set_aspect('equal')
        
        
        #Make legend
        angles = [(0,55),(90,60),(180,100),(270,80),(45,50),(225,90)]
        for angle, dist in angles:
            sx, sy = 200.0, 850.0
            dx, dy = cos(degToRad(angle))*50,sin(degToRad(angle))*50
            
            arr = Arrow(sx,sy,dx,dy,width=6.0, color="k")
            plt.gcf().gca().add_artist(arr)
            
            
            dx, dy = cos(degToRad(angle))*dist,sin(degToRad(angle))*dist
            ex, ey = sx+dx, sy+dy
            plt.text(ex,ey, angle, style='italic')
        
        if label == "FIT":
            cmap = plt.cm.GnBu
        else:
            cmap = plt.cm.GnBu_r
            
        cNorm  = colors.Normalize(vmin=np.min(y), vmax=np.max(y))

        scalarMap = cmx.ScalarMappable(norm=cNorm,cmap=cmap)
        for index, value in enumerate(y):
            print arrow_length
            colorVal = scalarMap.to_rgba(value)
            angle = index*step_angle
            
            arr = Arrow(670.0,670.0,cos(degToRad(angle))*arrow_length,sin(degToRad(angle))*arrow_length,width=6.0,  color=colorVal)
            plt.gcf().gca().add_artist(arr)
        
        art = Circle((670.0,670.0),5,facecolor=(0.0,1.0,0.5),edgecolor='k',alpha=0.6)
        plt.gcf().gca().add_artist(art)
        
        for x,y in base_receiver_set:
            art = Circle((x,y),5,facecolor='b',edgecolor='k',alpha=0.6)
            plt.gcf().gca().add_artist(art)
            
        art = RegularPolygon((330.0,330.0), 4, 8, 3.14/2.0,facecolor='r',edgecolor='k',alpha=0.8)
        plt.gcf().gca().add_artist(art)
        
        em = RegularPolygon((0,0), 4, 3, 3.14/2.0,facecolor='r',edgecolor='k',alpha=0.8)
        recv = Circle((0,0),3,facecolor='b',edgecolor='k',alpha=0.8)

        plt.legend([em,recv],  ["Emitter", "Receiver"],loc=4)
        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")

        loc = plticker.MultipleLocator(base=100.0)
        plt.gcf().gca().xaxis.set_major_locator(loc)
        plt.gcf().gca().yaxis.set_major_locator(loc)
            
        plt.savefig("%s %s - 2.png" % (filename, label))
        plt.clf()  
        plt.close()
        
#load_fig("generate_plot_radials.fig")
#exit(1)
def generate_plot_2d(c, base_receiver_set, step_angle_spread, max_angle_spread, step_angle, filename, saved_fig = False):
    if not saved_fig:
        save_fig("plotfitness_direction",generate_plot_2d,locals(),filename)
   
    plt.figure(1)

    dx, dy = step_angle,step_angle_spread
    y, x = np.mgrid[slice(-dy, max_angle_spread+dy , dy),slice(-dx, 360 +dx , dx)]

    plt.pcolormesh(x[:-1, :-1]+ dx/2.,y[:-1, :-1]+ dy/2., c, cmap='GnBu', vmin=0, vmax=np.max(c))
    plt.axis([-dx,360.0+dx,-dy,max_angle_spread])


    plt.ylabel("Angle spread")
    plt.xlabel("Last UAV angle")
    plt.colorbar().set_label("Fitness")
    
    
    loc = plticker.MultipleLocator(base=30.0)
    plt.gcf().gca().xaxis.set_major_locator(loc)
    #loc = plticker.MultipleLocator(base=20.0)
    #plt.gcf().gca().yaxis.set_major_locator(loc)
        
    
    plt.savefig("%s.png" % filename)
    plt.clf()  
    plt.close()
    
def compute(base_receiver_set, uav_base, emitter_position,noise_stddev, num_trials, grid_size, step_length, num_steps, step_angle):
    receiver_sets = []
    for angle in xrange(0,360+1,step_angle):
        receiver_set = base_receiver_set[:]
        receiver_set.extend(make_path(uav_base,angle,step_length,num_steps))
        receiver_sets.append(receiver_set)
    values = evaluate_fitness(receiver_sets,emitter_position,noise_stddev, num_trials, grid_size)
    return values
    

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--noise_stddev", nargs=1, metavar="SIGMA", type=float, default=1.0, help="The amount of noise")
    
    parser.add_argument("--num_uavs", metavar="#UAVs", type=int, default=3, help="The number of UAVs")
    parser.add_argument("--uav_base", nargs=2, metavar="X", type=int, default=None, help="Base point for UAVs")
    parser.add_argument("--num_trials", metavar="#Trials", type=int, default=100, help="The number of runs for each fitness eval.")
    parser.add_argument("--num_steps", metavar="#Steps", type=int, default=5, help="The number of steps per UAV")
    parser.add_argument("--step_length", nargs=2, metavar="X", type=int, default=50,help="Step size for the grid of the plot")
    
    parser.add_argument("--step_angle", metavar="THETA", type=float, default=1, help="The step of the angle for the last UAV")
    
    parser.add_argument("--step_angle_spread", metavar="THETA", type=float, default=2, help="The step in angle spread between each UAV path")
    parser.add_argument("--max_angle_spread", metavar="THETA", type=float, default=None, help="The maximal angle spread between each UAV path")
    
    parser.add_argument("--file_prefix", metavar="PREFIX", default="PltFit Direction", help="File prefix for generated plots")
    return parser



def main(noise_stddev, uav_base, num_uavs, num_trials,  num_steps, step_length, step_angle, step_angle_spread, max_angle_spread, file_prefix):

    if uav_base is None:
        uav_base = (670.0,670.0)
        
    emitter_position =  (330.0,330.0)
    grid_size = (1000.0,1000.0)
    
    #num_trials = 10
    #step_angle = 1
    #step_angle_spread = 1
    
    #num_uavs = 6
    
    assert 360 / step_angle * step_angle == 360, "Step angle must evenly divide 360"
    
    if max_angle_spread is None:
        max_angle_spread = 360 / (num_uavs - 1)
    
    assert max_angle_spread / step_angle_spread * step_angle_spread == max_angle_spread, "Step angle spread should evenly divide max step angle"

    results = []
    
    offset = 20
    if offset != 0:
        print "Warning using a non zero offset"
    
    for angle_spread in xrange(0,max_angle_spread+1,step_angle_spread):
        angles = []
        
        if (num_uavs-1) % 2 == 0:
            if (num_uavs-1) >= 2:
                angles.append(45+180+offset+angle_spread/2.0)
                angles.append(45+180+offset-angle_spread/2.0)
                
            if (num_uavs-1) >= 4:
                angles.append(45+180+offset-angle_spread*1.5)
                angles.append(45+180+offset+angle_spread*1.5)
        else:
            if (num_uavs-1) >= 1: 
                angles.append(45+180+offset)
            
            if (num_uavs-1) >= 3:
                angles.append(45+180+offset-angle_spread)
                angles.append(45+180+offset+angle_spread)
            
            if (num_uavs-1) >= 5:
                angles.append(45+180+offset-angle_spread*2.0)
                angles.append(45+180+offset+angle_spread*2.0)
            
        
        
        base_receiver_set = []
        
        for angle in angles:
            base_receiver_set.extend(make_path(uav_base,angle, step_length, num_steps))
        
        part_results = compute(base_receiver_set, uav_base, emitter_position, noise_stddev, num_trials, grid_size, step_length, num_steps, step_angle)
        
        filename = file_prefix +" UAVs %s, Samples %s, Trials %s, Step angle %s, Angle spread %s,  Noise %s" % (len(angles)+1, num_steps, num_trials, step_angle, angle_spread, noise_stddev)
        #def generate_plot_radials(c, base_receiver_set, step_angle, arrow_length, filename, saved_fig = False):
        generate_plot_radials(part_results, base_receiver_set, step_angle, num_steps*step_length, filename)
        generate_plot_graph(part_results, base_receiver_set, step_angle, filename)
        
        part_results = map(lambda v: v[0],part_results)
        results.append(part_results)
    results = np.array(results)
    filename = file_prefix +" UAVs %s, Samples %s, Trials %s, Step angle %s, Angle spread %s-%s,  Noise %s" % (len(angles)+1, num_steps, num_trials, step_angle, 0,max_angle_spread, noise_stddev)
    generate_plot_2d(results, base_receiver_set, step_angle_spread, max_angle_spread, step_angle, filename)
        
    
if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    main(args.noise_stddev, args.uav_base, args.num_uavs, args.num_trials, args.num_steps, args.step_length, args.step_angle, args.step_angle_spread, args.max_angle_spread, args.file_prefix)

