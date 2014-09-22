# A series of functions to map values to colors in the format (r,g,b) where the range is 0-1

def rainbow(value):
	hue = value % 360
	r = clamp(abs(hue-180)/60 - 1, 0, 1)
	g = clamp(-abs(hue-120)/60 + 2, 0, 1)
	b = clamp(-abs(hue-240)/60 + 2, 0, 1)
	return (r,g,b)
	
	
def clamp(n,n_min,n_max):
	return max(min(n,n_max),n_min)