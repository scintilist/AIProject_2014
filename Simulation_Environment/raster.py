import pyglet


# Returns the set of bins containing the circle of radius r at location a
def circle_bins(p = (0,0), r = 10, bin_size = 20):
	filled_bins = set()
	r_exp = 1.01*r/bin_size # Create a margin around the circle to prevent floating point errors
	x_center = p[0]/bin_size
	y_center = p[1]/bin_size	
	for x_bin in range(int(x_center-r_exp), int(x_center+r_exp)+1):
		for y_bin in range(int(y_center-r_exp), int(y_center+r_exp)+1):
			filled_bins.add((x_bin, y_bin))
	return filled_bins

# Returns the set of bins passed through by circle traveling from a to b
# Only complete if bin_size > circle diameter
def circle_path_bins(a = (0,0), b = (0,0), r = 10, bin_size = 20):
	filled_bins = set()
	r_exp = 1.01*r/bin_size # Create a margin around the circle to prevent floating point errors
	for p in a,b:
		x_center = p[0]/bin_size
		y_center = p[1]/bin_size	
		for x_bin in range(int(x_center-r_exp), int(x_center+r_exp)+1):
			for y_bin in range(int(y_center-r_exp), int(y_center+r_exp)+1):
				filled_bins.add((x_bin, y_bin))
	# If the move was larger than a bin, add bins along the 4 corner lines between the positions
	if abs(a[0] - b[0]) > bin_size or abs(a[1] - b[1]) > bin_size:
		for x_sign in range(-1,3,2):
			x_off = x_sign*1.1*r
			for y_sign in range(-1,3,2):
				y_off = y_sign*1.1*r
				filled_bins |= line_bins((a[0]+x_off, a[1]+y_off), (b[0]+x_off, b[1]+y_off), bin_size)
	return filled_bins
	
# Returns the set off all bins that contain part of the polygon p
def poly_bins(p = [(0,0),(0,0),(0,0)], bin_size = 20):
	filled_bins = set()
	# Get edge bins
	for i in range(len(p)):
		filled_bins |= line_bins(p[i], p[(i+1)%len(p)], bin_size)
	# Get interior bins
	poly_x, poly_y = zip(*p) # Unzip x and y 
	bin_x = tuple(x/bin_size for x in poly_x)
	bin_y = tuple(y/bin_size for y in poly_y)
	max_y_bin = int(max(bin_y))
	min_y_bin = int(min(bin_y))
	# Scan through the rows of bins
	for y_bin in range(min_y_bin, max_y_bin):
		node_x = []
		j = len(p) - 1
		# Build a list of nodes
		for i in range(len(p)):
			if (bin_y[i] < y_bin and bin_y[j] >= y_bin
			or bin_y[j] < y_bin and bin_y[i] >= y_bin): # If the branch crosses the y_bin scan line
				node_x.append(int(bin_x[i] + # Add the x coordinate of the crossing
					(y_bin-bin_y[i])/(bin_y[j]-bin_y[i])*(bin_x[j]-bin_x[i])))
			j = i
		node_x.sort()
		# Fill the bins between node pairs
		for i in range(0, len(node_x), 2):
			for j in range(node_x[i]+1, node_x[i+1]):
				filled_bins.add((j, y_bin))
	if not filled_bins: # if the polygon is contained in a single bin, add it
		filled_bins.add((int(bin_x[0]), int(bin_y[0])))
	return filled_bins
	
# Returns the set of all bins that contain part of the line ab
def line_bins(a = (0,0), b = (0,0), bin_size = 20):
	filled_bins = set()
	x1,y1 = a
	x2,y2 = b
	if x1 != x2:
		min_y_bin = min(y1, y2)//bin_size
		max_y_bin = max(y1, y2)//bin_size
		a = (y2 - y1) / (x2 - x1)
		b = (y1 - x1 * a) / bin_size
		dir = 1 if x2 > x1 else -1
		off = 1 if x2 > x1 else 0
		for x_bin in range(int(x1//bin_size + off), int(x2//bin_size + off), dir):
			y_bin = int(a * x_bin + b)
			if y_bin + 1 >= min_y_bin and y_bin <= max_y_bin:
				filled_bins.add((x_bin, y_bin))
				filled_bins.add((x_bin - 1, y_bin))
	if y1 != y2:
		min_x_bin = min(x1, x2)//bin_size
		max_x_bin = max(x1, x2)//bin_size
		a = (x2 - x1) / (y2 - y1)
		b = (x1 - y1 * a) / bin_size
		dir = 1 if y2 > y1 else -1
		off = 1 if y2 > y1 else 0
		for y_bin in range(int(y1//bin_size + off), int(y2//bin_size + off), dir):
			x_bin = int(a * y_bin + b)
			if x_bin + 1 >= min_x_bin and x_bin <= max_x_bin:
				filled_bins.add((x_bin, y_bin))
				filled_bins.add((x_bin, y_bin - 1))
	return filled_bins
	
def draw_bins(bins, s, color = (.3,.3,.3), style = 'wire'):
	if len(color) == 3:
		color = color+ (.5,)
	pyglet.gl.glColor4f(*color)
	if style == 'filled':
		for bin in bins:
			x = bin[0]
			y = bin[1]
			pyglet.graphics.draw(4, pyglet.gl.GL_POLYGON, 
				('v2f', (x*s,y*s,(x+1)*s,y*s,(x+1)*s,(y+1)*s,x*s,(y+1)*s) ) )
	elif style == 'wire':
		vertices = []
		for bin in bins:
			x = bin[0]
			y = bin[1]
			vertices.extend([x*s,    y*s,   (x+1)*s, y*s,
							(x+1)*s, y*s,   (x+1)*s,(y+1)*s,
							(x+1)*s,(y+1)*s, x*s,   (y+1)*s,
							x*s,    (y+1)*s, x*s,    y*s])
		pyglet.gl.glLineWidth(4)
		pyglet.graphics.draw(8*len(bins), pyglet.gl.GL_LINES,('v2f', vertices ) )	
			
			
			
			
			