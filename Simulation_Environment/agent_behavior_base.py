def behavior(input_data = [0,0,0,0,0,0,0,0,0]):
	# Inputs and outputs normalized to the range 0-1
		# Inputs
			# Length 9
			# terrain_distance[0:1], predator_distance, predator_angle, 
			# near_agent_dist, near_agent_angle, nearby_agent_count, health, random
		# Outputs
			# speed, ang_v
	# Greedy algorithm
		#heuristic places wieght on health and nearby agents and will pick whether to move or not based on this
	terr_dist = [0,0]
	terr_dist[0], terr_dist[1], pred_dist, pred_ang, agent_dist, agent_ang, support, health, rand = input_data	

	if pred_dist < 1: # Predator in view	
		if support > .3: # Attack
			if pred_dist > .2:
				speed = 1
			else:
				speed = pred_dist * 5
			if(.1 < pred_ang < .9):
				if(pred_ang > .5):
					ang_v = 1
				else:
					ang_v = 0
			else:
				ang_v = .5
		else: # Run away
			speed = 1
			if(.1 < pred_ang < .9):
				if(pred_ang > .5):
					ang_v = 0
				else:
					ang_v = 1
			else:
				ang_v = .5
	else: # Predator not in view
		speed = 1
		if terr_dist[0] == terr_dist[1]:
			ang_v = .5
		elif terr_dist[0] > terr_dist[1]:
			ang_v = 0
		else:
			ang_v = 1
	
	return [speed, ang_v] # List of length 2