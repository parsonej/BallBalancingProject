# Servo Testing/Functions
# call turnoff() to turn off servos
import pigpio
import time
import numpy as np

# CONSTANTS
xPIN = 18 # GPIO pin of the siginal wire to the x-servo
yPIN = 19 # GPIO pin of the siginal wire to the y-servo
xOFFSET = 0 # manual adjustment to fix zero angle
yOFFSET = -0.5 #23 manual adjustment to fix zero angle
maxplatformangle = 13
maxservoangle = 60

# Setup pigpio
if not pigpio.pi().connected:
    print("Failed to connect to pigpio daemon.")
    exit()

pig = pigpio.pi()  # Connect once
    
def setx(platformangle):
# Convert angle (-90 to 90) to pulsewidth (500–2500 microseconds)
    #rint("Platform Angle: ", platformangle)
    angle=convert(np.radians(constrain(platformangle,maxplatformangle)))
    #print("Angle to set: ", angle)
    pulsewidth = int(1500 + (angle - xOFFSET)*2000/255 )
    # i think that 255 is the full ROM of the servo. or sm. 
    # idk whatever, it seems to get roughly 180deg range, cool w me
    pig.set_servo_pulsewidth(xPIN, pulsewidth)
    
def sety(platformangle):
    # Convert angle (-90 to 90) to pulsewidth (500–2500 microseconds)
    angle=convert(np.radians(constrain(platformangle,maxplatformangle)))
    
    pulsewidth = int(1500 + (-angle - yOFFSET)*2000/255)
    # i think that 255 is the full ROM of the servo. or sm. 
    # idk whatever, it seems to get roughly 180deg range, cool w me
    pig.set_servo_pulsewidth(yPIN, pulsewidth)

def HARDRESET():
    pig.set_servo_pulsewidth(xPIN, 1500)
    pig.set_servo_pulsewidth(yPIN, 1500)


def constrain(angle,maximum):
    if (angle>=maximum):
        #print("platform angle greater than maximum, constraining; " + str(int(angle)))
        angle=maximum
    if (angle<=-maximum):
        #print("platform angle greater than maximum, constraining; " + str(int(angle)))
        angle=-maximum
    return angle
    
def convert(platformangle):
    #angle = -22.5*np.cos(platformangle) -4.65*np.sin(platformangle)
    
    angle = 37 * np.tan(platformangle*3) + 11.81 * np.cos(platformangle*4)
    #("Angle before constrain: ", angle)
    #print("After constrain: ", constrain(angle, maxservoangle))
    return constrain(angle,maxservoangle)
    
    
def turnoff():
    print("leveling platform and stopping servos")
    setx(0)
    sety(0)
    time.sleep(1)
    pig.set_servo_pulsewidth(xPIN, 0)
    pig.set_servo_pulsewidth(yPIN, 0)
    time.sleep(.2)
    pig.stop()
    time.sleep(.2)

