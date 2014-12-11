from multiprocessing import Process, Queue
import time
import json
import sys
import os
import shutil
import getopt

from genetic_programming import lgp_trial
from genetic_programming import simulation

NUMBER_OF_PROCESSES = 4

def main(argv):
	# Get configuration from json file
	config_fn = None
	try:
		opts, args = getopt.getopt(argv,"i:")
	except getopt.GetoptError:
		print('gen_prog.py -i <configfile.json>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('gen_prog.py -i <configfile.json>')
		elif opt == '-i':
			config_fn = arg
	
	# File can contain a single config as a dict, or multiple in a list
	with open(config_fn, 'r') as infile:
		json_data = json.load(infile)

	configs = [] # list of all configs
	if type(json_data) is dict:
		configs.append(json_data)
	else:
		configs = json_data	

	configs = json_data	
	
	# Create worker processes for simulation
	
	# Job input queue format is:
	# (index, individual, sim_time_step, sim_time_out)
	task_queue = Queue()
	
	# Job output queue format is:
	# (index, fitness, survivor_count)
	done_queue = Queue()

    # Start worker processes
	for i in range(NUMBER_OF_PROCESSES):
		Process(target=simulation.simulator, args=(task_queue, done_queue)).start()
	
	# Create folder for results
	time_str = time.strftime("%Y-%m-%dT%H.%M.%S")
	result_path = 'gp_results/{:}'.format(time_str)
	os.makedirs(result_path)
	
	# Copy config into results folder
	shutil.copyfile(config_fn, '{:}/{:}'.format(result_path, config_fn))
	
	# Run all configurations found 
	for i, config in enumerate(configs):
		print('\n**** Config {:d} ****'.format(i))
		lgp_trial.run(task_queue, done_queue, result_path, **config)

	# Tell worker processes to stop
	for i in range(NUMBER_OF_PROCESSES):
		task_queue.put('STOP')	
	
if __name__ == "__main__":
	main(sys.argv[1:])