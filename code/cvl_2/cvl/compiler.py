from constraints import cellbound, proximity, allornothing 
from algo.hittingset import HittingSetHeuristic
from constraints import Constraint
from query import WILDCARD
from templates import *

import imp
import re
import sys, os
import pdb

class CvlCompiler(object):
	"""docstring for CvlMain"""
	def __init__( self, query, conflict_resolver=HittingSetHeuristic ):
		super( CvlCompiler, self ).__init__()
		self.conflict_resolver = conflict_resolver( query )
		self.query = query
		self.constraints = self._load_constraints()
	
	def _load_constraints(self):
		constraints = []
		constraints_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'constraints')
		
		for constraint in self.query.subject_to:
			name = constraint[0]
			params = list(constraint[1:])
			module_name = 'constraints.%s' % name
			module_file = '%s/%s.py' % (constraints_dir, name)
			#pdb.set_trace()
			mod = imp.load_source( module_name, module_file )
			
			constraints.append(
				Constraint(name, self.query, mod.SET_UP, mod.FIND_CONFLICTS, mod.CLEAN_UP, *params)
			)
			
		return constraints
		
	
	def generate_sql(self):
		code = []
		code.append( INFO_COMMENT.format( **self.query.__dict__ ))
		code.append( BEGIN_TX )
		# GENERALIZE, RANK BY and PARTITION BY
		code.extend( self.setup() )
		# SUBJECT TO, FORCE LEVEL, TRANSFORM BY
		code.extend( self.create_levels() )
		code.extend( self.finalize() )
		code.append( COMMIT_TX )
		code.append( INSPECTION_HELPER.format( **self.query.__dict__ ))
		return "".join( code )
		
	def setup(self):
		"""TODO"""
		Q = self.query
		code = []
		code.append( SET_UP.format( **self.query.__dict__ ) )
		code.append( HEADER_MERGE )
		# MERGE PARTITIONS
		# pass 1: find wildcard and collect partitions to be merged
		merged = []
		has_merge_wildcard = False
		add_quotes = re.compile(r'(.*)')
		for merge in filter(lambda x: x[0] is not WILDCARD, Q.merge_partitions):
			after_merge = merge[1]
			code.append( MERGE_PARTITIONS.format(
				output=Q.output, 
				before_merge=', '.join(
					map(lambda x: add_quotes.sub(r"'\1'", x), merge[0])
				), 
				after_merge=after_merge
			))
			merged.append(after_merge)
		for merge in filter(lambda x: x[0] is WILDCARD, Q.merge_partitions):
			code.append( MERGE_PARTITIONS_REST.format(
				output=Q.output,
				merged = ', '.join(
					map(lambda x: add_quotes.sub(r"'\1'", x), merged)
				),
				after_merge = merge[1]
			))
		return code

	def create_levels(self):
		"""TODO"""
		code = []
		code.append( CREATE_LEVELS_HEADER )
		for current_z in reversed(range( self.query.zoomlevels )):
			code.extend( self.create_level_z( current_z ))
		
		return code
	
	def create_level_z(self, current_z ):

		code = []
		format_obj = dict( 
			self.query.__dict__.items() + 
			[('current_z', current_z)] + 
			[('conflict_resolution', ''.join(self.conflict_resolver.solver_sql()))] + 
			[('ignored_partitions',  ', '.join(map(lambda x: ("'%s'" % x[0]), self.query.force_level)))]
		)
		format_obj['comment'] = '--' if format_obj['ignored_partitions'] == '' else ''

		# create _conflicts
		code.append( INIT_LEVEL.format(**format_obj) )
		
		# SUBJECT TO
		for constraint in self.constraints:
			code.append( HEADER_CONSTRAINT.format(constraint_name=constraint.name) )
			code.extend( constraint.set_up(current_z) )
			format_obj['constraint_select'] = constraint.find_conflicts(current_z)
			if format_obj['ignored_partitions'] == '':
				code.extend( INSERT_INTO_CONFLICTS.format(**format_obj) )
			else:
				code.extend( INSERT_INTO_CONFLICTS_IGNORED_PARTITIONS.format(**format_obj) )
			code.extend( constraint.clean_up( current_z ) )
		
		# FORCE LEVEL
		for force_delete in filter(lambda x: x[1] == current_z+1, self.query.force_level):
			format_obj['delete_partition'] = "'%s'" % force_delete[0]
			code.append( FORCE_DELETE.format(**format_obj) )

		# make level feasible by deleting records
		code.append( RESOLVE_CONFLICTS.format(**format_obj) )

		# TRANSFORM BY
		if 'allornothing' in self.query.transform_by:
			code.append( ALLORNOTHING.format(**format_obj) )
		if 'simplify_carry' in self.query.transform_by:
			code.append( SIMPLIFY_LEVEL.format(**format_obj) )
		
		# delete _conflicts			
		code.append( CLEAN_UP_LEVEL.format(**format_obj) )

		return code
			
	def finalize(self):
		code = []
		code.append( HEADER_FINALIZE.format(**self.query.__dict__) )
		if 'simplify_once' in self.query.transform_by:
			code.append( SIMPLIFY.format(**self.query.__dict__))
		code.append( FINALIZE.format(**self.query.__dict__) )
		return code

if __name__ == '__main__':
	print 'try example1.py in the root directory'
		
		


		
		