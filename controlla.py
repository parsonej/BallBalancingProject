# CONTROL EQUATION (s)
# takes a history of deltas, returns a set angle

import math
import numpy as np

# note: gain = position Pid constant
#		damper = derivative piD constant	
#		accel = integral pId constant

# do nothing:
def zero():
	return 0

# position (linear) ctrl:
def pos(histDX):
	gain = -.07
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
	
# note: gain = position Pid constant
#		damper = derivative piD constant	
#		accel = integral pId constant

	gain = -.05
	accel = -.015
	damper = -1.5
	
	dervSamples = 12
	intSamples = 50
	
	deltaX = histDX[0]
	areaDX = np.average(histDX[0:50]) #this technically finds the mean offset, not the sum of offset. 
	deltaV = np.mean(histDX[0:dervSamples-1]-histDX[1:dervSamples])
	
	return gain*deltaX + accel*areaDX + damper*deltaV

# sqrt(position) + derivative^2 ctrl:
def sqdv(histDX):
	gain = -.7
	damper = -.3
	deltaX = histDX[0]
	deltaV = np.mean(histDX[0:-1]-histDX[1:])
	if (abs(deltaX) < 1):
		return -damper*deltaV*abs(deltaV)
	return gain*deltaX/math.sqrt(abs(deltaX)) + damper*deltaV*abs(deltaV)

