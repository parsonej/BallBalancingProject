# GEOMETRY FUNCTIONS
# provides conversions for various geometric relationships in the system 

# UPDATE: I DON'T HATE MYSELF EMOUGH TO MATH THIS OUT. GUESSING AND CHEDKING PID INSTEAD LMAO
# THIS DOCUMENT IS NOW UNUSED


# Imports
import math

# Constants
# CONSTANTS
# radius = 20/1000 # [m], radius of ball
# mass = 2.7/1000 # [kg], mass of ball
# inertia = (2/3)*mass*radius**2 # [kg*m^2], second moment of inertia
# g = 9.81 # [m/s^2] grav. 
# pi = math.pi # pi
pi = math.pi # pi
pivotDist2Center = 2.469096
connectingRodDist = 1.681527
servoHornDist = 0.944882
servoAxisDist2Center = 2.281488
servoVertOffset2pivot = -1.781527
zerodegoffset = -16.0919302 # [deg], offset of the servo motor from its zero to make the platform rest at zero degrees.

def ballpos(camx,camy,anglex,angley):
	# takes pixel location of ball and platform angle, returns ball position
    return 0

def servoangle(platangle):
	# takes desired platform angle, returns cooresponding servo angle
	return 0

def platangle(platangle):
	# takes servo angle, returns cooresponding platform angle
	return 0 

