


void Qxy(float * resultGridFromDevice, float *samples, unsigned int * numSteps, float * gridMax, unsigned int numSamples);

//void predictSingle(float * result, int algorithm,  float *samples,unsigned int * numSteps,float * gridMax,unsigned int numSamples);
void predict(float * result, int algorithm,  float *samples,unsigned int * numSteps,float * gridMax,unsigned int numSamples, unsigned int numSets);

//double ** fitness(int algorithm, int stepSize, int trials, int fitnessAlg,
//	int seed, int noiseType, double noiseStdDev, Triplet **receivers, Triplet emitter,
 //   double emitterStrength, Triplet grid, int pheno_len, int rec_len);
