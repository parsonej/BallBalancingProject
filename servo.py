# Servo Testing/Functions
# call turnoff() to turn off servos
import pigpio
import time

# CONSTANTS
xPIN = 18 # GPIO pin of the siginal wire to the x-servo
yPIN = 19 # GPIO pin of the siginal wire to the y-servo
xOFFSET = -8.7 # manual adjustment to fix zero angle
yOFFSET = -3.0 # manual adjustment to fix zero angle
levelangle = 25
maxangle=30


# Setup pigpio
if not pigpio.pi().connected:
    print("Failed to connect to pigpio daemon.")
    exit()

pig = pigpio.pi()  # Connect once
    
def setx(angle):
# Convert angle (-90 to 90) to pulsewidth (500–2500 microseconds)
    angle=constrain(angle)
    
    pulsewidth = int(500 + (90 - angle - xOFFSET - levelangle) / 255 * 2000)
    # i think that 255 is the full ROM of the servo. or sm. 
    # idk whatever, it seems to get roughly 180deg range, cool w me
    pig.set_servo_pulsewidth(xPIN, pulsewidth)
    
def sety(angle):
    # Convert angle (-90 to 90) to pulsewidth (500–2500 microseconds)
    angle=constrain(angle)
    
    pulsewidth = int(500 + (90 - angle - yOFFSET + levelangle) / 255 * 2000)
    # i think that 255 is the full ROM of the servo. or sm. 
    # idk whatever, it seems to get roughly 180deg range, cool w me
    pig.set_servo_pulsewidth(yPIN, pulsewidth)

def constrain(angle):
    if (angle>=maxangle):
        print("servo angle greater than maximum, constraining")
        angle=maxangle
    if (angle<=-maxangle):
        print("servo angle greater than maximum, constraining")
        angle=-maxangle
    return angle

def turnoff():
    print("leveling platform and stopping servos")
    setx(0)
    sety(0)
    time.sleep(1)
    pig.set_servo_pulsewidth(xPIN, 0)
    pig.set_servo_pulsewidth(yPIN, 0)
    time.sleep(.2)
    pig.stop()
