class BoundingBox(object):
	"""docstring for BoundingBox"""
	def __init__(self, minx=0, miny=0, maxx=0, maxy=0):
		super(BoundingBox, self).__init__()
		self.minx = minx
		self.miny = miny
		self.maxx = maxx
		self.maxy = maxy
	
	def __str__(self):
		return "{'minx':%f, 'miny':%f, 'maxx':%f, 'maxy':%f}" % (self.minx, self.miny,self.maxx,self.maxy)
	
	def __repr__(self):
		return self.__str__()	