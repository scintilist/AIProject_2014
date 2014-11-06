import random
import math

import swarm
import util

def create_random_terrain(environment, count = 10, scale = 100):
	# Create random convex quadrilaterals
	for i in range(count):
		x_cm = random.uniform(0, environment.width)
		y_cm = random.uniform(0, environment.height)
		x1 = x_cm + random.uniform(scale*.25,scale)
		y1 = y_cm + random.uniform(scale*.25,scale)
		x2 = x_cm + random.uniform(-scale,-scale*.25)
		y2 = y_cm + random.uniform(scale*.25,scale)
		x3 = x_cm + random.uniform(-scale,-scale*.25)
		y3 = y_cm + random.uniform(-scale,-scale*.25)
		x4 = x_cm + random.uniform(scale*.25,scale)
		y4 = y_cm + random.uniform(-scale,-scale*.25)
		environment.terrain.add_block_by_points([(x1,y1), (x2,y2), (x3,y3), (x4,y4)])
	
def create_random_swarm(environment, count = 20, radius = 20):
	for n in range(count):
		# Creates an agent at a random location not overlapping any terrain or near the predator
		while True:
			x = random.uniform(0, environment.width)
			y = random.uniform(0, environment.height)
			if (environment.terrain.distance_to_nearest((x, y)) > radius and 
				util.distance((x, y), (environment.predator.x, environment.predator.y)) > 200):
				break
		environment.swarm.add_new_agent(radius = radius, position = (x, y), 
										speed = 0, direction = random.uniform(0, math.pi*2))
	
def create_terrain_test_agents(environment):
	environment.swarm.add_new_agent(radius = 20, position = (100, 200), speed = 10, direction = math.pi)
	
def create_test_terrain(environment):
	environment.terrain.add_block_by_points([(115,75), (75,115), (115,155), (155,115)])
	environment.terrain.add_block_by_points([(115,525), (75,485), (115,445), (155,485)])
	environment.terrain.add_block_by_points([(685,75), (725,115), (685,155), (645,115)])
	environment.terrain.add_block_by_points([(685,525), (725,485), (685,445), (645,485)])
	environment.terrain.add_block_by_points([(200,400), (200,340), (275,340), (275,400)])
	environment.terrain.add_block_by_points([(200,200), (200,260), (275,260), (275,200)])
	environment.terrain.add_block_by_points([(600,400), (600,340), (525,340), (525,400)])
	environment.terrain.add_block_by_points([(600,200), (600,260), (525,260), (525,200)])
	environment.terrain.add_block_by_points([(350,300), (400,450), (450,300), (400,150)])