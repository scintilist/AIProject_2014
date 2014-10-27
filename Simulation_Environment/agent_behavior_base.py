import math

class Agent_Behavior_Base():

	def __init__(self, data):
		self.weight = [[0,0,-500,0,15,1000],[0,0,-500,0,15,1000]]
	
	def run(self, input_data = [0,0,0,0,0,0]):
		# Inputs and outputs normalized to the range 0-1
		# Inputs
			# Length 6
			# terrain_distance[0:1], predator_distance, predator_angle, nearby_agent_count, health
		# Outputs
			# speed, ang_v
		# Greedy algorithm
			#heuristic places wieght on health and nearby agents and will pick whether to move or not based on this
		output_data = [0, 0]
		total=0
		for i, input in enumerate(input_data):
			total += self.weight[0][i] * input_data[i]
			# limit output to the range 
		if total<=500:
			output_data[0]=10
			if(input_data[3]>2.5):
				self.ang_v = .5
			elif(input_data[3]<-2.5):
				self.ang_v = -.5
			else:
				self.ang_v = 0
			
		if total>500:
			output_data[0]=10*input_data[2]
			if(input_data[3]<.5):
				output_data[1] = -1
			elif(input_data[3]>-.5):
				output_data[1] = 1
			else:
				output_data[1] = 0
		
		return output_data # List of length 2