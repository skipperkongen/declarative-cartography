class Constraint(object):
	"""docstring for Constraint"""
	def __init__(self, name, query, set_up, find_conflicts, clean_up, *parameters):
		super(Constraint, self).__init__()
		self.name = name
		self.query = query
		self.set_up = set_up
		self.find_conflicts = find_conflicts
		self.clean_up = clean_up
		self.parameters = parameters
	
	def _get_format_obj(self, current_z):
		return dict(self.query.__dict__.items() + [('current_z', current_z)])

	def set_up(self, current_z):
		fmt_obj = _get_format_obj(current_z)
		return [SET_UP.format(**fmt_obj)]

	def find_conflicts(self, current_z):
		fmt_obj = _get_format_obj(current_z)
		return [FIND_CONFLICTS.format(**fmt_obj)]

	def clean_up(self, current_z):
		fmt_obj = _get_format_obj(current_z)
		return [CLEAN_UP.format(**fmt_obj)]