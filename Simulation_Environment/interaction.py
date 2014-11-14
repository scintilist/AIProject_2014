import random
import time

import pyglet
from pyglet.window import key

from . import util
from . import block
from . import agent

class Action():
	def __init__(self, environment, window, active_actions):
		self.active_actions = active_actions
		self.environment = environment
		self.window = window
		active_actions.active.append(self)
		
	def start_new_action(self):
		self.window.pop_handlers()
		# Push self to the undo stack and create new instance
		self.active_actions.undo.append(self)
		self.active_actions.active.remove(self)
		self.__class__(self.environment, self.window, self.active_actions)
		
	def exit(self):
		self.active_actions.active.remove(self)
		self.window.pop_handlers()
		
	def draw(self):
		pass
		
	def update(self):
		pass


class DeleteObject(Action):
	def __init__(self, environment, window, active_actions):
		super().__init__(environment, window, active_actions)
		self.mouse_over_object = False
		self.get_mouse_over_object(self.environment.mouse_x, self.environment.mouse_y)
		
		self.window.push_handlers(self.on_mouse_press, self.on_key_press)
		
	def undo(self):
		if isinstance(self.mouse_over_object, agent.Agent):
			self.environment.swarm.add_agent(self.mouse_over_object)
		elif isinstance(self.mouse_over_object, block.Block):
			self.environment.terrain.add_block(self.mouse_over_object)
		self.environment.redo.append(self)
		
	def redo(self):
		if isinstance(self.mouse_over_object, agent.Agent):
			self.environment.swarm.remove_agent(self.mouse_over_object)
		elif isinstance(self.mouse_over_object, block.Block):
			self.environment.terrain.remove_block(self.mouse_over_object)
		self.environment.undo.append(self)
		
	def draw(self):
		self.get_mouse_over_object(self.environment.mouse_x, self.environment.mouse_y)
		if self.mouse_over_object:
			self.mouse_over_object.draw(color = (.5,.5,.5,.8))

	def get_mouse_over_object(self, x, y):
		self.mouse_over_object = False
		dist = float('inf')
		# Check blocks
		blocks = self.environment.terrain.check_for_blocks(
			[(x//self.environment.terrain.grid_size, y//self.environment.terrain.grid_size)])
		for block in blocks:
			if util.point_in_poly((x, y), block.vertices):
				new_dist = util.distance(block.centroid,(x,y))
				if new_dist < dist:
					dist = new_dist
					self.mouse_over_object = block
		# Check agents
		agents = self.environment.swarm.check_for_agents(
			[(x//self.environment.terrain.grid_size, y//self.environment.terrain.grid_size)])
		for agent in agents:
			new_dist = util.distance((x,y), (agent.x, agent.y))
			if new_dist < agent.radius and new_dist < dist:
				dist = new_dist
				self.mouse_over_object = agent
	
	def on_mouse_press(self, x, y, button, modifiers):
		if self.mouse_over_object:
			if isinstance(self.mouse_over_object, agent.Agent):
				self.environment.swarm.remove_agent(self.mouse_over_object)
			elif isinstance(self.mouse_over_object, block.Block):
				self.environment.terrain.remove_block(self.mouse_over_object)
			self.start_new_action()
			return True
	
	def on_key_press(self, symbol, modifiers):
		# Return true if key handled, False if not
		if symbol == key.DELETE or symbol == key.BACKSPACE:
			return True
		return False
	

class PlaceAgent(Action):
	def __init__(self, environment, window, active_actions):
		super().__init__(environment, window, active_actions)
		self.radius = 20
		self.window.push_handlers(self.on_mouse_release, self.on_key_press)
		
	def undo(self):
		self.environment.swarm.remove_agent(self.agent)
		self.environment.redo.append(self)
	
	def redo(self):
		self.agent = self.environment.swarm.add_new_agent(radius = self.radius, position = self.position, 
			speed = 0, direction = 0)
		self.environment.undo.append(self)
	
	def on_mouse_release(self, x, y, button, modifiers):
		self.position = (x,y)
		self.agent = self.environment.swarm.add_new_agent(radius = self.radius, position = self.position, 
			speed = 0, direction = 0)
		self.start_new_action()
		return True
		
	def on_key_press(self, symbol, modifiers):
		# Return true if key handled, False if not
		if symbol == key.A:
			return True
		return False
		
		
class DrawPolygon(Action):
	def __init__(self, environment, window, active_actions):
		super().__init__(environment, window, active_actions)
		self.poly = [] # List of polygon coordinates
		self.vertices = []
		self.close_distance = 20 # Radius around the start point to detect the end of the polygon
		self.blocks = []
		
		self.window.push_handlers(self.on_mouse_press, self.on_key_press)
		
	def undo(self):
		for block in self.blocks:
			self.environment.terrain.remove_block(block)
		self.active_actions.redo.append(self)
	
	def redo(self):
		for block in self.blocks:
			self.environment.terrain.add_block(block)
		self.active_actions.undo.append(self)
		
	def draw(self):
		if self.poly:
			pyglet.gl.glColor3f(.9,.1,.1)
			pyglet.gl.glLineWidth(4)
			pyglet.graphics.draw(len(self.poly), pyglet.gl.GL_LINE_STRIP,('v2f', self.vertices ))
			
			pyglet.gl.glPointSize(self.close_distance)
			pyglet.graphics.draw(1, pyglet.gl.GL_POINTS,('v2f', self.vertices[0:2] ) )
			
	def on_mouse_press(self, x, y, button, modifiers):
		if len(util.remove_duplicate_vertices(self.poly)) >= 3:
			# if click was on the start of the polygon
			if util.distance((x,y), self.poly[0]) < 20:
				# Close and add polygon
				poly_list = util.poly_split(self.poly)
				for poly in poly_list:
					self.blocks.append(self.environment.terrain.add_block_by_points(poly))
				self.poly = []
				self.vertices = []
				self.start_new_action()
				return True
		self.poly.append((x,y))
		self.vertices.extend([x,y])
		return True
		
	def on_key_press(self, symbol, modifiers):
		# Return true if key handled, False if not
		if symbol == key.Z and modifiers & key.MOD_CTRL and self.poly:
			del self.poly[-1]
			del self.vertices[-2:]
			return True
		elif symbol == key.D:
			return True
		return False