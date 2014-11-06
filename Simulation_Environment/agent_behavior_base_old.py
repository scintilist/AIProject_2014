import math

class Agent_Behavior_Base():

	def __init__(self):
		self.weight = [[0,0,-500,0,15,1000],[0,0,-500,0,15,1000]]
	
	def run(self, input_data = [0,0,0,0,0,0,0,0,0]):
		# Inputs and outputs normalized to the range 0-1
		# Inputs
			# Length 9
			# terrain_distance[0:1], predator_distance, predator_angle, near_agent_dist, near_agent_angle, nearby_agent_count, health, random
		# Outputs
			# speed, ang_v
		# Greedy algorithm
			#heuristic places wieght on health and nearby agents and will pick whether to move or not based on this
		output_data = [0, 0]
		total=0
		self.pred_dist=input_data[2]
		self.pred_ang=input_data[3]
		for i, input in enumerate(input_data):
			total += self.weight[0][i] * input_data[i]
			# limit output to the range 
			
		print(total)
		if total<=500:
			self.speed=1
			if(self.pred_ang>2.5):
				self.angle = .5
			elif(self.pred_ang<-2.5):
				self.angle = -.5
			else:
				self.angle = 0
		else:
			self.speed=self.pred_dist
			if(self.pred_ang<.5):
				self.angle = -1
			elif(self.pred_ang>-.5):
				self.angle = 1
			else:
				self.angle = 0
		
		output_data[0]=self.speed
		output_data[1]=self.angle
		return output_data # List of length 2