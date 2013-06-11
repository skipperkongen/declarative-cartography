import pdb

class Colors(object):
	"""docstring for Colors"""
	def __init__(self, step=16):
		super(Colors, self).__init__()
		self.step = step
		self.colors = []
		self.compute_colors()
	
	def compute_colors(self):
		for red in range(0, 256, self.step):
			for green in range(0, 256, self.step):
				for blue in range(0, 256, self.step):
					colr = "#%02x%02x%02x" % (red, green, blue)
					self.colors.append(colr)
	
	def __getitem__(self, index):
		return self.colors[index]
	
	def __len__(self):
		return len(self.colors)

if __name__ == '__main__':
	colors = Colors()
	print 'num colors',len(colors)
