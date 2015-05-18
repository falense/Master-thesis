from random import gauss, seed
 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab



def PlotEmitterPointQxyDistribution():

	sigma = 4
	numTrials = 100000
	numBins = 50
	sampleCount = 3
	
	def QxyEmitter():
		sum = 0.0
		for x in xrange(sampleCount):
			for y in xrange(x,sampleCount):
				t = gauss(0,sigma) - gauss(0,sigma)
				sum += t**2
		return sum
		
	results = []
	for x in xrange(numTrials):
		results.append(QxyEmitter())

	fig = plt.figure()
	ax = fig.add_subplot(111)
	x = np.array(results)
	n, bins, patches = ax.hist(x, numBins, normed=1, alpha=0.75)

	
#PlotEmitterPointQxyDistribution()
from math import log, sqrt
def PlotPointQxyDistribution(samplePositions, emitterPosition, pointPosition, title=""):

    sigma = 4
    numTrials = 10000
    numBins = 200
    sampleCount = len(samplePositions)
    alpha = 2
    def distance(pos1, pos2):
        return  sqrt((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2)
    def QxyEmitter():
        sum = 0.0
        for k in xrange(sampleCount):
            for l in xrange(k,sampleCount):
                t = -10*alpha*log(distance(samplePositions[k],emitterPosition)/distance(samplePositions[l], emitterPosition))
                t += 10*alpha*log(distance(samplePositions[k],pointPosition)/distance(samplePositions[l], pointPosition))
                t += gauss(0,sigma) - gauss(0,sigma)
                sum += t**2
        return sum
        
    results = []
    for x in xrange(numTrials):
        results.append(QxyEmitter())

    fig = plt.figure()
    ax = fig.add_subplot(111)
    x = np.array(results)
    n, bins, patches = ax.hist(x, numBins, range=(0,40000),normed=1, alpha=0.75)

    #plt.title(title)
    plt.xlim([0,40000])
    plt.ylim([0,0.002])
    plt.xlabel("Qxy",fontsize=24)
    plt.ylabel("Probability",fontsize=20)
    plt.savefig((title + ".png").replace(" ","_"))
    
import random
from math import exp, log10
def PlotPointCorrelationQxyDistribution(samplePositions, emitterPosition, pointPosition1, pointPosition2, title):

    sigma = 4
    numTrials = 10000
    numBins = 50
    sampleCount = len(samplePositions)
    alpha = 2
    def distance(pos1, pos2):
        return  sqrt((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2)
    def QxyEmitter(pointPosition):
        sum = 0.0
        for k in xrange(sampleCount):
            for l in xrange(k,sampleCount):
                t = -10*alpha*log(distance(samplePositions[k],emitterPosition)/distance(samplePositions[l], emitterPosition))
                t += 10*alpha*log(distance(samplePositions[k],pointPosition)/distance(samplePositions[l], pointPosition))
                t += gauss(0,sigma) - gauss(0,sigma)
                sum += t**2
        return sum
        
    x = []
    y = []

    for i in xrange(numTrials):
        state = random.getstate()
        
        x.append(QxyEmitter(pointPosition1))
        random.setstate(state)
        y.append(QxyEmitter(pointPosition2))
    weights = map(lambda x: (1-exp(-max(0,-log(0.5)-20*log10(x[0]/x[1])))),zip(x,y))
    #print weights
    colors = map(lambda x: tuple(np.array((0.5,0,0)) * x + np.array((0,0.5,0))*  (1-x)), weights)
    #print colors
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(x,y, c = colors)


    #plt.title(title)
    plt.xlabel("Qxy - Wrong position",fontsize=24)
    plt.ylabel("Qxy - Emitter position",fontsize=28)
    plt.savefig((title + ".png").replace(" ","_"))


seed(1)
samplePositionsGood = ((1338.0, 1058.0),(1720.0, 986.0), (1406.0, 1410.0), (1140.0, 932.0), (1476.0, 820.0), (1148.0, 1230.0), (1724.0, 1310.0))
samplePositionsBad = ((1406.0, 1412.0), (1720.0, 986.0), (1406.0, 1410.0), (1140.0, 932.0), (1476.0, 820.0), (1148.0, 1230.0), (1724.0, 1310.0))

PlotPointQxyDistribution(samplePositionsBad,(500,500),(1333.0, 1053.0), "Ambiguous - Wrong position" )
PlotPointQxyDistribution(samplePositionsBad,(500,500),(500,500), "Ambiguous - Emitter position" )

PlotPointCorrelationQxyDistribution(samplePositionsBad,(500,500),(1333.0, 1053.0),(500,500), "Correlation Ambiguous")

PlotPointQxyDistribution(samplePositionsGood,(500,500),(1333.0, 1053.0), "Non-ambiguous - Wrong position" )
PlotPointQxyDistribution(samplePositionsGood,(500,500),(500,500), "Non-ambiguous - Emitter position" )

PlotPointCorrelationQxyDistribution(samplePositionsGood,(500,500),(1333.0, 1053.0),(500,500), "Correlation Non-ambiguous")




#plt.show()
