import json

from simulation_environment import create
from simulation_environment import environment
from genetic_programming import lgp
from simulation_environment import agent_behavior_base

def behavior_from_json(fn):
	with open(fn, 'r') as infile:
		pop_data = json.load(infile)
	max_fit = float('-inf')
	elite_individual = None
	for i, individual_data in enumerate(pop_data):
		if individual_data['_fit'] > max_fit:
			max_fit = individual_data['_fit']
			elite_individual = lgp.Behavior()
			elite_individual.s_lgp.prog = individual_data['s_lgp']
			elite_individual.a_lgp.prog = individual_data['a_lgp']
	return elite_individual.behavior

def main():
	# Get behavior
	behavior_function = behavior_from_json('test11_data.json')
	#behavior_function = agent_behavior_base.behavior
	
	sim_count = 30
	# Average over sim_count simulations
	fit_sum = 0
	survive_sum = 0
	for i in range(sim_count):
		# Create and initialize environment
		env = environment.Environment(behavior_function, dt = .1, sim_time = 0, 
		time_out = 50, hash_map_grid_size = 40, width = 800, height = 600, 
		show_bins = False)
	
		env.create_perimeter_walls(location = 'inside', thickness = 5) # Walls
		create.create_test_terrain(env) # Terrain
		create.create_random_swarm(env, count = 10, radius = 20) # Swarm
		
		sim_time, survivor_count, total_agent_health, predator_health = env.run_sim_no_gfx()
		fitness = total_agent_health - predator_health
	
		fit_sum += fitness
		survive_sum += survivor_count
		print('trial {:}/{:}, fitness = {:}'.format(i+1, sim_count, fitness), end='\r')

	print('\navg fitness over {:} simulations = {:.1f}'.format(sim_count, fit_sum / sim_count))
	
	
if __name__ == "__main__":
	main()