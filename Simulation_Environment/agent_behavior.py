import random

class Agent_Behavior():

	def __init__(self, data):
		self.weight = []
		for output in range(2):
			self.weight.append([])
			for input in range(6):
				self.weight[output].append(random.uniform(-1,1))
	
	def run(self, input_data = [0,0,0,0,0,0]):
		# Inputs and outputs normalized to the range 0-1
		# Inputs
			# Length 6
			# terrain_distance[0:1], predator_distance, predator_angle, nearby_agent_count, health
		# Outputs
			# speed, ang_v
		output_data = [0, 0]
		
		for i, output in enumerate(output_data):
			for j,input in enumerate(input_data):
				output_data[i] += self.weight[i][j] * input
			# limit output to the range 0-1
			output_data[i] = max(min(output_data[i], 1), 0)
		
		return output_data # List of length 2