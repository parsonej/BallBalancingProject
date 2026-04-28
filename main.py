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
import random
import matplotlib.pyplot as plt

# VARIABLES
runtime = 17 # [s] time before ending program
rate = 35 # [hz] max rate at which servo positions are set
dt = 1/rate # needed time between cycles to hit rate
maxHistory = 100 # number of points captured for vel/int stuff
timeinit = time.time()

# SETUP
def update_motion_DX():
	pos = camera.getCoords()
	#des = motion.zero(time.time()-timeinit)
	#desX = des[0]
	#desY = des[1]
	desX = 0 #for initial testing generations 
	desY = 0 
	posX = pos[0]
	posY = pos[1]
	DX = round(posX-desX,1)
	DY = round(posY-desY,1)
	return pos, DX, DY

def runSystem(genome):
	#if any(np.isnan(v) for v in genome):
		#print(f"NaN Genome detected: {genome}")
	# Extract genome from member: [gain, accel, damper, dervSamples, intSamples]
	controlla.configure_pid(genome[0], genome[1], genome[2], genome[3], genome[4])
	
	timeout = time.time() + runtime
	all_errors_x = []
	all_errors_y = []
	timestamps = []
	step = 0
	pos, histX, histY = update_motion_DX()
	histDX = np.array([])
	histDY = np.array([])
	while True: 
		tstart = time.time()
		# get current position, desired position, and error history
		pos, histX, histY = update_motion_DX()
		

		#Track error history for performance evaluation
		all_errors_x.append(abs(histX))
		all_errors_y.append(abs(histY))
		timestamps.append(time.time() - timeinit)

		#If error history is too long, drop oldest point.
		if(len(histDX) > maxHistory):
			histDX = np.concatenate(([histX], histDX[0:-1]))
			histDY = np.concatenate(([histY], histDY[0:-1]))
		#If error history is not full, push the current error.	
		else:
			histDX = np.concatenate(([histX], histDX))
			histDY = np.concatenate(([histY], histDY))	
			
			
		
		
		#Set servo angles based on control algorithm output
		#print("HistDX Length: ", len(histDX))
		#print("Current histDX: ", histDX)
		servo.setx(controlla.PID(histDX))
		servo.sety(controlla.PID(histDY))
		
		camera.dispframe(0,0) # CHange later----------------------------------------------------------------------------
		Dt = time.time()-tstart # actual time per cycle
		#print("pos:",str(pos[0]),",",str(pos[1]),"  delta:",str(histX),",",str(histY),"  dt:",round(Dt,3)," rtime",round(time.time()-timeinit,2))
		step += 1
		if time.time() > timeout:
			break
		if (dt > Dt):
			time.sleep(dt - Dt)	
	score, metrics = motion.calculate_performance(all_errors_x, all_errors_y, dt)
	print(f"Performance Score: {score:.2f}")
	print(f"Metrics: {metrics}")
	controlla.plot_errors(timestamps, all_errors_x, all_errors_y)
	servo.setx(0)
	servo.sety(0)
	return score




# ============== GA Parameters ==============
GENERATIONS = 3          # Number of generations to run
POP_SIZE = 5              # Population size
ELITE_COUNT = 2            # Number of top performers to carry to next generation
MUTATION_RATE = 0.1        # Probability of mutation for each gene
MUTATION_AMOUNT = 0.2      # Standard deviation of mutation
CROSSOVER_TYPE = "uniform" # Type of crossover: "uniform" or "single_point"
# ===========================================

# ============== PID Genome Parameters ==============
# Default values
DEFAULT_GAIN = -0.05
DEFAULT_ACCEL = -0.015
DEFAULT_DAMPER = -1.5
DEFAULT_DERV_SAMPLES = 12
DEFAULT_INT_SAMPLES = 50

# Ranges for initialization
GAIN_RANGE = (-0.2, 0.0)
ACCEL_RANGE = (-0.05, 0.0)
DAMPER_RANGE = (-3.0, 0.0)
DERV_SAMPLES_RANGE = (5, 20)
INT_SAMPLES_RANGE = (20, 100)
# ==================================================

class member:
	def __init__(self, params):
		self.params = params
	def get_genome(self):
		return self.params

def evaluate(mem):
	# Run mechanical system, return fitness score
	fitness = runSystem(mem)
	return fitness

def initialize_population():
	"""Create initial population with random genome values within specified ranges"""
	population = []
    
	for _ in range(POP_SIZE):
		# Create genome: [gain, accel, damper, dervSamples, intSamples]
		genome = [
			random.uniform(GAIN_RANGE[0], GAIN_RANGE[1]),
			random.uniform(ACCEL_RANGE[0], ACCEL_RANGE[1]),
			random.uniform(DAMPER_RANGE[0], DAMPER_RANGE[1]),
			random.randint(DERV_SAMPLES_RANGE[0], DERV_SAMPLES_RANGE[1]),
			random.randint(INT_SAMPLES_RANGE[0], INT_SAMPLES_RANGE[1])
		]
		population.append(member(genome))
    
	return population

def crossover(a, b):
	"""Create offspring by blending genomes of two parents using uniform crossover"""
	parent_a_genome = a.get_genome()
	parent_b_genome = b.get_genome()
    
	# Create child genome by randomly selecting each gene from either parent
	child_genome = []
	for i in range(len(parent_a_genome)):
		if random.random() < 0.5:
			child_genome.append(parent_a_genome[i])
		else:
			child_genome.append(parent_b_genome[i])
    
    
	return member(child_genome)

def mutate(mem):
	"""Randomly perturb genes in a member's genome"""
	genome = mem.get_genome()
	mutated_genome = genome.copy()
	# Mutate gain, accel, damper (continuous values)
	if random.random() < MUTATION_RATE:
		mutated_genome[0] = float(np.clip(
			mutated_genome[0] + np.random.normal(0, MUTATION_AMOUNT),
			GAIN_RANGE[0], GAIN_RANGE[1]
		))
	if random.random() < MUTATION_RATE:
		mutated_genome[1] = float(np.clip(
			mutated_genome[1] + np.random.normal(0, MUTATION_AMOUNT),
			ACCEL_RANGE[0], ACCEL_RANGE[1]
		))
	if random.random() < MUTATION_RATE:
		mutated_genome[2] = float(np.clip(
			mutated_genome[2] + np.random.normal(0, MUTATION_AMOUNT),
			DAMPER_RANGE[0], DAMPER_RANGE[1]
		))
	# Mutate dervSamples, intSamples (integer values)
	if random.random() < MUTATION_RATE:
		mutated_genome[3] = int(np.clip(
			mutated_genome[3] + random.randint(-2, 2),
			DERV_SAMPLES_RANGE[0], DERV_SAMPLES_RANGE[1]
		))
	if random.random() < MUTATION_RATE:
		mutated_genome[4] = int(np.clip(
			mutated_genome[4] + random.randint(-5, 5),
			INT_SAMPLES_RANGE[0], INT_SAMPLES_RANGE[1]
		))
	return member(mutated_genome)

def run_ga():
	population = initialize_population()
	best_fitness_per_generation = []
	avg_fitness_per_generation = []
	for gen in range(GENERATIONS):
		print(f"Generation {gen}")
		# Evaluate every member
		num = 1
		scored = []
		for mem in population:
			print("Member#: ", num)
			print("Genome: ", mem.get_genome())
			fitness = evaluate(mem.get_genome())
			scored.append((fitness, mem))
			num += 1
		#Sort best to worst
		scored.sort(key=lambda x: x[0], reverse=False)
		#Store best fitness value for this generation
		best_fitness = scored[0][0]
		best_fitness_per_generation.append(best_fitness)
        
		#Calculate average fitness for this generation
		avg_fitness = sum(fitness for fitness, _ in scored) / len(scored)
		avg_fitness_per_generation.append(avg_fitness)
        #Calculate increase from last generation
		if gen > 0:
			avg_increase = avg_fitness - avg_fitness_per_generation[gen - 1]
		else:
			avg_increase = 0
        
		# Print statistics
		print(f"  Best fitness: {best_fitness}")
		print(f"  Average fitness: {avg_fitness:.4f}")
		print(f"  Average Delta: {avg_increase:.4f}")

		# Select top half
		top_half = [m for _, m in scored[:len(scored) // 2]]

		# Build next generation
		next_gen = []

		# Elites carry over
		next_gen.extend(top_half[:ELITE_COUNT])
		# Fill rest with children
		while len(next_gen) < POP_SIZE:
			a, b = random.sample(top_half, 2)
			next_gen.append(mutate(crossover(a, b)))

		population = next_gen

	best_member_score, best_member = min(scored, key=lambda x: x[0])
	print("\n" + "="*60)
	print("EVOLUTION COMPLETE - BEST GENOME FOUND:")
	print("="*60)
	print(f"Score (Golf Rules): {best_member_score:.4f}")
	print(f"Genome [Gain, Accel, Damper, DervSamples, IntSamples]:")
	genome = best_member.get_genome()
	print(f"  Gain: {genome[0]:.6f}")
	print(f"  Accel: {genome[1]:.6f}")
	print(f"  Damper: {genome[2]:.6f}")
	print(f"  DervSamples: {genome[3]}")
	print(f"  IntSamples: {genome[4]}")
	print("="*60 + "\n")
	return best_member, best_fitness_per_generation, avg_fitness_per_generation

def plot_fitness(best_fitness_per_generation, avg_fitness_per_generation, save_path="fitness_plot.png"):
	"""Plot best and average fitness over generations"""
	generations = range(len(best_fitness_per_generation))
	
	fig, ax = plt.subplots(figsize=(10, 6))
	
	ax.plot(generations, best_fitness_per_generation, color='steelblue', label='Best Fitness', marker='o')
	ax.plot(generations, avg_fitness_per_generation, color='coral', label='Average Fitness', marker='s')
	ax.set_xlabel("Generation")
	ax.set_ylabel("Fitness")
	ax.set_title("Genetic Algorithm Fitness Over Generations")
	ax.legend()
	ax.grid(True)
	
	plt.tight_layout()
	plt.savefig(save_path)
	plt.close()
	print(f"Plot saved to {save_path}")

def test_popinit():
	pop = initialize_population()
	for member in pop:
		print(member.get_genome())
#test_popinit()

def test_crossover():
	#create population and crossover first two members
	pop = initialize_population()
	parent_a = pop[0]
	parent_b = pop[1]
	child = crossover(parent_a, parent_b)
	print("Parent A:", parent_a.get_genome())
	print("Parent B:", parent_b.get_genome())
	print("Child:", child.get_genome())
# test_crossover()

def test_mutation():
	#create population and mutate first member
	pop = initialize_population()
	member_to_mutate = pop[0]
	mutated_member = mutate(member_to_mutate)
	print("Original Member:", member_to_mutate.get_genome())
	print("Mutated Member:", mutated_member.get_genome())
#test_mutation()
run_ga()

#gain = -.05
#accel = -.005
#damper = -0.7
#dervSamples = 3
#intSamples = 50
#runSystem([gain, accel, damper, dervSamples, intSamples])
camera.turnoff()
servo.turnoff()
time.sleep(3)
