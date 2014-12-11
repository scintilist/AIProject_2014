"""
****virtual CPU register description and instruciton set****

**Register Description**
sr Boolean status register
acc floating point accumulator
idx integer index in range [0-8]
reg[0..8] Register data
inp[0..8] Input data

**Instructions**
Numeric
[0-8] | set idx = [0-8]

Input
ItoA | acc = inp[idx]

Register-Register
RtoA | acc = reg[idx]
AtoR | reg[idx] = acc
INC | acc = acc + 1
DEC | acc = acc - 1

Comparison
CMP | sr = acc > reg[idx]

Flow Control
PJMP | Jump Forward idx instructions if sr
NJMP | Jump Forward idx instruction if !sr

Math
ADD | acc = acc + reg[idx]
SUB | acc = acc - reg[idx]
MUL | acc = acc * reg[idx]
DIV | acc = acc / reg[idx]

**Execution**
Initialize with R[0-8] = I[0-8], F = 0, i = 0, S = 0
Run first code to completion
Normalize accumulator and take as first output
Persist Register state
Run second code to completion
Normalize accumulator and take as second output
"""


import random

# Contains Linear_Program, Virtual_CPU, and Behavior classes
# only the Behvaior class should be accessed externally

class Linear_Program():
	# Generates, and modifies a linear genetic program
	def __init__(self):
		# instructions and relative frequencies
		self.instr_set = [('num', 10), ('ItoA', 1), ('RtoA', 1), ('AtoR', 1), ('INC', 1), 
						  ('DEC', 1), ('CMP', 1), ('PJMP', 1), ('NJMP', 1), ('ADD', 1), 
						  ('SUB', 1), ('MUL', 1), ('DIV', 1)]
		self.prog = []
	
	def weighted_choice(self, choices):
		total = sum(w for c, w in choices)
		r = random.uniform(0, total)
		upto = 0
		for c, w in choices:
			if upto + w > r:
				return c
			upto += w
	
	def randomize(self, instr_count = 100):
		# Generate a random program with 100 instr_count instructions
		for i in range(instr_count):
			instr = self.weighted_choice(self.instr_set)
			if instr == 'num':
				instr = random.randint(0, 8)
			self.prog.append(instr)
			
	def crossover(self, parent = [None, None], c_prob = .01):
		# Parent is a Linear_Program object
		# Performes random multi-point crossover between parents
		# Every instruction has c_prob probability of being a crossover point
		self.prog = []
		par_sel = 0 # Current parent selection
		par_count = len(parent) # Number of parents
		instr_count = len(parent[0].prog) # Number of instructions
		for i in range(instr_count):
			if random.random() < c_prob: # Crossover point
				par_sel = (par_sel + 1) % par_count # Switch to the next parent
			self.prog.append(parent[par_sel].prog[i])
		
	def mutate(self, m_prob = .01):
		# Randomly mutates every instr with probability m_prob, following instr weighting
		for i, instr in enumerate(self.prog):
			if random.random() < m_prob:
				new_instr = self.weighted_choice(self.instr_set)
				if new_instr == 'num':
					new_instr = random.randint(0, 8)
				self.prog[i] = new_instr
	
	def print_prog(self):
		for instr in self.prog:
			print("{!s:>4}, ".format(instr), end="")
		print('')
		
		
class Behavior():
	# Configure behavior used in simulation loop
	def __init__(self):
		self.s_lgp = Linear_Program()
		self.a_lgp = Linear_Program()
		
	def randomize(self, instr_count = 100):
		self.s_lgp.randomize(instr_count)
		self.a_lgp.randomize(instr_count)
		
	def crossover(self, parent = [None, None], c_prob = .01):
		# Parents are Behavior objects
		self.s_lgp.crossover(parent = [ p.s_lgp for p in parent], c_prob = c_prob)
		self.a_lgp.crossover(parent = [ p.a_lgp for p in parent], c_prob = c_prob)
	
	def mutate(self, m_prob = .01):
		self.s_lgp.mutate(m_prob = m_prob)
		self.a_lgp.mutate(m_prob = m_prob)
	
	def behavior(self, input_data = [0,0,0,0,0,0,0,0,0]):
		# Inputs and outputs normalized to the range 0-1
			# Inputs
				# Length 9
				# terrain_distance[0:1], predator_distance, predator_angle, 
				# near_agent_dist, near_agent_angle, nearby_agent_count, health, random
			# Outputs
				# speed, ang_v
		v_cpu = Virtual_CPU()
		v_cpu.clear_state()
		v_cpu.set_input_data(input_data)
		v_cpu.set_reg_to_inp()
		
		output = []
		output.append(v_cpu.run(self.s_lgp.prog)) # Calculate the output speed
		output.append(v_cpu.run(self.a_lgp.prog)) # Calculate the output angular velcity
		return output
	
		
class Virtual_CPU():
	# Executes linear genetic programs
	def __inst__(self):
		self.clear_state()
		self.set_input_data()
		
	def clear_state(self): 
		# Clear the execution state
		self.sr = False # Status register
		self.acc = 0 # accumulator
		self.idx = 0 # index
		self.reg = [0 for i in range(9)] # registers
		self.pc = 0 # program counter
		
	def set_input_data(self, input_data = None):
		if input_data:
			self.inp = input_data
		else:
			self.inp = [0 for i in range(9)]
			
	def set_reg_to_inp(self):
		self.reg = self.inp[:]
		
	def run(self, prog):
		# Run the genetic program and return the resulting accumulator value, 
		# constrained to the range 0-1
		
		self.pc = 0 # program counter
		
		while self.pc < len(prog):
			instr = prog[self.pc]
			if type(instr) is str:
				getattr(self, instr)()
			else:
				self.idx = instr
			self.pc += 1
				
		return max(min(1, self.acc), 0)

	# All instructions
	def ItoA(self):
		self.acc = self.inp[self.idx]
	
	def RtoA(self):
		self.acc = self.reg[self.idx]
	
	def AtoR(self):
		self.reg[self.idx] = self.acc
	
	def INC(self):
		self.acc += 1
	
	def DEC(self):
		self.acc -= 1
	
	def CMP(self):
		self.sr = self.acc > self.reg[self.idx]
	
	def PJMP(self):
		if self.sr:
			self.pc += self.idx
	
	def NJMP(self):
		if not self.sr:
			self.pc += self.idx
	
	def ADD(self):
		self.acc += self.reg[self.idx]
		
	def SUB(self):
		self.acc -= self.reg[self.idx]
	
	def MUL(self):
		self.acc *= self.reg[self.idx]
	
	def DIV(self):
		if abs(self.reg[self.idx]) < .1:
			if self.reg[self.idx] >= 0:
				self.acc /= .1
			else:
				self.acc /= -.1
		else:
			self.acc /= self.reg[self.idx]
			
			
# Test functions
def test_randomization():	
	print('\n****Randomization Test****')
	lgp = Linear_Program()
	lgp.randomize(100)
	lgp.print_prog()
	
	cpu = Virtual_CPU()
	for i in range(100):
		cpu.clear_state()
		cpu.set_input_data([random.random() for i in range(9)])
		cpu.set_reg_to_inp()
		output = cpu.run(lgp.prog)
		print(output)

def test_instruction_set():
	print('\n****Instruction Set Test****')
	cpu = Virtual_CPU()
	cpu.clear_state()
	cpu.set_input_data([i for i in range(9)])
	prog = [5, 'ItoA', 0, 'AtoR',
			8, 'ItoA', 1, 'AtoR',
			3, 'ItoA', 2, 'AtoR',
			0, 'RtoA', 1, 'ADD',
			'CMP', 1, 'PJMP', 0, 
			'ADD', 'ADD', 'ADD',
			'INC', 'DEC',3,'AtoR',
			'DEC', 'CMP','DIV','MUL','SUB']
	cpu.run(prog)
	print(prog)
	print(cpu.reg)
	print(cpu.acc)
	print(cpu.sr)

def test_crossover():
	print('\n****Crossover Test****')
	lgp_p1 = Linear_Program()
	lgp_p1.randomize(10)
	lgp_p1.print_prog()
	
	lgp_p2 = Linear_Program()
	lgp_p2.randomize(10)
	lgp_p2.print_prog()
	
	lgp_c = Linear_Program()
	lgp_c.crossover(parent = [lgp_p1, lgp_p2], c_prob = .2)
	lgp_c.print_prog()

def test_mutation():
	print('\n****Mutation Test****')
	lgp = Linear_Program()
	lgp.randomize(15)
	lgp.print_prog()
	
	lgp.mutate(m_prob = .2)
	lgp.print_prog()
	
def test_behavior():
	new_behavior = Behavior()
	new_behavior.randomize(100)
	output = new_behavior.behavior([random.random() for i in range(9)])
	print(output)

if __name__ == "__main__":
	test_randomization()
	test_instruction_set()
	test_crossover()
	test_mutation()
	test_behavior()
	