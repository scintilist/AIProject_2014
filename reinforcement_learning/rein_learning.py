from simulation_environment import create
from simulation_environment import environment
import agent_behavior

# Agent behavior function
individual = agent_behavior.Behavior()
agent_behavior_function = individual.behavior;
f = open('output.txt', 'w')

i=0;
for x in range(0, 100000):
	# Create and initialize environment
	env = environment.Environment(agent_behavior_function, dt = .1, sim_time = 0, time_out = 50,
		hash_map_grid_size = 40, width = 800, height = 600, show_bins = False)
	env.create_perimeter_walls(location = 'inside', thickness = 5) # Walls
	create.create_test_terrain(env) # Terrain
	create.create_random_swarm(env, count = 10, radius = 20) # Swarm

	time, survivor_count, total_agent_health, predator_health = env.run_sim_no_gfx()

	fitness = total_agent_health - predator_health + 1000;
	print(fitness)
	s=str(x)
	f.write(s)
	f.write(',')
	s=str(fitness)
	f.write(s)
	f.write('\r\n')
	if (x % 1000)==0:
		Q = open('Q.txt', 'w')
		s=str(individual.Q)
		Q.write(s)
		Q.close()
	
f.close()
f = open('Q.txt', 'w')
s=str(individual.Q)
f.write(s)
f.close()

