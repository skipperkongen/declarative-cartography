class Constraint(object):
	"""docstring for Constraint"""
	def __init__(self, name, query, set_up, find_conflicts, clean_up, *parameters):
		super(Constraint, self).__init__()
		self.name = name
		self.query = query
		self.SET_UP = set_up
		self.FIND_CONFLICTS = find_conflicts
		self.CLEAN_UP = clean_up
		self.parameters = dict([("parameter_%d" % (i+1), x) for i,x in enumerate(parameters)])
		
	def _get_format_obj(self, current_z):
		return dict(self.query.__dict__.items() + self.parameters.items() + [('current_z', current_z)])

	def set_up(self, current_z):
		fmt_obj = self._get_format_obj(current_z)
		return [self.SET_UP.format(**fmt_obj)]

	def find_conflicts(self, current_z):
		fmt_obj = self._get_format_obj(current_z)
		return self.FIND_CONFLICTS.format( **fmt_obj )

	def clean_up(self, current_z):
		fmt_obj = self._get_format_obj(current_z)
		return [self.CLEAN_UP.format(**fmt_obj)]