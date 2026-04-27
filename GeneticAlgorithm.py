import main
import random
import numpy as np
import matplotlib.pyplot as plt

# ============== GA Parameters ==============
GENERATIONS = 6          # Number of generations to run
POP_SIZE = 15              # Population size
ELITE_COUNT = 5            # Number of top performers to carry to next generation
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
    fitness = main.runSystem(mem)
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
        scored = []
        for member in population:
            fitness = evaluate(member)
            scored.append((fitness, member))

        # Sort best to worst
        scored.sort(key=lambda x: x[0], reverse=True)

        # Store best fitness value for this generation
        best_fitness = scored[0][0]
        best_fitness_per_generation.append(best_fitness)
        
        # Calculate average fitness for this generation
        avg_fitness = sum(fitness for fitness, _ in scored) / len(scored)
        avg_fitness_per_generation.append(avg_fitness)
        
        # Calculate increase from last generation
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

    best_member = max(scored, key=lambda x: x[0])
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