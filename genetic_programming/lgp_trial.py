import random
import time

import json

from . import lgp
from . import simulation

# Runs genetic opimization cycle given the input parameters and saves the results to a log file
def run(task_queue = None, done_queue = None, result_path = None, config_name = None, 
		sim_time_out = 50, sim_time_step = .1, sim_count = 1, population = 20, generations = 100, 
		instr_count = 200, c_prob = .02, m_prob = .05):
	population_size = population
		
	# Open log file
	log_fn = '{:}/{:}_log.txt'.format(result_path, config_name)
	with open(log_fn, 'w') as logfile:
		# Write header to log file
		logfile.write('gen, peakF, survive, avgF, run_time\n')
	print('Config = {:}'.format(config_name))
	print('gen, peakF, survive, avgF, run_time')

	# Create random population
	population, total_norm_fit, elite_individual = random_population(population_size, instr_count)

	# Evolve for 'generations'
	for gen in range(generations):
		gen_start_time = time.perf_counter()

		# Generate a new population of agent behaviors using mutation and crossover
		new_population = []
		new_population.append(elite_individual)
		for i in range(1, population_size):
			# Pick 2 parents based on fitness proportionate selection
			parents = []
			for i in range(2):
				r = random.uniform(0, total_norm_fit)
				upto = 0
				for individual in population:
					upto += individual.norm_fitness
					if upto >= r:
						parents.append(individual)
						break
			# Perform crossover on parents to form new individual, then mutate
			new_individual = lgp.Behavior()
			new_individual.crossover(parent = parents, c_prob = c_prob)
			new_individual.mutate(m_prob = m_prob * i / population_size)
			new_population.append(new_individual)
			
		population = new_population
		
		# Simulate all individuals
		
		# Put all simulation jobs on the task_queue
		for index, individual in enumerate(population):
			task = (index, individual, sim_time_step, sim_time_out, sim_count)
			task_queue.put(task)
		
		# Save output from done_queue to individuals
		for i in range(population_size):
			index, fitness, survivor_count = done_queue.get()
			population[index].fitness = fitness
			population[index].survivor_count = survivor_count
			
		# Find the elite individual, and range of fitness values
		elite_individual = None
		max_fitness = float('-inf')
		min_fitness = float('inf')
		total_fitness = 0
		for individual in population:
			total_fitness += individual.fitness
			if individual.fitness > max_fitness:
				elite_individual = individual
				max_fitness = individual.fitness
			min_fitness = min(min_fitness, individual.fitness)

		# Generate normalized fitness for crossover
		total_norm_fit = 0
		for individual in population:
			individual.norm_fitness = individual.fitness - min_fitness + 1
			total_norm_fit += individual.norm_fitness
		
		gen_end_time = time.perf_counter()
		
		# Save population to json file
		save_population(population, fn = '{:}/{:}_data.json'.format(result_path, config_name))
		
		# Add generation data to log file and print
		avg_fit = total_fitness / population_size
		run_time = gen_end_time - gen_start_time
		survive = elite_individual.survivor_count
		log_string = '{:>3d}, {:>5.0f}, {:>4.1f}, {:>7.1f}, {:.2f}' \
					 .format(gen, max_fitness, survive, avg_fit, run_time)
		with open(log_fn, 'a') as logfile:
			logfile.write('{:}\n'.format(log_string))
		print(log_string)
	
	
# Save population data to a json file, sorted from most to least fit
def save_population(population = None, fn = 'population_data.json'):
	pop_data = []
	for individual in population:
		individual_data = {'_fit': individual.fitness,
						   's_lgp': individual.s_lgp.prog,
						   'a_lgp': individual.a_lgp.prog}	
		pop_data.append(individual_data)
	pop_data = sorted(pop_data, key=lambda dat: dat['_fit'], reverse=True)
	with open(fn, 'w') as outfile:
		json.dump(pop_data, outfile, indent = 4, sort_keys = True)

# Load population data from a json file
def load_population(fn = 'population_data.json'):
	with open(fn, 'r') as infile:
		pop_data = json.load(infile)
		
	population = []
	for individual_data in pop_data:
		new_individual = lgp.Behavior()
		new_individual.s_lgp.prog = individual_data['s_lgp']
		new_individual.a_lgp.prog = individual_data['a_lgp']
		new_individual.norm_fitness = 1
		population.append(new_individual)
	elite_individual = population[0]
	total_fitness = len(pop_data)
	return population, total_fitness, elite_individual
	
# Generate random initial population
def random_population(population_size, instr_count):
	population = []
	for i in range(population_size):
		new_individual = lgp.Behavior()
		new_individual.randomize(instr_count)
		new_individual.norm_fitness = 1
		population.append(new_individual)
	elite_individual = population[0]
	total_fitness = population_size
	return population, total_fitness, elite_individual