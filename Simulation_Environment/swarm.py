import agent
import raster

class Swarm():
	def __init__(self, environment):
		# Empty list of agents in the swarm
		self.agents = []
		# Id number of the next agent to be created
		self.next_agent_id = 0
		
		self.environment = environment
		self.terrain = environment.terrain
		self.grid_size = self.terrain.grid_size
		self.hash_map = {}
		
	def add_new_agent(self, radius = 16, position = (0, 0), speed = 0, direction = 0):
		new_agent = agent.Agent(self, self.next_agent_id, radius, position, speed, direction)
		self.agents.append(new_agent)
		self.next_agent_id += 1
		bins = raster.circle_bins((new_agent.x, new_agent.y), new_agent.radius, self.grid_size)
		self.put_in_map(bins, agent)
		return new_agent
		
	def add_agent(self, new_agent):
		self.agents.append(new_agent)
		return new_agent
		
	def remove_agent(self, agent):
		bins = raster.circle_bins((agent.x, agent.y), agent.radius, self.grid_size)
		self.remove_from_map(bins, agent)
		self.agents.remove(agent)
		
	def draw(self):
		for agent in self.agents:
			agent.draw()
	
	def update(self):
		for agent in self.agents:
			agent.get_inputs()
			agent.attack()
		# BEHAVIOR CODE RUN HERE
	
		for agent in self.agents:
			agent.update()
			
		# Prune agents marked for removal
		for i, agent in enumerate(self.agents):
			if agent.kill:
				del self.agents[i]
				
		# Update hash map for all agents
		self.reindex()
				
	def put_in_map(self, bins, agent):
		# Put agent in bins
		for bin in bins:
			if bin not in self.hash_map:
				self.hash_map[bin] = set()
			self.hash_map[bin].add(agent)
			
	def remove_from_map(self, bins, agent):
		# Remove agent from bins
		for bin in bins:
			if bin in self.hash_map:
				self.hash_map[bin].discard(agent)
				if not self.hash_map[bin]: # Remove dict entry if set is empty
					del self.hash_map[bin]
					
	def check_for_agents(self, bins):
		# Return the set of blocks contained in the set of bins
		agents = set()
		for bin in bins:
			if bin in self.hash_map:
				agents |= self.hash_map[bin]
		return agents
		
	def reindex(self):
		self.hash_map = {}
		# Places all agents into appropriate bins
		for agent in self.agents:
			# Put the agent into all hash map locations it covers
			bins = raster.circle_bins((agent.x, agent.y), agent.radius, self.grid_size)
			self.put_in_map(bins, agent)