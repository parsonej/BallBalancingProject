# PID Parameter Optimization using Bayesian Optimization
# Optimizes Kp (gain), Ki (trample), Kd (damper) for balanced performance across patterns
# Usage: python optimize_pid.py

import numpy as np
import time
import threading
from skopt import gp_minimize
from skopt.space import Real
from skopt.utils import use_named_args
import camera
import servo
import motion
import pickle
import json
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

OPTIMIZATION_CONFIG = {
    'n_calls': 50,                    # Number of Bayesian optimization trials
    'n_initial_points': 5,            # Random initial exploration
    'acq_func': 'EI',                 # Expected Improvement
    'n_jobs': 1,                      # Run sequentially (hardware constraint)
}

PATTERN_CONFIG = {
    'circle': {'cycles': 2, 'rpm': 6},
    'random_walk': {'cycles': 2, 'move_delay': 3},
    'step': {'num_steps': 2, 'step_size': 80},
}

METRICS_WEIGHTS = {
    'settling_time': 0.33,
    'steady_state_error': 0.33,
    'smoothness': 0.34,
}

# ============================================================================
# UTILITIES
# ============================================================================

class RollingBuffer:
    """Track velocity from position history"""
    def __init__(self, max_size=100):
        self.max_size = max_size
        self.buffer_x = [0]
        self.buffer_y = [0]
    
    def add(self, x, y):
        self.buffer_x.append(x)
        self.buffer_y.append(y)
        if len(self.buffer_x) > self.max_size:
            self.buffer_x.pop(0)
            self.buffer_y.pop(0)
    
    def get_velocity(self, dt):
        if len(self.buffer_x) < 2:
            return 0, 0
        vx = (self.buffer_x[-1] - self.buffer_x[-2]) / dt
        vy = (self.buffer_y[-1] - self.buffer_y[-2]) / dt
        return vx, vy
    
    def get_as_list(self):
        return list(zip(self.buffer_x, self.buffer_y))


def extract_state(ball_x, ball_y, ball_buffer, setpoint_x, setpoint_y, dt):
    """Build state vector for agent"""
    ball_vx, ball_vy = ball_buffer.get_velocity(dt)
    state = [ball_x, ball_y, ball_vx, ball_vy, setpoint_x, setpoint_y]
    return state


def calculate_error(ball_x, ball_y, setpoint_x, setpoint_y):
    """Calculate error magnitude"""
    return np.sqrt((ball_x - setpoint_x)**2 + (ball_y - setpoint_y)**2)


def pid_controller(error_history, kp, ki, kd):
    """PID controller with configurable gains"""
    if len(error_history) == 0:
        return 0
    
    # Current error
    delta_x = error_history[0]
    
    # Integral (sum of errors)
    area_dx = np.sum(error_history[0:1])  # For single step
    
    # Derivative (rate of change)
    derv_samples = min(3, len(error_history))
    if len(error_history) > 1:
        delta_v = np.mean(error_history[0:derv_samples-1] - error_history[1:derv_samples])
    else:
        delta_v = 0
    
    return kp * delta_x + ki * area_dx + kd * delta_v


# ============================================================================
# PERFORMANCE MEASUREMENT
# ============================================================================

def measure_performance_on_pattern(pattern_type, kp, ki, kd, duration_sec=15):
    """Test PID with given parameters on a pattern, return metrics"""
    
    rate = 30  # Hz
    dt = 1.0 / rate
    num_steps = int(duration_sec * rate)
    
    errors = []
    servo_angles_x = []
    servo_angles_y = []
    
    # Initialize
    ball_buffer = RollingBuffer()
    time_init = time.time()
    error_hist_x = [0, 0]
    error_hist_y = [0, 0]
    
    print(f"    Testing {pattern_type}...", end='', flush=True)
    
    for step in range(num_steps):
        step_start = time.time()
        elapsed = time.time() - time_init
        
        # Get setpoint from pattern
        if pattern_type == 'circle':
            des = motion.circle(elapsed)
        elif pattern_type == 'random_walk':
            des = motion.teleports(elapsed)
        else:  # step
            des = [80 if elapsed > 2 else 0, 0]  # Step change after 2s
        
        # Get ball position
        try:
            ball_x, ball_y = camera.getCoords()
        except:
            print(" ERROR getting camera feed")
            return None
        
        ball_buffer.add(ball_x, ball_y)
        
        # Calculate errors
        err_x = ball_x - des[0]
        err_y = ball_y - des[1]
        error_mag = calculate_error(ball_x, ball_y, des[0], des[1])
        errors.append(error_mag)
        
        # Update error histories
        error_hist_x = [err_x] + error_hist_x[:-1]
        error_hist_y = [err_y] + error_hist_y[:-1]
        
        # Compute control actions
        action_x = pid_controller(error_hist_x, kp, ki, kd)
        action_y = pid_controller(error_hist_y, kp, ki, kd)
        
        # Constrain and apply
        action_x = np.clip(action_x, -30, 30)
        action_y = np.clip(action_y, -30, 30)
        
        servo_angles_x.append(action_x)
        servo_angles_y.append(action_y)
        
        servo.setx(action_x)
        servo.sety(action_y)
        
        # Timing
        step_elapsed = time.time() - step_start
        if dt > step_elapsed:
            time.sleep(dt - step_elapsed)
    
    print(" Done.")
    return calculate_metrics(errors, servo_angles_x, servo_angles_y)


def calculate_metrics(errors, servo_x, servo_y):
    """Calculate performance metrics from trial"""
    errors = np.array(errors)
    servo_x = np.array(servo_x)
    servo_y = np.array(servo_y)
    
    # Settling time: when error stays below threshold
    threshold = 8  # pixels
    settling_idx = None
    for i in range(len(errors) - 30):
        if np.all(errors[i:i+30] < threshold):
            settling_idx = i
            break
    
    settling_time = (settling_idx if settling_idx else len(errors)) / 30.0  # Convert to seconds
    
    # Steady state error (last 10% of trial)
    steady_state = np.mean(errors[-int(len(errors)*0.1):])
    
    # Smoothness: mean absolute servo movement
    servo_changes = np.mean(np.abs(np.diff(servo_x))) + np.mean(np.abs(np.diff(servo_y)))
    smoothness = servo_changes / 2.0
    
    return {
        'settling_time': settling_time,
        'steady_state_error': steady_state,
        'smoothness': smoothness,
        'mean_error': np.mean(errors),
    }


# ============================================================================
# OBJECTIVE FUNCTION FOR BAYESIAN OPTIMIZATION
# ============================================================================

trial_count = 0

@use_named_args([
    Real(-0.5, -0.01, name='kp'),
    Real(-0.2, -0.01, name='ki'),
    Real(-10.0, -0.1, name='kd'),
])
def objective(kp, ki, kd):
    """Objective function: lower score is better"""
    global trial_count
    trial_count += 1
    
    print(f"\n{'='*70}")
    print(f"Trial {trial_count}: Kp={kp:.4f}, Ki={ki:.4f}, Kd={kd:.4f}")
    print(f"{'='*70}")
    
    pattern_scores = {}
    
    # Test on each pattern
    for pattern_name, config in PATTERN_CONFIG.items():
        if pattern_name == 'circle':
            duration = (config['cycles'] * 60) / (config['rpm'])  # cycles to seconds
        elif pattern_name == 'random_walk':
            duration = config['cycles'] * config['move_delay'] * 2
        else:  # step
            duration = 8  # fixed duration for step response
        
        metrics = measure_performance_on_pattern(pattern_name, kp, ki, kd, duration)
        
        if metrics is None:
            print(f"  FAILED on {pattern_name}")
            return 1000  # High penalty for failure
        
        # Normalize metrics (lower is better)
        # Settling time: 0-2 seconds is good
        settling_score = min(metrics['settling_time'] / 2.0, 1.0)
        
        # Steady state error: 0-15 pixels is good
        error_score = min(metrics['steady_state_error'] / 15.0, 1.0)
        
        # Smoothness: 0-5 degrees per step is good
        smooth_score = min(metrics['smoothness'] / 5.0, 1.0)
        
        pattern_scores[pattern_name] = {
            'settling': settling_score,
            'error': error_score,
            'smoothness': smooth_score,
            'weighted': (settling_score * METRICS_WEIGHTS['settling_time'] +
                        error_score * METRICS_WEIGHTS['steady_state_error'] +
                        smooth_score * METRICS_WEIGHTS['smoothness']),
        }
        
        print(f"  {pattern_name}:")
        print(f"    Settling: {metrics['settling_time']:.2f}s (score: {settling_score:.3f})")
        print(f"    Steady-State Error: {metrics['steady_state_error']:.2f}px (score: {error_score:.3f})")
        print(f"    Smoothness: {metrics['smoothness']:.3f}°/step (score: {smooth_score:.3f})")
        print(f"    Pattern Score: {pattern_scores[pattern_name]['weighted']:.3f}")
    
    # Balanced score across all patterns
    total_score = np.mean([p['weighted'] for p in pattern_scores.values()])
    
    print(f"\nBalanced Score: {total_score:.4f} (lower is better)")
    print(f"{'='*70}\n")
    
    return total_score


# ============================================================================
# OPTIMIZATION RUNNER
# ============================================================================

def run_optimization():
    """Execute Bayesian Optimization"""
    
    print("\n" + "="*70)
    print("PID PARAMETER OPTIMIZATION - BAYESIAN OPTIMIZATION")
    print("="*70)
    print(f"Optimizing: Kp (gain), Ki (trample), Kd (damper)")
    print(f"Patterns: {', '.join(PATTERN_CONFIG.keys())}")
    print(f"Trials: {OPTIMIZATION_CONFIG['n_calls']}")
    print(f"Metrics (balanced): settling_time, steady_state_error, smoothness")
    print("="*70 + "\n")
    
    # Define search space
    space = [
        Real(-0.5, -0.01, name='kp'),
        Real(-0.2, -0.01, name='ki'),
        Real(-10.0, -0.1, name='kd'),
    ]
    
    # Run Bayesian Optimization
    result = gp_minimize(
        func=objective,
        dimensions=space,
        n_calls=OPTIMIZATION_CONFIG['n_calls'],
        n_initial_points=OPTIMIZATION_CONFIG['n_initial_points'],
        acq_func=OPTIMIZATION_CONFIG['acq_func'],
        n_jobs=OPTIMIZATION_CONFIG['n_jobs'],
        verbose=0,
    )
    
    # Extract best parameters
    best_kp, best_ki, best_kd = result.x
    best_score = result.fun
    
    print("\n" + "="*70)
    print("OPTIMIZATION COMPLETE")
    print("="*70)
    print(f"Best Kp (gain):      {best_kp:.6f}")
    print(f"Best Ki (trample):   {best_ki:.6f}")
    print(f"Best Kd (damper):    {best_kd:.6f}")
    print(f"Best Score:          {best_score:.4f}")
    print("="*70 + "\n")
    
    # Save results
    save_optimization_results(result, best_kp, best_ki, best_kd, best_score)
    
    return best_kp, best_ki, best_kd


def save_optimization_results(result, best_kp, best_ki, best_kd, best_score):
    """Save optimization results to file"""
    
    timestamp = datetime.now().isoformat()
    results = {
        'timestamp': timestamp,
        'best_parameters': {
            'kp': float(best_kp),
            'ki': float(best_ki),
            'kd': float(best_kd),
        },
        'best_score': float(best_score),
        'n_trials': OPTIMIZATION_CONFIG['n_calls'],
        'all_trials': [
            {'parameters': {'kp': float(x[0]), 'ki': float(x[1]), 'kd': float(x[2])}, 'score': float(y)}
            for x, y in zip(result.x_iters, result.func_vals)
        ]
    }
    
    with open('optimization_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to optimization_results.json")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\nStarting PID optimization in 3 seconds...")
    print("Make sure hardware is powered and camera is running!")
    time.sleep(3)
    
    best_kp, best_ki, best_kd = run_optimization()
    
    print("\nUpdate controlla.py with:")
    print(f"  gain = {best_kp}")
    print(f"  trample = {best_ki}")
    print(f"  damper = {best_kd}")
