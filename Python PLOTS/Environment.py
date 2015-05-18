from math import sqrt, log, log10
from random import gauss

class Environment:
	emitterStrength  = None
	emitterPosition = None
	lossFactorA = 2
	def __init__(self,emitterPosition, emitterStrength, noiseStdDev):
		self.setEmitterPos(emitterPosition, emitterStrength)
		self.setNoiseStdDev(noiseStdDev)
	def setEmitterPos(self,emitterPosition, emitterStrength):
		self.emitterPosition = map(float,emitterPosition)
		self.emitterStrength = float(emitterStrength)
	def setNoiseStdDev(self,stdDev):
		self.stdDev = float(stdDev)
	def Noise(self):
		return gauss(0,self.stdDev)
	def emitterStrengthdBm(self):
		return 10*log(self.emitterStrength,10)
	def ActualPower(self,x,y):
		d = sqrt(pow(self.emitterPosition[0]-x,2)+pow(self.emitterPosition[1]-y,2))
		if d == 0: return self.emitterStrengthdBm()
		else:
			return self.emitterStrengthdBm() - 10 * self.lossFactorA * log(d,10)
	def MeasuredPower(self,x,y):
		a = self.ActualPower(x,y)
		n = self.Noise()
		return a + n
