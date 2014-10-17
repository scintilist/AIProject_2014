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
import event_handlers
import active_actions

# Set up graphical window
config = Config(double_buffer=True, depth_size=0, sample_buffers=1, samples=8)
window = pyglet.window.Window(fullscreen=True, config=config) 
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
	environment.update()
	active_actions.update()

# Create and initialize environment
environment = environment.Environment(dt = .015, sim_time = 0, window = window, 
										hash_map_grid_size = 40, show_bins = False)
environment.create_perimeter_walls(location = 'inside', thickness = 15)
# Create terrain
create.create_terrain(environment, count = 30, scale = 60)
# Create instances of agents
create.create_swarm(environment, count = 20, radius = 20, velocity_range = (150, 300))

create.create_predator(environment, radius = 50, velocity_range = (150, 300))

# Create active action manager
active_actions = active_actions.ActiveActions(environment)

pyglet.clock.schedule_interval(update, 1/120) # Update display 60 times per second

window.push_handlers(event_handlers.EventHandlers(environment, active_actions))
pyglet.app.run() # Run pyglet