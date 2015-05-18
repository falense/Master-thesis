

#define DEBUG false
#define BENCHMARK true
#define CPU_ENABLED false
#define GPU_ENABLED true

// System includes
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <assert.h>
#include <iostream>
#include <sys/time.h>
#include <iomanip>

// CUDA runtime
#include <cuda_runtime.h>

// helper functions and utilities to work with CUDA
#include "helper_cuda.h"
//#include <helper_functions.h>

#ifndef MAX
#define MAX(a,b) (a > b ? a : b)
#endif




__device__ float devEuclidianDistanceSquared(const float x1,const  float y1,const  float x2,const  float y2){
		float t1 = x1-x2;
		float t2 = y1-y2;
		return t1*t1 + t2*t2; 
}


#define ALPHA 2.0f


__global__ void devCalculateQxy(float * __restrict__ resultGrid,  const float stepX, const float stepY,  const float *  __restrict__ samples, const unsigned int  sampleCount)
{
	const unsigned int resRowDim = blockDim.x * gridDim.x;
	const unsigned int resY = blockIdx.y*blockDim.y + threadIdx.y;
	const unsigned int resX = blockIdx.x*blockDim.x + threadIdx.x;
	
    const unsigned int posX = resX*stepX;
    const unsigned int posY = resY*stepY;
    
	float ret = 0.0;
	for (unsigned int k = 0; k < (sampleCount); k++){
        float dk = devEuclidianDistanceSquared(posX,posY,samples[k*3+0],samples[k*3+1]);
        float Pk = samples[k*3+2];
        float lDk = log10(dk);
		for (unsigned int l = k+1; l < (sampleCount); l++){
            float dl = devEuclidianDistanceSquared(posX,posY,samples[l*3+0],samples[l*3+1]);
			float p = Pk-samples[l*3+2] - 5.0f * ALPHA * (log10(dl)-lDk);
			ret += p * p;
		}
	}
	
	resultGrid[resX+resRowDim*resY] = ret;
    return;
}

__global__ void devReduction(float *g_idata, float *g_odata, unsigned int * g_oindexdata, const unsigned int numElements){
	unsigned int tid = blockIdx.x*blockDim.x + threadIdx.x;
	
	unsigned int numThreads = blockDim.x*gridDim.x;
	
	unsigned int numElementsPerThread = numElements/numThreads;
	
	unsigned int blockIndex = blockDim.x * blockIdx.x * numElementsPerThread ;
	unsigned int startIndex = threadIdx.x * numElementsPerThread + blockIndex; 
	
	unsigned int bestIndex = startIndex;
	float bestScore = g_idata[startIndex];
	for (unsigned int i = startIndex; i < startIndex+numElementsPerThread; i++){
		if (g_idata[i] < bestScore){
			bestIndex = i;
			bestScore = g_idata[i];
		}
	}
		
	g_odata[tid] = bestScore;
	g_oindexdata[tid] = bestIndex;
	
	__syncthreads();
	
	unsigned int number = 1;
	
	while ( number <= (blockDim.x >> 1)){
		if (tid % (number*2) == 0){
			if (g_odata[tid] > g_odata[tid+number])
			{
				g_odata[tid] = g_odata[tid+number];
				g_oindexdata[tid] = g_oindexdata[tid+number];
			}
			
		}
		number <<= 1;
		
		__syncthreads();
	}
}



__global__ void devFinalReduction(float *g_odata, unsigned int * g_oindexdata, unsigned int stride){
	unsigned int numThreads = blockDim.x;
	unsigned int tid = threadIdx.x;
	
	unsigned int number = 1;
	
	while ( number <= (numThreads >> 1)){
		if (tid % (number*2) == 0){
			unsigned int firstIndex = stride*tid;
			unsigned int secondIndex = stride*(tid+number);
			if (g_odata[firstIndex] > g_odata[secondIndex])
			{
				g_odata[firstIndex] = g_odata[secondIndex];
				g_oindexdata[firstIndex] = g_oindexdata[secondIndex];
			}
		}
		number <<= 1;
		
		__syncthreads();
	}
}



inline float EuclidianDistanceSquared(const float x1,const  float y1,const  float x2,const  float y2){
		float t1 = x1-x2;
		float t2 = y1-y2;
		return t1*t1 + t2*t2; 
}


float Qxy(const float *pos, const float*  samples, const unsigned int sampleCount){
	float ret = 0.0;
	for (unsigned int k = 0; k < sampleCount; k++){
        float dk = EuclidianDistanceSquared(pos[0],pos[1],samples[k*3+0],samples[k*3+1]);
        
        
		for (unsigned int l = k+1; l < sampleCount; l++){
			//std::cout << "S:" << k << ":" << l << std::endl;
            float dl = EuclidianDistanceSquared(pos[0],pos[1],samples[l*3+0],samples[l*3+1]);
			float p = samples[k*3+2]-samples[l*3+2] - 5 * ALPHA * log10(dl/dk);
			ret += p * p;
		}
	}
	return ret;
}

void calculateQxy(float * resultGrid, const unsigned int * numSteps, const float * step, unsigned int  *bestPos, const float *samples, const unsigned int sampleCount)
{	
	
	float bestScore = 999999999.0;
	float pos[] = {0.0,0.0};
	for (int x = 0; x < numSteps[0]; x ++){
		//std::cout << "x:" << x ;
        pos[0] = x*step[0];
		for (int y = 0; y < numSteps[1]; y ++){
			//std::cout << " y:" << y << std::endl;
            pos[1] = y*step[1];
			float score = Qxy(pos,samples, sampleCount);
			if (score < bestScore){
				bestScore = score;
				bestPos[0] = x;
				bestPos[1] = y;
			}
			resultGrid[x+y*numSteps[0]] = score;
		}
	}
}

double gpuWrapperQxy(const dim3 & grid,const dim3  & threads,float * d_resultGrid, const float & stepX, const float & stepY,float * d_samples, const float * samples, const unsigned int & sampleCount){
	
    struct timeval t1, t2;
    double gpuTimeQxy;
    
    // Copy data to device
    checkCudaErrors(cudaMemcpy(d_samples, samples, sizeof(float) * 3 * sampleCount,cudaMemcpyHostToDevice));

    if (DEBUG)
		std::cout << std::endl << "Computing on GPU" << std::endl;
    
	if (BENCHMARK)
		gettimeofday(&t1, 0);
	
	devCalculateQxy<<< grid, threads >>>(d_resultGrid,stepX, stepY,d_samples,sampleCount);
    getLastCudaError("Kernel execution failed");
    
	checkCudaErrors(cudaThreadSynchronize());
	
	
	if (BENCHMARK){
		gettimeofday(&t2, 0);
		gpuTimeQxy = (1000000.0*(t2.tv_sec-t1.tv_sec) + t2.tv_usec-t1.tv_usec);
	}
	
    if (DEBUG){
		std::cout << "Done computing on GPU" << std::endl;
	
		if (BENCHMARK){
			printf("Time to generate:  %3.1f us \n", gpuTimeQxy);
		}
	}
	
	return gpuTimeQxy;
}

double cpuWrapperPredict(float * resultGridFromDevice, const float * d_resultGrid, const unsigned int gridMemSize, unsigned int * gpuBestPos, const unsigned int * numSteps, const float * step ){	
    struct timeval t1, t2;
    double cpuTimeReduction;
    
	if (DEBUG){
		std::cout << std::endl << "Calulating GPU prediction on CPU" << std::endl;
	}
    
    if (BENCHMARK)
		gettimeofday(&t1, 0);
	
    // copy results from device to host
    checkCudaErrors(cudaMemcpy(resultGridFromDevice, d_resultGrid, gridMemSize, cudaMemcpyDeviceToHost));
	
	float gpuBestScore = resultGridFromDevice[0];
	gpuBestPos[0] = 0;
	gpuBestPos[1] = 0;
	for (unsigned int x = 0; x < numSteps[0]; x++){
		for (unsigned int y = 0; y < numSteps[1]; y++){
			if (gpuBestScore > resultGridFromDevice[x+y*numSteps[0]]){
				gpuBestScore = resultGridFromDevice[x+y*numSteps[0]];
				gpuBestPos[0] = x;
				gpuBestPos[1] = y;
			}
				
		}
	}
	
	if (BENCHMARK){
		gettimeofday(&t2, 0);
		cpuTimeReduction = (1000000.0*(t2.tv_sec-t1.tv_sec) + t2.tv_usec-t1.tv_usec);	
	}
	
	if (DEBUG){
		std::cout <<  "GPU: Predicted position (" << gpuBestPos[0]*step[0] << "," << gpuBestPos[1]*step[1] << ")" <<  ", (x,y) = (" << gpuBestPos[0] << "," << gpuBestPos[1] << ")" << std::endl;
		std::cout << "Value: "  <<  gpuBestScore << std::endl;
		
		std::cout << "Finished calculating GPU prediction on CPU" << std::endl;
		

		if (BENCHMARK)
			printf("Time to generate:  %3.1f us \n", cpuTimeReduction);
	}
	return cpuTimeReduction;
}

double gpuWrapperPredict(float * d_resultGrid, const unsigned int gridSize, unsigned int *gpuBestPos, const unsigned int * numSteps, const float * step){	
	  
    struct timeval t1, t2;
    double gpuTimeReduction;
    
    float * d_maxResultGrid;
    float maxResult;
    unsigned int * d_maxIndexResultGrid;
    unsigned int maxIndexResult;
    
    
    checkCudaErrors(cudaMalloc((void**)&d_maxResultGrid, sizeof(float)*gridSize));
    checkCudaErrors(cudaMalloc((void**)&d_maxIndexResultGrid, sizeof(unsigned int)*gridSize));
	  
    dim3 gridPrediction(32,1, 1);
    dim3 threadsPrediction(1024, 1, 1);
    
	dim3 gridFinalReduction(1,1,1);
	dim3 blockFinalReduction(gridPrediction.x,1,1);
	
	if (DEBUG){
		std::cout << std::endl << "Calculating GPU prediction on GPU" << std::endl;
	}	
	
	if (BENCHMARK)
		gettimeofday(&t1, 0);
	
	devReduction<<< gridPrediction, threadsPrediction >>>(d_resultGrid,d_maxResultGrid,d_maxIndexResultGrid,gridSize);
    getLastCudaError("Kernel execution failed");
    
	checkCudaErrors(cudaThreadSynchronize());
	
	devFinalReduction<<< gridFinalReduction,blockFinalReduction>>>(d_maxResultGrid,d_maxIndexResultGrid,threadsPrediction.x);
    getLastCudaError("Kernel execution failed");
	
    checkCudaErrors(cudaMemcpy(&maxIndexResult, d_maxIndexResultGrid, sizeof(unsigned int), cudaMemcpyDeviceToHost));
    checkCudaErrors(cudaMemcpy(&maxResult, d_maxResultGrid, sizeof(float), cudaMemcpyDeviceToHost));
    
    if (BENCHMARK){
		gettimeofday(&t2, 0);
		gpuTimeReduction = (1000000.0*(t2.tv_sec-t1.tv_sec) + t2.tv_usec-t1.tv_usec);
	}
	
	gpuBestPos[0] = maxIndexResult%numSteps[0];
	gpuBestPos[1] = maxIndexResult/numSteps[1];
	
	if (DEBUG){
		std::cout << "GPU reduction: (" << gpuBestPos[0]*step[0]  << "," << gpuBestPos[1]*step[1] << ")\t " <<  maxIndexResult<< std::endl;
		std::cout << "Value: "   << maxResult << std::endl;
		
		std::cout << "Finished calculating GPU prediction on GPU" << std::endl;
		if (BENCHMARK)
			printf("Time to generate:  %3.1f us \n", gpuTimeReduction);
	}
	
	checkCudaErrors(cudaFree(d_maxResultGrid));
	checkCudaErrors(cudaFree(d_maxIndexResultGrid));
	
	return gpuTimeReduction;
}

double cpuWrapperQxy(float * resultGrid, const unsigned int * numSteps, const float * step, unsigned int * cpuBestPos, const float * samples, const unsigned int sampleCount, const double cpuTimeReduction){
	struct timeval t1, t2;
    double cpuTimeQxy;
    
    if(DEBUG)
		std::cout << std::endl << "Computing on CPU" << std::endl;
    
	if (BENCHMARK)
		gettimeofday(&t1, 0);
	
	calculateQxy(resultGrid, numSteps, step, cpuBestPos, samples, sampleCount);
	
	if (BENCHMARK){
		gettimeofday(&t2, 0);
		cpuTimeQxy = (1000000.0*(t2.tv_sec-t1.tv_sec) + t2.tv_usec-t1.tv_usec) - cpuTimeReduction;
	}
	
    if(DEBUG){
		std::cout << "CPU: Predicted position (" << cpuBestPos[0]*step[0] << "," << cpuBestPos[1]*step[0] << ") , (x,y) = (" << cpuBestPos[0] << "," << cpuBestPos[1] << ")" << std::endl;
		std::cout << "Done computing on CPU" << std::endl;
		
		
		if(BENCHMARK){
			printf("Time to generate:  %3.1f us \n", cpuTimeReduction+cpuTimeQxy);
		}
 
	}
	
	return cpuTimeQxy;
}


void Qxy(float * resultGridFromDevice, float *samples, unsigned int * numSteps, float * gridMax, unsigned int numSamples){
	
	if (DEBUG){
		std::cout << "GridMax: (" << gridMax[0] << "," << gridMax[1] << ")" << std::endl;
		std::cout << "NumSteps: (" << numSteps[0] << "," << numSteps[1] << ")" << std::endl;
		std::cout << "NumSamples: " << numSamples << std::endl;
		
	}
	// use command-line specified CUDA device, otherwise use device with highest Gflops/s
	findCudaDevice(0, 0);
	
	const float step [] = {gridMax[0]/numSteps[0],gridMax[1]/numSteps[1]};
		
	const unsigned int gridSize = numSteps[0] * numSteps[1];
	
	const unsigned int gridMemSize = gridSize * sizeof(float);
	const unsigned int sampleMemSize = sizeof(float) * 3 * numSamples;

	// Allocate device memory
	float *d_samples;
	float *d_resultGrid;
	
	checkCudaErrors(cudaMalloc((void**)&d_samples, sampleMemSize));
	checkCudaErrors(cudaMalloc((void**)&d_resultGrid, gridMemSize));
	
	// Setup grid and block sizes
	const unsigned int threadBlockDim = 16;
	dim3 grid(numSteps[0]/threadBlockDim, numSteps[1]/threadBlockDim, 1);
	dim3 threads(threadBlockDim, threadBlockDim, 1);
	
	std::cout << std::setprecision(3) << std::fixed;
	
	if (GPU_ENABLED)
		gpuWrapperQxy(grid,threads, d_resultGrid, step[0], step[1], d_samples, samples, numSamples);
	
	checkCudaErrors(cudaMemcpy(resultGridFromDevice, d_resultGrid, gridMemSize, cudaMemcpyDeviceToHost));
	
	
}


void predictSingle(float * result, int algorithm,  float *samples, unsigned int * numSteps,float * gridMax,unsigned int numSamples){
	if (algorithm == 0){
			if (DEBUG){
				std::cout << "Using algorithm: " << algorithm << std::endl;
				std::cout << "GridMax: (" << gridMax[0] << "," << gridMax[1] << ")" << std::endl;
				std::cout << "NumSteps: (" << numSteps[0] << "," << numSteps[1] << ")" << std::endl;
				std::cout << "NumSamples: " << numSamples << std::endl;
				
			}
			// use command-line specified CUDA device, otherwise use device with highest Gflops/s
			findCudaDevice(0, 0);
			
			const float step [] = {gridMax[0]/numSteps[0],gridMax[1]/numSteps[1]};
				
			const unsigned int gridSize = numSteps[0] * numSteps[1];
			
			const unsigned int gridMemSize = gridSize * sizeof(float);
			const unsigned int sampleMemSize = sizeof(float) * 3 * numSamples;

			unsigned int cpuCalcGpuBestPos [] = {0,0};
			unsigned int gpuBestPos [] = {0,0};
			unsigned int cpuBestPos[] = {0,0};
			
			double gpuTimeQxy;
			double gpuTimeReduction;
			double cpuTimeQxy;
			double cpuTimeReduction;
			
			float *resultGrid = (float*) malloc(gridMemSize);
			float *resultGridFromDevice = (float*) malloc(gridMemSize);
			
			// Allocate device memory
			float *d_samples;
			float *d_resultGrid;
			
			checkCudaErrors(cudaMalloc((void**)&d_samples, sampleMemSize));
			checkCudaErrors(cudaMalloc((void**)&d_resultGrid, gridMemSize));
			
			// Setup grid and block sizes
			const unsigned int threadBlockDim = 16;
			dim3 grid(numSteps[0]/threadBlockDim, numSteps[1]/threadBlockDim, 1);
			dim3 threads(threadBlockDim, threadBlockDim, 1);
			
			std::cout << std::setprecision(3) << std::fixed;
			
			if (GPU_ENABLED)
				gpuTimeQxy = gpuWrapperQxy(grid,threads, d_resultGrid, step[0], step[1], d_samples, samples, numSamples);
			
			if (CPU_ENABLED)
				cpuTimeReduction = cpuWrapperPredict(resultGridFromDevice, d_resultGrid, gridMemSize, cpuCalcGpuBestPos, numSteps, step);
			
			if (GPU_ENABLED)
				gpuTimeReduction = gpuWrapperPredict(d_resultGrid, gridSize, gpuBestPos, numSteps, step);
			
			if (CPU_ENABLED)
				cpuTimeQxy = cpuWrapperQxy(resultGrid, numSteps, step,  cpuBestPos, samples, numSamples, cpuTimeReduction);
			
			if (DEBUG && CPU_ENABLED && GPU_ENABLED){
				float error = sqrt(pow(cpuBestPos[0]-gpuBestPos[0],2)+pow(cpuBestPos[1]-gpuBestPos[1],2));
				std::cout << "GPU vs CPU error was: " << error << std::endl;
		
				if(BENCHMARK){
					printf("\n\t\t Qxy \t\t Reduction \t\t Qxy + Reduction \n");
					printf("CPU: \t %10.1f \t\t %10.1f \t\t %10.1f \n", cpuTimeQxy, cpuTimeReduction, cpuTimeQxy+cpuTimeReduction);
					printf("GPU: \t %10.1f \t\t %10.1f \t\t %10.1f \n", gpuTimeQxy, gpuTimeReduction, gpuTimeQxy+gpuTimeReduction);
					printf("Speedup: %10.1f x \t\t %10.1f x \t\t %10.1f x \n", cpuTimeQxy/gpuTimeQxy, cpuTimeReduction/gpuTimeReduction, (cpuTimeQxy+cpuTimeReduction) / (gpuTimeQxy+gpuTimeReduction));
				}
			}

		    checkCudaErrors(cudaFree(d_samples));
		    checkCudaErrors(cudaFree(d_resultGrid));
			free(resultGrid);
			free(resultGridFromDevice);
			
			result[0] = gpuBestPos[0]*step[0];
			result[1] = gpuBestPos[1]*step[1];
	}
	
}

void predict(float * result, int algorithm,  float *samples,unsigned int * numSteps,float * gridMax,unsigned int numSamples,unsigned int numSets){
	
	for ( unsigned int i = 0; i < numSets; i++){
		/*for (unsigned int j = 0; j < numSamples; j++){
			for (unsigned int l = 0; l < 3; l++){
				std::cout << samples[i*numSamples*3 + j*3 + l] << std::endl;
			}
			std::cout << std::endl;
		}*/
		predictSingle(&result[i*2], algorithm, &samples[i*numSamples*3], numSteps, gridMax, numSamples);
	}
}

extern "C" bool
runTest(int argc, char **argv)
{
	/*	float * samples = (float*) malloc(sampleMemSize);
			srand(11);
			for (unsigned int i = 0; i < sampleCount; i++){
				samples[i*3+0] = (float) (rand()%100);
				samples[i*3+1] = (float) (rand()%100);
				samples[i*3+2] = (float) (rand()%10);
				
			}*/
				float samples2 [] = {
			103.044449975,37.5749896125,-26.1923435464 ,
			103.026091643,37.523839946,-25.5523156053 ,
			103.994168647,36.9311709869,-26.4742067687 ,
			106.180122539,35.9270807992,-25.8361988542 ,
			109.290196049,34.5971894763,-25.8526809338 ,
			115.946530409,32.049713707,-26.6842774032 ,
			127.328613766,28.4147515553,-29.6847952096 ,
			133.875968633,24.6830498173,-35.7722972657 ,
			143.106648943,21.1359316569,-30.2415020612 ,
			150.743984466,16.3434303186,-26.6873405738 ,
			156.203120413,13.1654793153,-24.9629362518 ,
			161.974391634,9.81628812497,-28.1841922118 ,
			164.702297142,8.26956669457,-31.4362932872 ,
			166.627383183,6.56050067206,-38.8563342597 ,
			167.110314051,6.35367810877,-34.6971965389 ,
			167.729573226,5.71319533124,-34.1375850024 ,
			167.722353599,5.42631242046,-33.5265873133 ,
			167.433578103,5.95337637291,-35.3004719541 ,
			169.510981532,7.02751936468,-33.9005561564 ,
			173.567809903,10.3500237728,-38.4458296544 ,
			177.61271973,18.391640867,-29.7300924561 ,
			185.796451677,24.6196687086,-27.1066268752 ,
			192.341180063,29.8280390729,-35.5981976925 ,
			196.504742503,33.9144526271,-41.8390766975 ,
			200.716080698,39.1317185847,-33.8883913917 ,
			204.907923252,44.5513593098,-34.393778751 ,
			208.625755546,49.6852290727,-31.4775922602 ,
			214.598995506,55.5140671278,-32.6440687182 ,
			219.646438802,61.4529881598,-34.8694172927 ,
			221.884176772,69.2444166698,-50.3789218541 ,
			219.220136902,73.0739699434,-32.4132878969 ,
			214.978122963,79.8068227518,-32.973072406 ,
			211.640281516,84.9784987897,-34.0524302717 ,
			207.944929,86.4029058002,-29.0272555731 ,
			201.613542127,88.8547539325,-31.2348066541 ,
			191.571280357,92.0727351096,-31.3896116721 ,
			180.84536686,93.6194565392,-29.8945293508 ,
			169.318330547,94.9715868477,-29.4668411486 ,
			157.960500687,94.731405806,-27.6718815559 ,
			145.938924215,95.0494232965,-34.2399422316 ,
			135.981922617,96.2781272356,-31.8002077752 ,
			129.785256945,98.155097597,-29.1874275027 ,
			124.965623704,98.0516863154,-24.0942554996 ,
			121.237590584,96.5238680233,-24.0951838818 ,
			117.934004739,96.3381724962,-25.8207170094 ,
			115.948451371,94.7136146179,-24.0655931066 ,
			114.231016279,94.3700222945,-25.4052220419 ,
			113.483327878,92.9700781676,-23.1736302667 ,
			113.246323658,92.9678542697,-23.6323510354 ,
			112.904172342,92.8777863788,-24.0816911862 ,
			112.943140213,92.111653334,-23.5958904402 ,
			113.162364073,91.3744309702,-24.5591877125 ,
			111.596895885,88.2064875103,-24.5716028518 ,
			110.154366518,85.4288382428,-25.623572934 ,
			108.216142632,82.1341325663,-24.4579167494 ,
			106.164978873,78.7460231516,-22.6656360697 ,
			102.629520311,73.4642641358,-22.1670262145 ,
			96.7474356914,65.2847653322,-21.4916445096 ,
			91.9635027205,59.6694215366,-20.6601490868 ,
			86.9158408255,54.1619368193,-20.5624620322 ,
			83.9800378138,50.7938424915,-21.5829190437 ,
			83.1094638584,45.4431426218,-21.2738889449 ,
			83.8423017339,40.2625709891,-19.5858379141 ,
			84.3486527729,37.3370324687,-20.2683026221 ,
			88.8323866668,34.9808119733,-20.2249963105 ,
			92.7386020518,33.635353361,-20.9845766019 ,
			97.8120674029,31.9296231866,-20.1387172421 ,
			100.885385259,31.9285112372,-21.2429675891 ,
			102.674659421,30.8877267238,-22.3030164832 ,
			102.357506445,31.9385187807,-24.1537852405 ,
			102.62176086,32.4878217179,-22.7039022625 ,
			103.274914458,32.836973788,-22.7135212491 ,
			104.02206951,33.9922890759,-21.9097440792 ,
			104.082112026,35.5501299983,-27.3000627279 ,
			103.863993038,36.5119661135,-22.2377354043 ,
			103.910146378,37.3715028965,-24.3208055833 ,
			103.901780884,38.0853743254,-26.0922559655 ,
			103.956840543,38.7803426167,-20.5548585865 ,
			103.911209788,39.118375194,-25.031573264 ,
			103.817730276,39.5320203214,-24.5408298697 ,
			104.352389753,39.4897662489,-22.2280253548 ,
			104.542110903,39.3596681851,-23.1608972453 ,
			104.70957962,39.1661890125,-22.7137658272 ,
			104.720704468,39.24624936,-22.9558318635
			};

			unsigned int numSamples = 40;
			float * samples = &samples2[0];
			
			const unsigned int magnitude = 10;
			
			unsigned int numSteps[] = {(1 << magnitude),(1 << magnitude)};
			float gridMax[] = {100.0,100.0};
			
			int algorithm  = 0;
			
			float * result = (float*) malloc(sizeof(float)*2);
			predictSingle(result,algorithm,  samples, numSteps, gridMax, numSamples);

    return true;
}
