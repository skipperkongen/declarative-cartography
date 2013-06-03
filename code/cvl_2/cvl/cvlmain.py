from constraints import cellbound, proximity, allornothing 
from algo.hittingset import HittingSetHeuristic
from query import Constraint
from templates import *

import imp

class CvlMain(object):
	"""docstring for CvlMain"""
	def __init__( self, conflict_resolver=HittingSetHeuristic, query ):
		super( CvlMain, self ).__init__()
		self.conflict_resolver = conflict_resolver( query )
		self.query = query
		self.constraints = _load_constraint_implementations( query )
	
	def _load_constraint_implementations(self):
		for constraint in query.subject_to:
			name = constraint[0]
			params = list(constraint[1:])
			mod = imp.load_source('constraints.'+name, 'constraints/'+name+'.py')
			impl = 
		
	
	def generate_sql(self):
		code = []
		code.append( INFO_COMMENT.format( **self.query ))
		code.append( BEGIN_TX )
		code.extend( self.setup() )
		code.extend( self.create_levels() )
		code.extend( self.finalize() )
		code.extend( self.cleanup() )
		code.append( COMMIT_TX )
		code.append( INSPECTION_HELPER.format( **self.query ))
		return "".join( code )
		
	def setup(self):
		"""TODO"""
		code = []
		sql = SET_UP.format( **self.query )
		code.append( sql )
		return code

	def create_levels(self):
		"""TODO"""
		code = []
		code.append( CREATE_LEVELS_HEADER )
		for current_z in reversed(range( self.query['zoomlevels'] )):
			code.extend( self.create_level_z( current_z ))
		
		return code
	
	def create_level_z(self, current_z ):
		code = []
		format_obj = dict( self.query.items() + [('current_z', current_z), ('conflict_resolution', "".join(self.hittingset.solver_sql()))] )
		code.append( CREATE_LEVEL_Z_HEADER.format( **format_obj ))
		code.append(COPY_DOWN.format( **format_obj ))
		
		for constraint in self.constraints:
			code.append("\n-- " + constraint.__class__.__name__ + "\n")
			code.append( CREATE_TEMP_TABLE_CONFLICTS )
			# set up
			code.extend(constraint.set_up(current_z))
			# insert conflicts into _conflicts
			format_obj['constraint_select'] = "".join(constraint.find_conflicts(current_z))
			code.append(INSERT_INTO_CONFLICTS.format(**format_obj))
			# delete records to resolve conflicts
			code.append(DELETE_FROM.format( **format_obj ))
			# clean up
			code.extend(constraint.clean_up( current_z ))
			code.append( CLEAN_UP_LEVEL )
		return code
		
	def cleanup(self):
		"""TODO"""
		code = []
		sql = CLEAN_UP.format(**self.query)
		code.append( sql )
		return code
	
	def finalize(self):
		if self.query['simplify']:
			return ["UPDATE {table} SET {geometry} = ST_Simplify({geometry}, ST_ResZ(_tile_level, 256)/2);".format(
			**self.query
			)]
		else:
			return []

if __name__ == '__main__':
	print 'try example1.py in the root directory'
		
		


		
		