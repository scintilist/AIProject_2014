import math

import pyglet

from . import util
from . import raster
from . import agent

class Predator():

	def __init__(self,  environment, radius = 32, position = (0,0), speed = 10, direction = 0):
		self.initial_health = 2000
		self.dps = 50
		self.view_range = 200
		
		self.health = self.initial_health
		self.speed = speed
		self.dir = direction # Radians, 0-2*pi
		self.ang_v = 0 # Radians / second
		self.radius = radius
		self.x, self.y = position
		
		self.is_kill = False  # Set to True to cause the predator to be removed
		
		self.distance_travelled = 0 # Tracks the total distance the agent has travelled over its life
		self.environment = environment
		self.terrain = environment.terrain
		self.grid_size = self.terrain.grid_size
		self.hash_map = {}
		
		bins = raster.circle_bins((self.x, self.y), self.radius, self.grid_size)
		self.put_in_map(bins)
		
		self.agent_in_view = False # Used for debug
	
	def behavior(self):
		# Inputs
			# self.terrain_distance[0:2], self.agent_distance, self.agent_angle, self.nearby_agent_count, self.health
		# Outputs
			# self.speed, self.ang_v
		#print(self.nearby_agent_count)
		
		self.speed = 100
		if(self.nearby_agent_count==0):
			if (self.terrain_distance[2] == self.terrain_distance[0] and self.terrain_distance[2] == 200):
				self.ang_v = 0
			elif (self.terrain_distance[2] >= self.terrain_distance[0] and self.terrain_distance[2] == 200):
				self.ang_v = -1
			elif (self.terrain_distance[2] <= self.terrain_distance[0] and self.terrain_distance[0] == 200):
				self.ang_v = -1
			elif (self.terrain_distance[2] <= self.terrain_distance[0] and self.terrain_distance[0] < 200):
				self.ang_v = -1
			elif (self.terrain_distance[2] >= self.terrain_distance[0] and self.terrain_distance[0] > 200):
				self.ang_v = -1
			else:
				self.ang_v = -1
		elif(self.nearby_agent_count>0 and self.nearby_agent_count<3):
			if(self.agent_angle>0):
				self.ang_v = 5
			elif(self.agent_angle<0):
				self.ang_v = -5
			else:
				self.ang_v = 0
				
			if(self.agent_distance < self.radius):
				self.speed = 0
		else:
			if(-2.8 < self.agent_angle < 2.8):
				if(self.agent_angle > 0):
					self.ang_v = -5
				else:
					self.ang_v = 5
			else:
				self.ang_v = 0
	
	def update(self):
		self.get_inputs()
		self.attack()
		
	    # Run predator behavior
		self.behavior()
	
		# Update direction with angular velocity
		self.dir += self.ang_v * self.environment.dt
		
		# Generate x and y velocity from speed and direction
		self.vx = self.speed * math.cos(self.dir)
		self.vy = self.speed * math.sin(self.dir)
	
		# Save current positions to determine if movement occurred
		self.px = self.x
		self.py = self.y
		
		# Calculate final location after move
		dx = self.vx * self.environment.dt
		dy = self.vy * self.environment.dt
		moves = 0
		while (dx != 0 or dy != 0) and moves < 4:
			dx, dy = self.terrain_collision_handler(dx, dy)
			moves += 1
		
		# Update hash map for predator
		self.reindex()
		
		# Mark predator for removal if its health drops to 0 or less
		if self.health <= 0:
			self.is_kill = True
	
	def reindex(self):
		self.hash_map = {}
		bins = raster.circle_bins((self.x, self.y), self.radius, self.grid_size)
		self.put_in_map(bins)
			
	def get_inputs(self):
		# Cast ray of length view_range forward, and 45 degrees to each side, return list of collision distances
		self.terrain_distance = self.get_terrain_input(self.view_range)
		# Get distance and angle to nearest agent, and count of nearby agents
		self.agent_distance, self.agent_angle, self.nearby_agent_count, self.closest_agent = self.get_agent_input(self.view_range)
	
	def get_agent_input(self, view_range = 200):
		nearby_agent_count = 0
		dist = view_range
		closest_agent = False
		for agent in self.environment.swarm.agents:
			new_dist = util.distance((self.x, self.y),(agent.x, agent.y))
			if new_dist < view_range  and self.terrain.line_of_sight((self.x, self.y), (agent.x, agent.y)):
				nearby_agent_count += 1
				if new_dist < dist:
					dist = new_dist
					closest_agent = agent
		if closest_agent:
			abs_angle = math.atan2(closest_agent.y - self.y, closest_agent.x - self.x)
			rel_angle = (math.pi + abs_angle - self.dir) % (2*math.pi) - math.pi
			self.agent_in_view = True
			return dist, rel_angle, nearby_agent_count, closest_agent
		else:
			self.agent_in_view = False
			return view_range, 0, nearby_agent_count, closest_agent
		
	def get_terrain_input(self, view_range = 200):
		terrain_distance = []
		for i in range(0,3):
			angle = self.dir + (i-1) * math.pi/4 # Left 45deg, Center, Right 45deg
			# Line from self.x,self.y to view_x, view_y
			view_x = self.x + view_range * math.cos(angle)
			view_y = self.y + view_range * math.sin(angle)
			# Get set of terrain hash map bins crossed by line
			bins = raster.line_bins(a = (self.x, self.y), b = (view_x, view_y), 
				bin_size = self.terrain.grid_size)
			# Get set of blocks contained in the set of bins
			block_set = self.terrain.check_for_blocks(bins)
			# Get distance to closest intersection
			dist = view_range
			for block in block_set:
				for edge in block.edges:
					intersection = util.intersect((self.x, self.y), (view_x, view_y), edge[0], edge[1])
					if intersection:
						new_dist = util.distance((self.x, self.y), intersection)
						dist = min(dist, new_dist)
			terrain_distance.append(dist)
		return terrain_distance
		
	def attack(self):
		if self.closest_agent:
			if self.agent_distance < self.radius + self.closest_agent.radius :
				self.closest_agent.health -= self.environment.dt * self.dps

	def put_in_map(self, bins):
		# Put agent in bins
		for bin in bins:
			if bin not in self.hash_map:
				self.hash_map[bin] = set()
			self.hash_map[bin].add(self)

	def terrain_collision_handler(self, dx, dy):
		# Add velocity to get next position (assuming no collision)
		self.nx = self.x + dx
		self.ny = self.y + dy

		# Get set of terrain hash map bins crossed by circle
		bins = raster.circle_path_bins(a = (self.x, self.y), b = (self.nx, self.ny), 
			r = self.radius, bin_size = self.terrain.grid_size)
		# Get set of blocks contained in the set of bins
		block_set = self.terrain.check_for_blocks(bins)
		
		# Check for intersection of move vector with block collision boundary
		intersection_locations = []
		for block in block_set:
			block_intersect = block.circle_intersect(r = self.radius,
															a = (self.x, self.y),
															b = (self.nx, self.ny))
			# If there was an intersection, add the points and the block to the list
			if block_intersect:
				# Block, interestion location, surface normal
				intersection_locations.append((block, block_intersect[0], block_intersect[1]))

		start_inside_block = False
		if intersection_locations:
			# Find the collision point as the intersection closest to the start position
			dist = float('inf')
			for block_data in intersection_locations:
				new_dist = util.distance((self.x, self.y), block_data[1])
				if new_dist < dist:
					dist = new_dist # Distance from start position to collision location
					collided_block = block_data[0] # Block that caused collision
					collision_location = block_data[1] # Location where collision occured
					surface_normal = block_data[2] # Surface normal at collision point
			# Determine whether the start was inside the colliided block
			if collided_block.point_distance((self.x, self.y)) < self.radius:
				start_inside_block = True
			else: # Handle collision
				start_inside_block = False
				# Stop at intersection, then back off 1/1000 of a pixel
				full_move_dist = math.sqrt(dx**2 + dy**2)
				off_x = -.001 * dx / full_move_dist
				off_y = -.001 * dy / full_move_dist
				nx = collision_location[0] + off_x
				ny = collision_location[1] + off_y
				self.distance_travelled += util.distance((self.x, self.y), (nx, ny))
				self.x = nx
				self.y = ny
				# New move remaining for sliding behavior
				sn_ux = surface_normal[0]
				sn_uy = surface_normal[1]
				sn_dir = math.atan2(-sn_uy, -sn_ux)
				collide_angle = (self.dir - sn_dir + math.pi) % (math.pi*2) - math.pi
				if collide_angle > 0: # Add 90 degrees to surface normal
					rv_ux = sn_uy
					rv_uy = -sn_ux
				else:	# Subtract 90 degrees from surface normal
					rv_ux = -sn_uy
					rv_uy = sn_ux
				# Calculate remaining move vectors
				rm_dist = util.distance((self.x, self.y),(self.nx, self.ny))
				rm_x = rv_ux * rm_dist
				rm_y = rv_uy * rm_dist	
				return (rm_x, rm_y) # Move incomplete, return remaining move vector

		# If there was no intersection, or the start was inside the block				
		if start_inside_block or not intersection_locations:
			# If an intersecting block has been identified, only search that block, otherwise search all
			blocks_to_test = block_set
			if start_inside_block:
				blocks_to_test = [collided_block]	
			# Assume the move is allowed, until shown otherwise
			move_allowed = True
			for block in blocks_to_test:
				start_dist = block.point_distance((self.x, self.y))
				if start_dist <= self.radius:
					end_dist = block.point_distance((self.nx, self.ny))
					# out from block allowed, into block not
					move_allowed = end_dist >= start_dist
					break
			if move_allowed:
				self.distance_travelled += util.distance((self.x, self.y), (self.nx, self.ny))
				self.x = self.nx
				self.y = self.ny
			else:
				self.dir += math.pi
		return (0,0) # Move complete, no remaining dx or dy
					
	def draw(self, color = (.2,.2,1,1)):
		
		# Draw field of view
		#pyglet.gl.glColor4f(0,0,0,.5)
		#pyglet.gl.glLineWidth(3)
		#pyglet.graphics.draw(4, pyglet.gl.GL_LINES,  ('v2f', (
		#	self.x, self.y, 
		#	self.x + self.view_range * math.cos(self.dir + math.pi/4), self.y + self.view_range * math.sin(self.dir + math.pi/4),
		#	self.x, self.y, 
		#	self.x + self.view_range * math.cos(self.dir - math.pi/4), self.y + self.view_range * math.sin(self.dir - math.pi/4)
		#	)))
		
		# Draw the predator body circle
		pyglet.gl.glPointSize(self.radius*2)
		pyglet.gl.glColor4f(*color)
		pyglet.graphics.draw(1, pyglet.gl.GL_POINTS, ('v2f', (self.x, self.y) ) )
		
		# Draw the predator agent sighted ring
		if self.agent_in_view:
			pyglet.gl.glPointSize(self.radius*2)
			pyglet.gl.glColor4f(.8,0,0,1)
			pyglet.graphics.draw(1, pyglet.gl.GL_POINTS, ('v2f', (self.x, self.y) ) )
		
		# Draw the predator dirction mark, from center to edge
		pyglet.gl.glColor4f(0,0,0,1)
		pyglet.gl.glLineWidth(3)
		pyglet.graphics.draw(2, pyglet.gl.GL_LINES,  ('v2f', 
			(self.x, self.y, 
			self.x + self.radius * math.cos(self.dir), self.y + self.radius * math.sin(self.dir)) ) )
			
		# Draw the predator dirction mark, from center to edge
		pyglet.gl.glColor4f(0,0,0,1)
		pyglet.gl.glLineWidth(3)
		pyglet.graphics.draw(2, pyglet.gl.GL_LINES,  ('v2f', 
			(self.x, self.y, 
			self.x + self.radius * math.cos(self.dir), self.y + self.radius * math.sin(self.dir)) ) )
		
		# Draw the predator health circle
		pyglet.gl.glPointSize(self.radius)
		v = self.health / self.initial_health
		pyglet.gl.glColor4f(v,v,v,1)
		pyglet.graphics.draw(1, pyglet.gl.GL_POINTS, ('v2f', (self.x, self.y) ) )
