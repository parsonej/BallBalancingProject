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
historyct = 100 # number of points captured for vel/int stuff
timeinit = time.time()

# SETUP
def updateMotion():
	global desX
	global desY
	# test = zeros, circle = you can prolly guess
	des = motion.test(time.time()-timeinit)
	desX = des[0]
	desY = des[1]
updateMotion()
	
def updateDX():
	pos = camera.getCoords()
	global posX 
	global posY 
	global DX 
	global DY 
	posX = pos[0]
	posY = pos[1]
	DX = round(posX-desX,1)
	DY = round(posY-desY,1)
updateDX()

histDX = [DX, DX]
histDY = [DY, DY]

timeout = time.time() + runtime

while True: 
	tstart = time.time()
	updateMotion()
	updateDX()

	if(len(histDX) > historyct):
		histDX = np.concatenate(([DX], histDX))
		histDY = np.concatenate(([DY], histDY))		
	else:
		histDX = np.concatenate(([DX], histDX[0:-1]))
		histDY = np.concatenate(([DY], histDY[0:-1]))
	
	#servo.setx(controlla.PID(histDX))
	#servo.sety(controlla.PID(histDY))
	
	servo.setx(controlla.PID(histDX))
	servo.sety(controlla.PID(histDY))
	
	camera.dispframe(desX,desY)

	Dt = time.time()-tstart # actual time per cycle

	print("pos:",str(posX),",",str(posY),"  delta:",str(DX),",",str(DY),"  dt:",round(Dt,3)," rtime",round(time.time()-timeinit,2))

	if time.time() > timeout:
		break
	if (dt > Dt):
		time.sleep(dt - Dt)
score, metrics = motion.calculate_performance(histDX, histDY, dt)
print(f"Performance Score: {score:.2f}")
print(f"Metrics: {metrics}")

camera.turnoff()
servo.turnoff()
time.sleep(3)
