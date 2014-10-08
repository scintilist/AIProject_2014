class ActiveActions():

	def __init__(self, environment):
		self.environment = environment
		self.active = [] # list of active objects
		self.undo = [] # stack of objects with undo methods to be called when ctrl-z is pressed
		self.redo = [] # stack of objects with redo methods to be called when ctrl-y is pressed
		
	def update(self):
		for object in self.active:
			object.update()
			
	def draw(self):
		for object in self.active:
			object.draw()
			
	def clear_state(self):
		for object in self.active:
			object.exit()