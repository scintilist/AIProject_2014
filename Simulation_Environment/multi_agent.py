import time

import pyglet
from pyglet.gl import *

import create
import environment
import event_handlers
import active_actions
import agent_behavior_base

# Set up graphical window
config = Config(double_buffer=True, depth_size=0, sample_buffers=1, samples=8)
window = pyglet.window.Window(width = 800, height = 600, config=config) # fullscreen = True
glClearColor(.8,.8,.8,1) # Set background color
glEnable(GL_BLEND) # Enable transparency / alpha blending
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

counter = pyglet.clock.ClockDisplay()

@window.event
def on_draw():
	window.clear()
	environment.draw()
	active_actions.draw()
	counter.draw()
	
def update(realtime_dt):
	if environment.update() == "terminate":
		pyglet.app.exit()
	active_actions.update()

# Baseline
agent_behavior_function = agent_behavior_base.behavior

# Create and initialize environment
environment = environment.Environment(agent_behavior_function, dt = .05, sim_time = 0, time_out = 100,
	hash_map_grid_size = 40, width = 800, height = 600, show_bins = False, run_max_speed = True)
environment.create_perimeter_walls(location = 'inside', thickness = 5) # Walls
create.create_test_terrain(environment) # Terrain
create.create_random_swarm(environment, count = 10, radius = 20) # Swarm

# Create active action manager
active_actions = active_actions.ActiveActions(environment)

pyglet.clock.schedule_interval(update, 1/120) # Update display 60 times per second

window.push_handlers(event_handlers.EventHandlers(environment, window, active_actions))
pyglet.app.run() # Run pyglet