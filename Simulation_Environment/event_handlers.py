import time

import pyglet
from pyglet.window import key

import agent
import swarm
import block
import terrain
import interaction

class EventHandlers():
	def __init__(self, environment, window, active_actions):
		self.window = window
		self.environment = environment
		self.active_actions = active_actions
		
	# Keyboard events
	def on_key_press(self, symbol, modifiers):
		# Take Screenshot
		if symbol == key.F12:
			fname = 'capture_' + time.strftime("%Y-%m-%d_%H%M%S",time.localtime()) + '.png'
			pyglet.image.get_buffer_manager().get_color_buffer().save(fname)
		
		# Quit
		elif symbol == key.Q:
			pyglet.app.exit()
		
		# Undo
		elif symbol == key.Z and modifiers & key.MOD_CTRL:
			if self.active_actions.undo:
				self.active_actions.undo.pop().undo()
		
		# Redo	
		elif symbol == key.Y and modifiers & key.MOD_CTRL:
			if self.active_actions.redo:
				self.active_actions.redo.pop().redo()
		
		# Cancel current actions
		elif symbol == key.ESCAPE:
			self.active_actions.clear_state()
		
		# Togggle hash grid display
		elif symbol == key.H:
			self.environment.show_bins = not self.environment.show_bins
		
		# Increase hash table grid size
		elif symbol == key.EQUAL:
			self.environment.terrain.grid_size += 10
			self.environment.swarm.grid_size = self.environment.terrain.grid_size
			self.environment.terrain.reindex()
			self.environment.swarm.reindex()
		
		# Decrease hash table grid size
		elif symbol == key.MINUS:
			self.environment.terrain.grid_size -= 10
			self.environment.terrain.grid_size = max(10, self.environment.terrain.grid_size)
			self.environment.swarm.grid_size = self.environment.terrain.grid_size
			self.environment.terrain.reindex()
			self.environment.swarm.reindex()
		
		# Pause
		elif symbol == key.P:
			if self.environment.paused:
				self.environment.real_time_start += time.perf_counter() - self.pause_start_time
				self.environment.paused = False
			else:
				self.pause_start_time = time.perf_counter()
				self.environment.paused = True
		
		# Remove object
		elif symbol == key.DELETE or symbol == key.BACKSPACE:
			self.active_actions.clear_state()
			interaction.DeleteObject(self.environment, self.window, self.active_actions)
		
		# Draw block
		elif symbol == key.D:
			self.active_actions.clear_state()
			interaction.DrawPolygon(self.environment, self.window, self.active_actions)
		
		#  Place Agent
		elif symbol == key.A:
			self.active_actions.clear_state()
			interaction.PlaceAgent(self.environment, self.window, self.active_actions)
			
		return True
	
	# Mouse Events
	def on_mouse_press(self, x, y, button, modifiers):
		pass
				
	def on_mouse_release(self, x, y, button, modifiers):
		pass
				
	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		self.environment.mouse_x = x
		self.environment.mouse_y = y
			
	def on_mouse_motion(self, x, y, dx, dy):
		self.environment.mouse_x = x
		self.environment.mouse_y = y
		
	def on_mouse_leave(self, x, y):
		self.environment.mouse_x = x
		self.environment.mouse_y = y
			
	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
		# Change hash table grid size
		self.environment.terrain.grid_size += 10*scroll_y
		self.environment.terrain.grid_size = max(10, self.environment.terrain.grid_size)
		self.environment.swarm.grid_size = self.environment.terrain.grid_size
		self.environment.terrain.reindex()
		self.environment.swarm.reindex()