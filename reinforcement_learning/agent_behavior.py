from simulation_environment import create
from simulation_environment import environment
import agent_behavior
import random

class Behavior():

	def __init__(self):
		self.alpha=.9;
		self.epsilon=.1;
		self.gamma=1;
		# the number of Actions:
		self.actions=9; 
		
		# the number of states;
		self.states=256;
		self.initial=True;
		
		self.prev=[[0 for x in range(2)] for x in range(10)];
		self.Q=[[0 for x in range(self.actions)] for x in range(self.states)];
		self.ntaken = [[0 for x in range(self.actions)] for x in range(self.states)];
		self.reward=0;		
		
	def behavior(self,input_data = [0,0,0,0,0,0,0,0,0],id=0):
		terr_dist = [0,0];
		self.reward=0;
		terr_dist[0], terr_dist[1], pred_dist, pred_ang, agent_dist, agent_ang, support, health, rand = input_data;
		self.state=0;
		
		if agent_dist < .1 and agent_dist > 0:
			self.state=self.state+128;
		if support > .2 and support < .5:
			self.state=self.state+64;
		if pred_dist < .1 and pred_dist > 0:
			self.state=self.state+32;
		if health >.5:
			self.state=self.state+16;
		if pred_ang <.5:
			self.state=self.state+8;
		if agent_ang>.5:
			self.state=self.state+4;
		if terr_dist[0]>.5:
			self.state=self.state+2;
		if terr_dist[0]>.5:
			self.state=self.state+1;
		#pick a state
		self.action = self.Q[self.state][:].index(max(self.Q[self.state][:]))
		
		if rand<self.epsilon:
			self.action=random.randint(0,self.actions-1);
		
		if self.initial==False:
			self.prev_state=self.prev[id][0];
			self.prev_action=self.prev[id][1];
			rew=self.give_reward(self.state,self.prev_state)
			self.reward = self.reward+rew;
			self.ntaken[self.prev_state][self.prev_action-1]=self.ntaken[self.prev_state][self.prev_action-1]+1
			#Q_qlearn(sti_qlearn,at_qlearn) = Q_qlearn(sti_qlearn,at_qlearn) + alpha*( rew_qlearn + gamma*max(Q_qlearn(stp1i_qlearn,:)) - Q_qlearn(sti_qlearn,at_qlearn) );
			self.Q[self.prev_state][self.prev_action-1]=self.Q[self.prev_state][self.prev_action-1]+self.alpha*(self.reward+self.gamma*max(self.Q[self.state][:])-self.Q[self.prev_state][self.prev_action-1]);
			
		self.prev[id][0]=self.state;
		self.prev[id][1]=self.action;
		
		speed=1;
		angle=0;
		
		if self.action==9:
			speed=1;
			angle=0;
		if self.action==8:
			speed=.5;
			angle=0;
		if self.action==7:
			speed=0;
			angle=0;
		if self.action==6:
			speed=1;
			angle=agent_ang;
		if self.action==5:
			speed=.5;
			angle=agent_ang;
		if self.action==4:
			speed=0;
			angle=agent_ang;
		if self.action==3:
			speed=1;
			angle=pred_ang;
		if self.action==2:
			speed=.5;
			angle=pred_ang;
		if self.action==1:
			speed=0;
			angle=pred_ang;
		if id==9:
			self.initial=False;
		return [speed, angle]	
		
	def give_reward(self,current_state,prev_state):
		if current_state>=224 and prev_state>=224:
			rew=30;
		elif current_state>=192 and prev_state>=224:
			rew=10;
		elif current_state>=96 and prev_state>=224:
			rew=-50;
		elif current_state>=224 and prev_state>=192:
			rew=40;
		elif current_state>=192 and prev_state>=192:
			rew=20;
		elif current_state>=96 and prev_state>=192:
			rew=-40;
		elif current_state>=224 and prev_state>=96:
			rew=50;
		elif current_state>=192 and prev_state>=96:
			rew=30;
		elif current_state>=96 and prev_state>=96:
			rew=-10;
		else:
			rew=-50;
		return rew; 