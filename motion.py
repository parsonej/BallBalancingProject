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
def calculate_performance(error_history_x, error_history_y, dt):
    """
    Calculate performance metrics from error history
    Returns: score and detailed metrics
    """
    import numpy as np
    # MAE: Mean Absolute Error
    mae_x = np.mean(np.abs(error_history_x))
    mae_y = np.mean(np.abs(error_history_y))
    mae = (mae_x + mae_y) / 2
    # IAE: Integral of Absolute Error
    iae_x = np.sum(np.abs(error_history_x)) * dt
    iae_y = np.sum(np.abs(error_history_y)) * dt
    iae = (iae_x + iae_y) / 2
    # Max Error
    max_err_x = np.max(np.abs(error_history_x))
    max_err_y = np.max(np.abs(error_history_y))
    
    # Composite score (lower is better)
    # Weights can be adjusted based on importance of each metric
    # Increasing Max Error would penalize performances with large spikes,
    # MAE and IAE capture overall performance
    score = mae + 0.3*iae + 0.5*max(max_err_x, max_err_y)
    
    return score, {'MAE': mae, 'IAE': iae, 'MaxErr': max(max_err_x, max_err_y)}

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


def zero(t):
      
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
