import random
import math

import swarm
import color_maps

def create_terrain(environment, count = 10, scale = 100):
	# Create random convex quadrilaterals
	for i in range(count):
		x_cm = random.uniform(0, environment.window.width)
		y_cm = random.uniform(0, environment.window.height)
		x1 = x_cm + random.uniform(scale*.25,scale)
		y1 = y_cm + random.uniform(scale*.25,scale)
		x2 = x_cm + random.uniform(-scale,-scale*.25)
		y2 = y_cm + random.uniform(scale*.25,scale)
		x3 = x_cm + random.uniform(-scale,-scale*.25)
		y3 = y_cm + random.uniform(-scale,-scale*.25)
		x4 = x_cm + random.uniform(scale*.25,scale)
		y4 = y_cm + random.uniform(-scale,-scale*.25)
		environment.terrain.add_block_by_points([(x1,y1), (x2,y2), (x3,y3), (x4,y4)])
	
def create_swarm(environment, count = 20, radius = 20, velocity_range = (0, 500)):
	for n in range(count):
		# Creates an agent at a random location and initial velocity, 
		# but not overlapping any terrain
		while True:
			x = random.uniform(0, environment.window.width)
			y = random.uniform(0, environment.window.height)
			if environment.terrain.distance_to_nearest((x, y)) > radius:
				break
		direction = random.uniform(0, math.pi*2)
		speed = random.uniform(*velocity_range)
		environment.swarm.add_new_agent(radius = radius, position = (x, y), speed = speed, direction = direction)