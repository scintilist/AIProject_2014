from simulation_environment import create
from simulation_environment import environment
import agent_behavior


population_size = 2
generations = 2

# Create the initial population of agent behaviors
population = []

for i in range(population_size):
	new_behavior = agent_behavior.Behavior()
	new_behavior.random_trees()
	population.append(new_behavior)

# Evolve for 'generations'
for gen in range(generations): 
	
	# Simulate all behavior functions and store the fitness for each
	for individual in population:
	
		# Agent behavior function
		agent_behavior_function = individual.behavior

		# Create and initialize environment
		env = environment.Environment(agent_behavior_function, dt = .1, sim_time = 0, time_out = 30,
			hash_map_grid_size = 40, width = 800, height = 600, show_bins = False)
		env.create_perimeter_walls(location = 'inside', thickness = 5) # Walls
		create.create_test_terrain(env) # Terrain
		create.create_random_swarm(env, count = 10, radius = 20) # Swarm

		time, survivor_count, total_agent_health, predator_health = env.run_sim_no_gfx()

		individual.fitness = total_agent_health - predator_health
		
	# Print the highest fitness for the current generation
	peak_fitness = float('-inf')
	for individual in population:
		if individual.fitness > peak_fitness:
			peak_fitness = individual.fitness
	print("gen", gen, "peak fitness = ", peak_fitness)

	# Generate a new population of agent behaviors using mutation and crossover
	new_population = []
	for i in range(population_size):
		new_behavior = agent_behavior.Behavior()
		new_behavior.random_trees()
		new_population.append(new_behavior)
		
	population = new_population
	
	



"""
-each generation will consist of instances for the agent_behavior class
-for evolution, trees will be extracted from the instance, recombined and used to generate new instances


"""