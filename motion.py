# MOTION PROFILES
# returns des as a fn of time :)
# desired positions range from -100 to +100. these translates to +/- 250px, or 500 of the 675 picked up by the camera

import math
import time
import random

delaytime = 0
desx = 0
desy = 0


# setpoint format: (time [s], [desx, desy])
# test duration: 5s centering + 20s runtime 
setpoints = [
    (0, [0, 0]), 
    (5, [60, 60]), 
    (10, [-80, -80]), 
    (14, [-20,-20]),
    (17, [0, 0])
]

test_times = [p[0] for p in setpoints]
test_posns = [p[1] for p in setpoints]

current_pos = test_posns[0]
    
def test(t):
    # standard test for functionality. 
    # uses test setpoints defined above
    for i in range(len(test_times)):
        if t >= test_times[i]:
            current_pos = test_posns[i]
        else:
            break

    return current_pos


def manual(t):
      
    return [0,0]

def circle(t):
    rpm = 15
    rps = rpm/60
    radius = 60
    desx = round(60*math.sin(t * rps * 6.28),1)
    desy = round(60*math.cos(t * rps * 6.28),1)
    return [desx,desy]

def teleports(t):
    global delaytime
    global desx
    global desy
    movedelay = 3
    edgemax = 80
    
    while (t > delaytime):
        desx = edgemax*(2*random.random()-1)
        desy = edgemax*(2*random.random()-1)        
        
        if(abs(desx)<edgemax and abs(desy)<edgemax):
            delaytime = delaytime + movedelay
            break
    
    return [desx,desy]
