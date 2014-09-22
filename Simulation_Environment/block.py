import pyglet

import util

class Block():
	'''Blocks are stationary obstacles to the agents
	   Blocks are simple polygons defined as a list of vertices.'''
	   
	def __init__(self, vertices = [(0, 0), (0, 0)]):
		self.vertices = []
		self.num_vertices = len(vertices)
		for i in range(self.num_vertices): # Remove duplicate vertices
			if vertices[i] != vertices[(i+1)%self.num_vertices]:
				vertex = Vertex(vertices[i])
				vertex.block = self
				self.vertices.append(vertex)
		self.num_vertices = len(self.vertices)
		self.edges = []
		for i in range(self.num_vertices):
			edge = Edge((vertices[i], vertices[(i+1)%self.num_vertices]))
			edge.block = self
			self.edges.append(edge)
		# Get orientation
		self.get_orientation()
		# Get centroid
		area = 0
		cx = 0
		cy = 0
		for i, a in enumerate(vertices):
			b = vertices[(i+1)%self.num_vertices]
			area += a[0]*b[1]-b[0]*a[1]
			cx += (a[0]+b[0])*(a[0]*b[1]-b[0]*a[1])
			cy += (a[1]+b[1])*(a[0]*b[1]-b[0]*a[1])
		area /= 2
		cx /= 6*area
		cy /= 6*area
		self.centroid = (cx, cy)
		# Create vertex list for drawing
		tri_vertices = util.tri_poly(vertices)
		vertex_list = []
		for vertex in tri_vertices:
			vertex_list.extend(vertex)
		self.vertex_list = pyglet.graphics.vertex_list(len(tri_vertices), ('v2f', vertex_list))
		
	def draw(self, color = (0,0,0,1)):
		pyglet.gl.glColor4f(*color)
		self.vertex_list.draw(pyglet.gl.GL_TRIANGLES)
		
	def get_orientation(self):
		# Get polygon orientation
		twice_area = 0
		for edge in self.edges:
			twice_area += (edge[1][0] - edge[0][0]) * (edge[1][1] + edge[0][1])
		self.orientation = 1 if twice_area > 0 else -1
	
	def circle_intersect(self, r = 10, a = (0,0), b = (1,1)):
		# Returns False if no intersection between circle of radius r passing from 
		# a to b and the Block, or a tuple of the closest intersection to a and the surface normal
		intersections = []
		# Expand block by radius r and test for intersection with line ab
		for edge in self.edges:
			# Get edge perpendicular unit vectors
			edge_len = util.distance(edge[0], edge[1])
			uy = self.orientation * (edge[1][0] - edge[0][0]) / edge_len
			ux = -self.orientation * (edge[1][1] - edge[0][1]) / edge_len
			# Get perpendicular shift by r
			x_shift = ux * r
			y_shift = uy * r
			# Get new edge endpoints
			a0 = (edge[0][0] + x_shift, edge[0][1] + y_shift)
			b0 = (edge[1][0] + x_shift, edge[1][1] + y_shift)
			# Test intersection
			location = util.intersect(a, b, a0, b0)
			if location:
				intersections.append((location, edge))
		for vertex in self.vertices:
			locations = util.line_circle_intersect(a, b, vertex, r)
			for location in locations:
				intersections.append((location, vertex))
		# If there are no intersections, return False
		if not intersections:
			return False
		# Find the intersection closest to point a
		dist = float('inf')
		for intersection in intersections:
			new_dist = util.distance(a, intersection[0])
			if new_dist < dist:
				dist = new_dist
				closest_intersection = intersection[0] # Location of closest intersection
				collided_element = intersection[1] # Vertex or edge that was intersected
		surface_normal = collided_element.surface_normal(closest_intersection)
		return (closest_intersection, surface_normal)
		
	def point_distance(self, p = (0,0)):
		# Returns the distance from the point to the polygon block, negetive if inside
		sign = 1
		if util.point_in_poly(p, self.vertices):
			sign = -1
		min_dist = float('Inf')
		# Calculate perpendicular distance from each edge segment to the point
		for edge in self.edges:
			min_dist = min(util.perpendicular_distance(edge[0], edge[1], p), min_dist)
		# Calculate distance from each vertex to the point
		for vertex in self.vertices:
			min_dist = min(util.distance(vertex, p), min_dist)
		return min_dist*sign
		
class Edge(tuple):
	def surface_normal(self, point):
		# Unit vector out perpendicular to edge
		edge_len = util.distance(self[0], self[1])
		uy = self.block.orientation * (self[1][0] - self[0][0]) / edge_len
		ux = -self.block.orientation * (self[1][1] - self[0][1]) / edge_len
		return ux,uy
	
class Vertex(tuple):
	def surface_normal(self, point):
		# Unit vector from vertex to point
		dist = util.distance(self, point)
		ux = (point[0] - self[0]) / dist
		uy = (point[1] - self[1]) / dist
		return ux,uy
