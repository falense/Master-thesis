#!/usr/bin/python

import argparse

from math import *
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from random import *
import os
import pylab as P
import numpy as np
#from cfitness import fitness
from random import randint
from math import cos, sin, pow, sqrt
import pylab as pl

grid = [1000,1000]
grid_size_x, grid_size_y = grid
step_size = 2
num_trials = 50
emitter_position = (330,330)

def evaluate_fitness(receivers,noise_std_dev):
    from nllsCuda import pyMultipleFitness
    vals = pyMultipleFitness(receivers, emitter_position, num_trials,noise_std_dev, step_size, grid)
    return vals

    
    vals = fitness(receivers,(50.0,50.0,0.0),(100.0,100.0,1.0),0,step_size,num_trials,0,0,0,noise_std_dev);
    return vals


n = 5000
receiver_sets = []


positions = [[720, 255],[714, 201],[613, 339],[641, 306],[780, 398],[777, 357],[490, 238],[761, 182],[746, 327],[429, 270],[627, 255],[560, 240],[583, 372],[543, 398],[725, 287],[777, 136]]


for x in xrange(n):
    receiver_sets.append(positions)
fitness_list = evaluate_fitness(receiver_sets,1.0)

def calc_avg_var(values):
    n = len(values)
    total = sum(values)
    avg = total/n
    std_dev = 0.0
    for value in values:
        std_dev += pow(value-avg,2)
    std_dev = sqrt(std_dev/n)
    return avg,std_dev


bias = map(lambda x: x[1], fitness_list)
spread = map(lambda x: x[4], fitness_list)
print fitness_list[:10]

print "Statistics bias"
avg,std_dev = calc_avg_var(bias)
print "Avg.", avg
print "Std. dev.", std_dev

print "Statistics variance"
avg,std_dev = calc_avg_var(spread)
print "Avg.", avg
print "Std. dev.", std_dev
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

plt.figure(1)
plt.scatter(bias, spread)



fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
x = bias
y = spread

hist, xedges, yedges = np.histogram2d(x, y, bins=(20,20))
xpos, ypos = np.meshgrid(xedges[:-1]+xedges[1:], yedges[:-1]+yedges[1:])

xpos = xpos.flatten()/2.
ypos = ypos.flatten()/2.
zpos = np.zeros_like (xpos)

dx = xedges [1] - xedges [0]
dy = yedges [1] - yedges [0]
dz = hist.flatten()

ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color='b', zsort='average')
plt.xlabel ("X")
plt.ylabel ("Y")

plt.show()
