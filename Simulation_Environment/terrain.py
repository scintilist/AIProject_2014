import block
import raster

import util

class Terrain():
	'''Contains all blocks'''
	def __init__(self, environment, grid_size):
		self.grid_size = grid_size
		self.environment = environment
		self.hash_map = {}
		self.blocks = []
		
	def add_block_by_points(self, point_list):
		new_block = block.Block(point_list)
		self.blocks.append(new_block)
		# Put the block into all hash map locaitons it covers
		bins = raster.poly_bins(point_list, self.grid_size)
		self.put_in_map(bins, new_block)
		return new_block
		
	def add_block(self, new_block):
		self.blocks.append(new_block)
		# Put the block into all hash map locaitons it covers
		bins = raster.poly_bins(new_block.vertices, self.grid_size)
		self.put_in_map(bins, new_block)
		return new_block
		
	def remove_block(self, block):
		bins = raster.poly_bins(block.vertices, self.grid_size)
		self.remove_from_map(bins, block)
		self.blocks.remove(block)
	
	def draw(self):
		# draw all blocks in the terrain
		for block in self.blocks:
			block.draw()
			
	def distance_to_nearest(self, location = (0,0)):
		# returns distance from the location to the nearest block
		dist = float('inf')
		for block in self.blocks:
			dist = min(block.point_distance(location), dist)
		return dist
		
	def put_in_map(self, bins, block):
		# Put block in bins
		for bin in bins:
			if bin not in self.hash_map:
				self.hash_map[bin] = set()
			self.hash_map[bin].add(block)
			
	def remove_from_map(self, bins, block):
		# Remove block from bins
		for bin in bins:
			if bin in self.hash_map:
				self.hash_map[bin].discard(block)
				if not self.hash_map[bin]: # Remove dict entry if set is empty
					del self.hash_map[bin]
					
	def check_for_blocks(self, bins):
		# Return the set of blocks contained in the set of bins
		blocks = set()
		for bin in bins:
			if bin in self.hash_map:
				blocks |= self.hash_map[bin]
		return blocks
		
	def reindex(self):
		self.hash_map = {}
		# Places all blocks into appropriate bins
		for block in self.blocks:
			# Put the block into all hash map locaitons it covers
			bins = raster.poly_bins(block.vertices, self.grid_size)
			self.put_in_map(bins, block)
	
	def line_of_sight(self, a = (0, 0), b = (0,0)):
		# Returns true if line of sight between a and b is clear, false if obstructed by terrain
		bins = raster.line_bins(a, b, bin_size = self.grid_size)
		block_set = self.check_for_blocks(bins)
		for block in block_set:
			for edge in block.edges:
				if util.intersect(a, b, edge[0], edge[1]):
					return False
		return True
		
		