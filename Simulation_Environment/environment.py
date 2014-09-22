import time

import terrain
import swarm
import raster
import util

# Contains terrain and swarms, and is used to allow individual agents and blocks to access
# environmental information such as time

class Environment():
	def __init__(self, dt, sim_time, window, hash_map_grid_size, show_bins = False):
		self.show_bins = show_bins
	
		self.sim_time = sim_time
		self.dt = dt # Set the time step in seconds used for calculations (100fps = .01).
		self.update_time_out = .02 # Set update time out interval in seconds
		self.window = window # The window the environment is being displayed in
		self.terrain = terrain.Terrain(self, hash_map_grid_size)
		self.swarm = swarm.Swarm(self)
		
		self.active = [] # list of active objects that must be drawn
		self.undo = [] # stack of objects with undo methods to be called when ctrl-z is pressed
		self.redo = [] # stack of objects with redo methods to be called when ctrl-y is pressed
		
		self.mouse_x = -1
		self.mouse_y = -1
		self.paused = False # if True, do not update
		
		# get the real time of the simulation start (with added 1 second delay for loading the window)
		self.real_time_start = time.perf_counter() + 1
		
	def update(self):
		if not self.paused:
			calc_start_time = time.perf_counter() # Get calculation start time
			# Run update loop until simulation is caught up with real time or time out occurs
			while ( (time.perf_counter() - calc_start_time) < self.update_time_out and 
					self.sim_time < (time.perf_counter() - self.real_time_start) ):
				self.sim_time += self.dt
				self.swarm.update()
	
	def draw(self):
		self.terrain.draw()
		self.swarm.draw()
			
		if self.show_bins:
			# Get swarm bins
			swarm_bins = set(self.swarm.hash_map.keys())
			# Get terrain bins
			terrain_bins = set(self.terrain.hash_map.keys())
			# Draw terrain bins in dark grey
			raster.draw_bins(terrain_bins - swarm_bins, self.terrain.grid_size, color = (.3, .3, .3))
			# Draw swarm bins in green
			raster.draw_bins(swarm_bins - terrain_bins, self.terrain.grid_size, color = (.1,.9,.1))
			# Draw overlap in red
			raster.draw_bins(swarm_bins & terrain_bins, self.terrain.grid_size, color = (.9,.1,.1))
	
	def create_perimeter_walls(self, location = 'outside', thickness = 10):
		s = 1 if location == 'inside' else -1
		w = self.window.width
		h = self.window.height
		t = thickness
		self.terrain.add_block_by_points([(w,h), (0,h), (0,h-t*s), (w,h-t*s)]) # Top
		self.terrain.add_block_by_points([(0,0), (w,0), (w,t*s),   (0,t*s)  ]) # Bottom
		self.terrain.add_block_by_points([(w,0), (w,h), (w-t*s,h), (w-t*s,0)]) # Right
		self.terrain.add_block_by_points([(0,h), (0,0), (t*s,0),   (t*s,h)  ]) # Left
