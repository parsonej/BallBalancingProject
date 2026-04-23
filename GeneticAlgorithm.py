def evaluate(member):
    # Run mechanical system, return fitness score
    pass

def initialize_population():
    pass

def crossover(a, b):
    pass

def mutate(member):
    pass

def run_ga():
    population = initialize_population()

    for gen in range(GENERATIONS):
        print(f"Generation {gen}")

        # Evaluate every member
        scored = []
        for member in population:
            fitness = evaluate(member)
            scored.append((fitness, member))

        # Sort best to worst
        scored.sort(key=lambda x: x[0], reverse=True)

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

    return max(scored, key=lambda x: x[0])