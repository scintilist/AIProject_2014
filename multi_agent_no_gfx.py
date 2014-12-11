from simulation_environment import create
from simulation_environment import environment
from simulation_environment import agent_behavior_base

# Baseline
agent_behavior_function = agent_behavior_base.behavior

# Create and initialize environment
environment = environment.Environment(agent_behavior_function, dt = .1, sim_time = 0, time_out = 150,
	hash_map_grid_size = 40, width = 800, height = 600, show_bins = False)
environment.create_perimeter_walls(location = 'inside', thickness = 5) # Walls
create.create_test_terrain(environment) # Terrain
create.create_random_swarm(environment, count = 10, radius = 20) # Swarm

time, survivor_count, total_agent_health, predator_health = environment.run_sim_no_gfx()

print("time = ", time)
print("survivor_count = ", survivor_count)
print("total_agent_health = ", total_agent_health)
print("predator_health = ", predator_health)