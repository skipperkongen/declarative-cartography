import cPickle

class Serializer():
	
	def serialize(self, data, filename):
		with open( filename, 'w' ) as f:
			cPickle.dump( data, f )
	
	def deserialize(self, filename):
		with open( filename, 'r' ) as f:
			return cPickle.load( f )
