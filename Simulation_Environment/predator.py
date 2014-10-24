import math

import pyglet

import util
import raster
import agent

class Predator():

	def __init__(self,  environment, radius = 32, position = (0,0), speed = 10, direction = 0):
		self.health = 2000
		
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
		elif(self.nearby_agent_count>0 and self.nearby_agent_count<5):
			if(self.agent_angle>0):
				self.ang_v = 5
			elif(self.agent_angle<0):
				self.ang_v = -5
			else:
				self.ang_v = 0
				
			if(self.agent_distance < self.radius):
				self.speed = 0
		else:
			if(self.agent_angle<3.14):
				self.ang_v = -5
			elif(self.agent_angle>-3.14):
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
		self.terrain_collision_handler(dx, dy)	
		
		# Update hash map for predator
		self.hash_map = {}
		bins = raster.circle_bins((self.x, self.y), self.radius, self.grid_size)
		self.put_in_map(bins)
		
		# Mark predator for removal if its health drops to 0 or less
		if self.health <= 0:
			self.is_kill = True
			
	def get_inputs(self):
		# Get terrain inputs
		# Cast ray forward, and 45 degrees to each side, return list of collision distances
		self.terrain_distance = self.get_terrain_input(view_range = 200)
		# Get the distance to the predator if in range, or inf if not in range
		# and the angle to rotate to face the predator, or 0 if predator not in range
		# Also get the count of nearby agents within the view range
		self.agent_distance, self.agent_angle, self.nearby_agent_count, self.closest_agent = self.get_agent_input(view_range = 200)
	
	def get_agent_input(self,view_range = 200):
		nearby_agent_count = 0
		dist = view_range
		closest_agent = False
		for agent in self.environment.swarm.agents:
			new_dist = util.distance((self.x, self.y),(agent.x, agent.y))
			if new_dist < view_range:
				nearby_agent_count += 1
				if new_dist < dist:
					dist = new_dist
					closest_agent = agent
		if closest_agent:
			abs_angle = math.atan2(closest_agent.y - self.y, closest_agent.x - self.x)
			rel_angle = (math.pi + abs_angle - self.dir) % (2*math.pi) - math.pi
			return dist, rel_angle, nearby_agent_count, closest_agent
		else:
			return float('inf'), 0, nearby_agent_count, closest_agent
		
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
		if(self.closest_agent):
			if(self.agent_distance < self.radius + self.closest_agent.radius):
				self.closest_agent.health = self.closest_agent.health - 1

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
				self.speed = 0

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
					
	def draw(self, color = (0,0,1,1)):
		# Draw the agent body circle
		pyglet.gl.glPointSize(self.radius*2)
		pyglet.gl.glColor4f(*color)
		pyglet.graphics.draw(1, pyglet.gl.GL_POINTS, ('v2f', (self.x, self.y) ) )
		
		# Draw the agent dirction mark, from center to edge
		pyglet.gl.glColor4f(0,0,0,1)
		pyglet.gl.glLineWidth(3)
		pyglet.graphics.draw(2, pyglet.gl.GL_LINES,  ('v2f', 
			(self.x, self.y, 
			self.x + self.radius * math.cos(self.dir), self.y + self.radius * math.sin(self.dir)) ) )
