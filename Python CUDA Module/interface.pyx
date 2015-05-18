cimport numpy as np
import numpy as np
import cython
from math import sqrt, log
from random import gauss
import random



cdef extern from "GAInterface.h": 
    void predict(float * result, int algorithm,  float *samples,unsigned int * numSteps,float * gridMax,unsigned int numSamples,unsigned int numSets)
    void Qxy(float * resultGridFromDevice, float *samples, unsigned int * numSteps, float * gridMax, unsigned int numSamples)
    
def py2cQxy(samples, numSteps, gridMax, numSamples):
    cdef np.ndarray[np.float32_t, ndim=1, mode="c"] cSamples
    cdef np.ndarray[np.uint32_t, ndim=1, mode="c"] cNumSteps
    cdef np.ndarray[np.float32_t, ndim=1, mode="c"] cGridMax
    cdef np.ndarray[np.float32_t, ndim=1, mode="c"] cResult
    npSamples = np.array(samples)
    npSamples = npSamples.astype(np.float32)
    
    cSamples = np.ascontiguousarray(npSamples, dtype=np.float32)
    cNumSteps = np.ascontiguousarray(numSteps, dtype=np.uint32)
    cGridMax = np.ascontiguousarray(gridMax, dtype=np.float32)
    cResult = np.ascontiguousarray([0 for x in range(numSteps[0]*numSteps[1])], dtype=np.float32)
    Qxy(<float*> cResult.data,  <float*> cSamples.data, <unsigned int*> cNumSteps.data, <float*> cGridMax.data, len(samples)/3)
    results = np.reshape(np.array(cResult), (numSteps[0],numSteps[1]))
    return results/(numSamples**2)

def pyQxy(samples,  numSteps, gridMax):
    lSamples = []
    for sample in samples:
        for value in sample:
            lSamples.append(value)
    lResults = py2cQxy(lSamples, numSteps, gridMax, len(samples))
    
    return lResults

def pyPredictSingle(samples,numSteps, gridMax):
    lSamples = []
    for sample in samples:
        for value in sample:
            lSamples.append(value)
    lResults = py2cPredict(0,  lSamples, numSteps, gridMax,  1)
    return (lResults[0],lResults[1])

        

#@cython.boundscheck(False)
#@cython.wraparound(False)
def py2cPredict(algorithm,  samples, numSteps, gridMax,  numSets):
    cdef np.ndarray[np.float32_t, ndim=1, mode="c"] cSamples
    cdef np.ndarray[np.uint32_t, ndim=1, mode="c"] cNumSteps
    cdef np.ndarray[np.float32_t, ndim=1, mode="c"] cGridMax
    cdef np.ndarray[np.float32_t, ndim=1, mode="c"] cResult
    
    cSamples = np.ascontiguousarray(samples, dtype=np.float32)
    cNumSteps = np.ascontiguousarray(numSteps, dtype=np.uint32)
    cGridMax = np.ascontiguousarray(gridMax, dtype=np.float32)
    cResult = np.ascontiguousarray([0 for x in range(numSets*2)], dtype=np.float32)
    predict(<float*> cResult.data, 0, <float*> cSamples.data, <unsigned int*> cNumSteps.data, <float*> cGridMax.data, len(samples)/(3*numSets), numSets)
    
    return cResult
    
    
def pyPredict(samples,numSteps, gridMax):
    lSamples = []
    for sampleGroup in samples:
        for sample in sampleGroup:
            for value in sample:
                lSamples.append(float(value))
    
    numSamples = len(samples[0])
    numSets = len(samples)			
    
    
    
    lResults = py2cPredict(0,  lSamples, map(int,numSteps), map(float,gridMax),  numSets)
    
    results = []
    for x in xrange(numSets):
        prediction = (float(lResults[x*2]),float(lResults[x*2+1]))
        results.append(prediction)
    return results



def pySimpleFitness(samples, emitterPosition, numSteps, gridMax):
        
    def distance(pos1, pos2):
        return sqrt(sum(map(lambda x: (x[0]-x[1])**2, zip(pos1,pos2))))
    
    predictions = pyPredict(samples,[256,256],[100,100])
    
    fitness_value = 0.0
        
    for position in predictions:
        fitness_value += distance(emitterPosition, position)

    fitness_value = fitness_value/len(samples)

    return fitness_value
    
    
def pyFitness(receiverPositions, emitterPosition, numTrials, noiseStdDev, numSteps, gridMax):
    emitterStrength  = 1
    lossFactorA = 2
    def measuredPower(x,y):
        d = sqrt(pow(emitterPosition[0]-x,2)+pow(emitterPosition[1]-y,2))
        if (d < 1.0):
            a = 10*log(emitterStrength,10)
        else:
            a = 10*log(emitterStrength,10) - 10 * lossFactorA * log(d,10)
        n = gauss(0,noiseStdDev)
        return a + n

        
    def distance(pos1, pos2):
        return sqrt(sum(map(lambda x: (x[0]-x[1])**2, zip(pos1,pos2))))
    
    samples = []
    for x in xrange(numTrials):
        t = map(lambda x: (x[0],x[1],measuredPower(x[0],x[1])), receiverPositions)
        samples.append(t)
    
    predictions = pyPredict(samples,numSteps,gridMax)
    
    fitnessValue = 0.0
        
    for position in predictions:
        fitnessValue += distance(emitterPosition, position)

    fitnessValue = fitnessValue/len(samples)

    return fitnessValue
    
def pyFitnessAlt(receiverPositions, emitterPosition, numTrials, noiseStdDev, numSteps, gridMax):
    
    
    emitterStrength  = 1
    lossFactorA = 2
    def measuredPower(x,y):
        d = sqrt(pow(emitterPosition[0]-x,2)+pow(emitterPosition[1]-y,2))
        if (d < 1.0):
            a = 10*log(emitterStrength,10)
        else:
            a = 10*log(emitterStrength,10) - 10 * lossFactorA * log(d,10)
        n = gauss(0,noiseStdDev)
        return a + n

        
    def distance(pos1, pos2):
        return sqrt(sum(map(lambda x: (x[0]-x[1])**2, zip(pos1,pos2))))
    
    samples = []
    for x in xrange(numTrials):
        t = map(lambda x: (x[0],x[1],measuredPower(x[0],x[1])), receiverPositions)
        samples.append(t)
        
    predictions = pyPredict(samples,numSteps,gridMax)
    
    avgDeviation = 0.0
    maxDeviation = 0.0
    minDeviation = max(distance(gridMax, emitterPosition), distance((0.0,0.0), emitterPosition))*2.0
    deviations = []
        
    for position in predictions:
        d = distance(emitterPosition, position)
        avgDeviation += d
        if maxDeviation < d:
            maxDeviation = d
        if minDeviation > d:
            minDeviation = d
        deviations.append(d)

    avgDeviation = avgDeviation/len(samples)


    mean_x, mean_y = 0.0,0.0
    for x,y in predictions:
        mean_x += x
        mean_y += y
    mean_x = mean_x / len(samples)
    mean_y = mean_y / len(samples)
    
    
    varPredictions = 0.0
    for x,y in predictions:
        varPredictions += (x - mean_x)**2 + (y - mean_y)**2
    varPredictions = varPredictions/len(samples)

    absBias = distance(emitterPosition, (mean_x,mean_y))
    
    fitnessValue = avgDeviation * varPredictions


    return fitnessValue, avgDeviation, maxDeviation, minDeviation, varPredictions, absBias
    

    
def pyMultipleFitness(receiverSets, emitterPosition, numTrials, noiseStdDev, stepSize, gridMax, fixedNoise = False):
    
    #NOTE: CUDA NLLS DOES NOT SUPPORT RESOLUTION LESS THAN (256,256)
    tx = int(log(gridMax[0] / stepSize)/log(2.0))
    numStepsX = max(256, 2.0**tx)
    ty = int(log(gridMax[1] / stepSize)/log(2.0))
    numStepsY = max(256, 2.0**ty)
    numSteps = [numStepsX,numStepsY]
    
    state = random.getstate()
    results = []
    for receiverPositions in receiverSets:
        if fixedNoise:
            random.setstate(state)
        t = pyFitnessAlt(receiverPositions, emitterPosition, numTrials, noiseStdDev, numSteps, gridMax)
        results.append(t)
    if fixedNoise:
        random.setstate(state)
    return results
