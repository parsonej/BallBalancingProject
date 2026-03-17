# MOTION PROFILES
# returns des as a fn of time :)
import math
import time
import random

delaytime = 0
desx = 0
desy = 0

def test(t):
    return 0

def manual(t):
      
    return 0

def circle(t):
    rpm = 6
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
