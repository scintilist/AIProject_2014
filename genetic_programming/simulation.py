from simulation_environment import create
from simulation_environment import environment

def simulator(input, output):
	for index, individual, sim_time_step, sim_time_out, sim_count in iter(input.get, 'STOP'):
	
		# Average over sim_count simulations
		fit_sum = 0
		survive_sum = 0
		for i in range(sim_count):
			# Create and initialize environment
			env = environment.Environment(individual.behavior, dt = sim_time_step, sim_time = 0, 
			time_out = sim_time_out, hash_map_grid_size = 40, width = 800, height = 600, 
			show_bins = False)
		
			env.create_perimeter_walls(location = 'inside', thickness = 5) # Walls
			create.create_test_terrain(env) # Terrain
			create.create_random_swarm(env, count = 10, radius = 20) # Swarm
			
			sim_time, survivor_count, total_agent_health, predator_health = env.run_sim_no_gfx()
			fitness = total_agent_health - predator_health
		
			fit_sum += fitness
			survive_sum += survivor_count

		result = (index, fit_sum/sim_count, survive_sum/sim_count)
		output.put(result)
	
