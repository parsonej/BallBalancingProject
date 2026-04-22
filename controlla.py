# CONTROL EQUATION (s)
# takes a history of deltas, returns a set angle

import math
import numpy as np
import matplotlib.pyplot as plt

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
def plot_errors(timestamps, errorDX, errorDY, save_path="error_plot.png"):
	"""Plot tracking error over time"""
	fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
	
	ax1.plot(timestamps, errorDX, color='steelblue')
	ax1.set_ylabel("Error X")
	ax1.set_title("Tracking Error Over Time")
	ax1.grid(True)
	
	ax2.plot(timestamps, errorDY, color='coral')
	ax2.set_ylabel("Error Y")
	ax2.set_xlabel("Time (s)")
	ax2.grid(True)
	
	plt.tight_layout()
	plt.savefig(save_path)
	plt.close()
	print(f"Plot saved to {save_path}")

