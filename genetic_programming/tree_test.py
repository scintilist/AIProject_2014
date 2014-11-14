class Tree():
	def __init__(self, data = None, terminal = False):
		self.terminal = terminal # If True, the data will be a constant value, or a reference to an input value
								 # If False, the data will be a reference to an operator
		self.data = data # Value of the node
		self.children = [] # References to children
	
	def add_child(self, child):
		if not self.terminal: # terminal nodes cannot have children
			self.children.append(child)
			
		
root = Tree()
root.data = 1
root.add_child(Tree(2))
root.add_child(Tree(3))

root.children[1].add_child(Tree(4))
root.children[1].add_child(Tree(5))
root.children[1].add_child(Tree(6))




# walk the tree starting at 'root' and print all of the children
def walk(node):
	print(node.data)
	for child in node.children:
		walk(child)
	
	

	
walk(root)


"""
-Node contains a flag marking it as a terminal type
-Node contains value of depth from the root node, can be used to prevent adding children after some max depth

-Flag for terminal node idicates if data is a constant of a reference to an input



"""