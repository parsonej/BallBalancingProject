# CONTROL EQUATION (s)
# takes a history of deltas, returns a set angle

import math
import numpy as np


# do nothing:
def zero():
	return 0

# position (linear) ctrl:
def pos(histDX):
	gain = -.1
	return gain*histDX[0]

# position + derivative ctrl:
def derv(histDX):
	gain = -.15
	damper = -1
	deltaX = histDX[0]
	deltaV = np.mean(histDX[0:-1]-histDX[1:])
	return gain*deltaX + damper*deltaV

# position + integral + derivative ctrl:
def PID(histDX):
	gain = -.15
	trample = -.05
	damper = -3
	
	dervSamples = 3
	deltaX = histDX[0]
	areaDX = np.sum(histDX[0])
	deltaV = np.mean(histDX[0:dervSamples-1]-histDX[1:dervSamples])
	
	return gain*deltaX + trample*areaDX + damper*deltaV

# sqrt(position) + derivative^2 ctrl:
def sqdv(histDX):
	gain = -.7
	damper = -.3
	deltaX = histDX[0]
	deltaV = np.mean(histDX[0:-1]-histDX[1:])
	if (abs(deltaX) < 1):
		return -damper*deltaV*abs(deltaV)
	return gain*deltaX/math.sqrt(abs(deltaX)) + damper*deltaV*abs(deltaV)

