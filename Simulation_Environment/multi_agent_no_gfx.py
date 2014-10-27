"""
Agents are non-inertial, massless, and do not collide with eachother
Agents can be set to either bounce on terrain collision, or stop
velocity is defined as pixels/second where the standard visual update is 100 steps/second
"""

import time

import pyglet
from pyglet.gl import *

import create
import environment
import agent_behavior
import agent_behavior_base

# Create and initialize environment
agent_behavior_function = agent_behavior_base.Agent_Behavior_Base()
environment = environment.Environment(agent_behavior_function, dt = .01, sim_time = 0, time_out = 10,
	hash_map_grid_size = 40, width = 800, height = 600, show_bins = False)
environment.create_perimeter_walls(location = 'inside', thickness = 5)
# Create terrain
#create.create_random_terrain(environment, count = 30, scale = 60)
# Create instances of agents
create.create_random_swarm(environment, count = 10, radius = 20, velocity_range = (150, 300))
#create.create_terrain_test_agents(environment)

time, survivor_count, total_agent_health, predator_health = environment.run_sim_no_gfx()

print("time = ", time)
print("survivor_count = ", survivor_count)
print("total_agent_health = ", total_agent_health)
print("predator_health = ", predator_health)