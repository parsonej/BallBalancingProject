# BALANCING TABLE -- MAIN
# CREATED JUNE 2025 BY JEREMIAH SWEENY
# VERSION 0.0 

# CONVENTIONS
# the top/back of the table is the side with the back panel. that side is in the negative y direction from the center. 
# "positive" x & y angles make the ball move in the positive x and *negative* y direction. 
# in other words, the normal vector for the x-rotation points along the positive y-axis, and the normal vector for the y-rotation points along the positive x-axis
# desired positions range from -100 to +100. these translates to +/- 250px, or 500 of the 675 picked up by the camera

# IMPORTS
import deg
import math
import servo
import time
import motion
import camera
import controlla
import numpy as np

# VARIABLES
runtime = 17 # [s] time before ending program
rate = 20 # [hz] max rate at which servo positions are set
dt = 1/rate # needed time between cycles to hit rate
maxHistory = 100 # number of points captured for vel/int stuff
timeinit = time.time()

# SETUP
def update_motion_DX():
	pos = camera.getCoords()
	des = motion.circle(time.time()-timeinit)
	desX = des[0]
	desY = des[1]
	posX = pos[0]
	posY = pos[1]
	DX = round(posX-desX,1)
	DY = round(posY-desY,1)
	return pos, des, [DX, DX], [DY, DY]

def runSystem():
	timeout = time.time() + runtime
	all_errors_x = []
	all_errors_y = []
	timestamps = []
	step = 0
	histDX = []
	histDY = []
	pos, des, histX, histY = update_motion_DX()
	histDX = histX
	histDY = histY
	while True: 
		tstart = time.time()
		# get current position, desired position, and error history
		pos, des, histX, histY = update_motion_DX()
		print("HistDX Length: ", len(histDX))

		#Track error history for performance evaluation
		all_errors_x.append(abs(histDX[0]))
		all_errors_y.append(abs(histDY[0]))
		timestamps.append(time.time() - timeinit)

		#If error history is too long, drop oldest point.
		if(len(histDX) > maxHistory):
			histDX = np.concatenate(([histX[0]], histDX))
			histDY = np.concatenate(([histY[0]], histDY))	
		#If error history is not full, push the current error.	
		else:
			histDX = np.concatenate(([histX[0]], histDX[0:-1]))
			histDY = np.concatenate(([histY[0]], histDY[0:-1]))
		
		
		#Set servo angles based on control algorithm output
		servo.setx(controlla.PID(histDX))
		servo.sety(controlla.PID(histDY))

		camera.dispframe(des[0],des[1])
		Dt = time.time()-tstart # actual time per cycle
		print("pos:",str(pos[0]),",",str(pos[1]),"  delta:",str(histX[0]),",",str(histY[0]),"  dt:",round(Dt,3)," rtime",round(time.time()-timeinit,2))
		step += 1
		if time.time() > timeout:
			break
		if (dt > Dt):
			time.sleep(dt - Dt)

#score, metrics = motion.calculate_performance(all_errors_x, all_errors_y, dt)
#print(f"Performance Score: {score:.2f}")
#print(f"Metrics: {metrics}")
#controlla.plot_errors(timestamps, all_errors_x, all_errors_y)
runSystem()
camera.turnoff()
servo.turnoff()
time.sleep(3)
