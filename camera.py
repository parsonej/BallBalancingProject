# ALL THINGS CAMERA

import cv2
from picamera2 import Picamera2
from libcamera import ColorSpace
import time
import math

picam2 = Picamera2()

config=picam2.create_still_configuration(main={"size":(1350, 1350),"format":"RGB888"})
picam2.configure(config)

picam2.start()

def getCoords():
	global cX
	global cY
	global rotated
	global gray
	global thresh
	# take a frame
	image = picam2.capture_array()
	resized = cv2.resize(image, (675,675), interpolation = cv2.INTER_AREA)
	rotated = cv2.rotate(resized, cv2.ROTATE_180)
	blur = cv2.blur(rotated,(7,7))
	gray = cv2.cvtColor(blur, cv2.COLOR_RGB2GRAY)
	ret,thresh = cv2.threshold(gray,220,255,0)
	
	# calculate moments of binary image
	M = cv2.moments(thresh)
	 
	# calculate x,y coordinate of center
	if(M["m00"]>0):
		cX = int(M["m10"] / M["m00"])
		cY = int(M["m01"] / M["m00"])
	else:
		cX = 338 
		cY = 338
	
	# return converted coords:
	return (pxtocoord(cX),pxtocoord(cY))
	
def dispframe(desX,desY):
	settarget()
	
	desX = coordtopx(desX)
	desY = coordtopx(desY)
	# mark the ball center and desired location
	# dist2center = math.hypot(cX-338,cY-338)
	circrad = round(60 + math.hypot(cX-338,cY-338)/40)
	# circrad = 60
	
	cv2.circle(target, (desX, desY), circrad-1, (0, 255, 0),2)
	cv2.circle(target, (desX, desY), circrad+1, (255, 0, 0),2)
	
	cv2.circle(target, (cX, cY), circrad, (0, 0, 0), 7)
	cv2.circle(target, (cX, cY), circrad, (255, 255, 255), 3)
	
	# display the image	
	cv2.imshow("Frame", target)
	if(cv2.waitKey(1) == ord("p")):
		# no idea why but removing this functionality breaks the display
		cv2.imwrite("test_frame.png", target)
		print("you saved a frame")
		time.sleep(.5)
	
def settarget():
	# sets frame to display based on current runtime
	tenSecLoop = int(time.time()%10)
	global target
	if(tenSecLoop >= 5):
		target = thresh
	else:
		target = rotated
		

def pxtocoord(pixel_location):
	return round((pixel_location-(675/2)) / 2.5,2)
	
def coordtopx(coordinate):
	return round(coordinate*2.5+(675/2))
	
def turnoff():
	cv2.destroyAllWindows()
	
	
#while True:
#	starttime = time.perf_counter()
#	getCoords(0,0)
#	endtime = time.perf_counter()
#	runtime = endtime-starttime
#	print(str(runtime))
