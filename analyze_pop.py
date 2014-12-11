import json
from collections import Counter

from genetic_programming import lgp

# Load population data from a json file
with open('test10_data.json', 'r') as infile:
	pop_data = json.load(infile)
		
		
pop_data = sorted(pop_data, key=lambda dat: dat['_fit'], reverse=True)
	
# 's_lgp' 'a_lgp'

op_code_count = Counter()
for op_code in pop_data[0]['s_lgp']:
	op_code_count[op_code] += 1
	
print(op_code_count)

op_code_count = Counter()
for op_code in pop_data[0]['a_lgp']:
	op_code_count[op_code] += 1
	
print(op_code_count)