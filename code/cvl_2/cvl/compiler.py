from constraints import cellbound, proximity, allornothing 
import solvers
import templates
from constraints import Constraint
from query import Query,WILDCARD

import imp
import re
import sys, os
import pdb

class CvlToSqlCompiler(object):
	"""Compiler that turns CVL into a single transaction in SQL"""
	def __init__( self ):
		super( CvlToSqlCompiler, self ).__init__()
	
	def _load_constraints( self, query ):
		constraints = []
		constraints_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'constraints')
		
		for constraint in query.subject_to:
			name = constraint[0]
			params = list(constraint[1:])
			module_name = 'constraints.%s' % name
			module_file = '%s/%s.py' % (constraints_dir, name)
			#pdb.set_trace()
			mod = imp.load_source( module_name, module_file )
			constraints.append(
				Constraint(name, query, mod.SET_UP, mod.FIND_CONFLICTS, mod.CLEAN_UP, *params)
			)
		return constraints
	
	def compile( self, query, templates=templates.pgtemplates, optimizer=solvers.pgsolvers.HittingSetHeuristic ):
		# initialize empty SQL transaction tx
		constraints = self._load_constraints( query )
		tx = TransactionBuilder( query, templates, optimizer, *constraints )
		# preample
		tx.BeginTx()
		tx.AddInfo()
		tx.AddFramework()
		tx.InitializeOutput() 
		tx.MergePartitions() # MERGE PARTITIONS
		# main loop: bottom up
		for z in reversed(range( query.zoomlevels )):
			tx.BigComment( 'Creating zoom-level %d' % z )
			tx.CopyLevel( z+1, z )
			tx.InitializeLevel( z )
			tx.PreTransform( z ) # FORCE LEVEL
			tx.OptimizeLevel( z ) # SUBJECT TO
			tx.PostTransform( z ) # TRANSFORM: allornothing, simplify_carryforward
			tx.CleanLevel( z )
		# finalize
		tx.SimplifyOutput() # TRANSFORM: simplify_once
		tx.FinalizeOutput() # TRANSFORM
		tx.RemoveFramework()
		tx.CommitTx()
		tx.TryThis()
		return tx.get_sql()
							
class TransactionBuilder(object):
	"""docstring for Transaction"""
	def __init__( self, query, templates, optimizer, *constraints ):
		super(TransactionBuilder, self).__init__()
		self.Q = query
		self.F = query.__dict__
		self.T = templates
		self.O = optimizer()
		self.C = constraints
		self.tx = []

	def BeginTx( self ):
		self.tx.append( self.T.BEGIN_TX.format( **self.F ) )

	def CommitTx( self ):
		self.tx.append( self.T.COMMIT_TX.format( **self.F ) )
	
	def AddInfo( self ):
		self.tx.append( self.T.ADD_INFO.format( **self.F ) )
	
	def AddFramework( self ):
		self.Comment( 'Adding CVL tiling framework' )
		self.tx.append( self.T.ADD_FRAMEWORK.format( **self.F ))
	
	def RemoveFramework( self ):
		self.Comment( 'Removing CVL tiling framework' )
		self.tx.append( self.T.REMOVE_FRAMEWORK.format( **self.F ))

	def InitializeOutput( self ):
		self.Comment( 'Initializing output' )
		self.tx.append( self.T.INITIALIZE_OUTPUT.format( **self.F ))
			
	def MergePartitions( self ):
		self.Comment( 'Merging partitions' )
		_tx = []
		merged = []
		has_merge_wildcard = False
		add_quotes = re.compile(r'(.*)')
		for merge in filter(lambda x: x[0] is not WILDCARD, self.Q.merge_partitions):
			self.F['before_merge'] = ', '.join(map(lambda x: add_quotes.sub(r"'\1'", x), merge[0]))
			self.F['after_merge'] = merge[1]
			
			_tx.append( self.T.MERGE_PARTITIONS.format( **self.F ))

			merged.append( merge[1] )
		for merge in filter(lambda x: x[0] is WILDCARD, self.Q.merge_partitions):
			self.F['merged'] = ', '.join(map(lambda x: add_quotes.sub(r"'\1'", x), merged))
			self.F['after_merge'] = merge[1]

			_tx.append( self.T.MERGE_PARTITIONS_REST.format( **self.F ))
		
		self.tx.extend(_tx)
	
	def CopyLevel( self, from_z, to_z ):
		self.Comment( 'Copy data from level %d to level %d' % (from_z, to_z) )
		self.F['from_z'] = from_z
		self.F['to_z'] = to_z
		self.tx.append( self.T.COPY_LEVEL.format( **self.F ) )
	
	def InitializeLevel( self, z ):
		self.Comment( 'Initialization for level %d' % z )
		self.F['current_z'] = z
		self.tx.append( self.T.INITIALIZE_LEVEL.format( **self.F ) )

	def PreTransform(self, z ):
		# FORCE LEVEL
		for force_delete in filter(lambda x: x[1] == z+1, self.Q.force_level):
			self.Comment( 'Prepruning records' )
			self.F['delete_partition'] = "'%s'" % force_delete[0]
			self.tx.append( self.T.FORCE_DELETE.format( **self.F ) )
		
	def OptimizeLevel( self, z ):
		self.F['conflict_resolution'] = ''.join(self.O.get_solver( self.Q ))
		self.F['ignored_partitions'] = ', '.join(map(lambda x: ("'%s'" % x[0]), self.Q.force_level))
		self.F['comment'] = '--' if self.F['ignored_partitions'] == '' else ''
		
		# find conflicts
		for constraint in self.C:
			self.Comment( 'Finding conflicts' )
			self.tx.extend( constraint.set_up( z ) )
			self.F['constraint_select'] = constraint.find_conflicts( z )
			if self.F['ignored_partitions'] == '':
				self.tx.extend( self.T.INSERT_INTO_CONFLICTS.format( **self.F ) )
			else:
				self.tx.extend( self.T.INSERT_INTO_CONFLICTS_IGNORED_PARTITIONS.format( **self.F ) )
			self.tx.extend( constraint.clean_up( z ) )
		
		# resolve conflicts
		self.Comment( 'Resolve conflicts' )
		self.tx.append( self.T.RESOLVE_CONFLICTS.format( **self.F ) )

	def PostTransform( self, z ):
		if 'allornothing' in self.Q.transform_by:
			self.Comment( 'Apply all-or-nothing' )
			self.tx.append( self.T.POSTPRUNE_LEVEL.format( **self.F ) )
		if 'simplify_carryforward' in self.Q.transform_by:
			self.Comment( 'Simplifying level' )
			self.tx.append( self.T.SIMPLIFY_LEVEL.format( **self.F ) )
			
	def CleanLevel( self, z ):
		self.Comment( 'Clean-up for level %d' % z )
		self.tx.append( self.T.CLEAN_LEVEL.format( **self.F ) )

	def SimplifyOutput( self ):
		self.Comment( 'Simplifying output' )
		if 'simplify_once' in self.Q.transform_by:
			self.tx.append( self.T.SIMPLIFY_OUTPUT.format( **self.F ) )

	def FinalizeOutput( self ):
		self.Comment( 'Finalizing output ' )
		self.tx.append( self.T.FINALIZE_OUTPUT.format( **self.F ) )
	
	def TryThis( self ):
		self.Comment( 'Something you can try')
		self.tx.append( self.T.TRYTHIS.format( **self.F) )
	
	def Comment( self, comment ):
		self.tx.append( self.T.COMMENT.format(comment=comment) )
	
	def BigComment( self, comment ):
		self.tx.append( self.T.BIG_COMMENT.format(comment=comment) )
	
	def get_sql( self ):
		return "".join( self.tx )
		
if __name__ == '__main__':
	print 'try example1.py in the root directory'
		
		


		
		